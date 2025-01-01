import traceback
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.urls import reverse
from django.utils import timezone
import random
from decimal import Decimal
import stripe
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from djstripe.models import APIKey
import json
import logging
from products.models import Product
from orders.models import Order, OrderItem
from users.models import Address

from core.mixins import StripeMixin

from .models import Cart, CartItem
from .serializers import CartSerializer

from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST


logger = logging.getLogger(__name__)


class CartListAPIView(ListAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        cart = Cart.objects.filter(user=self.request.user)
        if not cart.exists():
            # Create an empty cart if none exists
            cart = Cart.objects.create(user=self.request.user)
            return [cart]
        return cart


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    product_id = request.data.get("product_id")
    quantity = int(request.data.get("quantity", 1))

    if not product_id:
        return Response(
            {"error": "Product ID is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    product = get_object_or_404(Product, id=product_id)

    # Validate stock
    if quantity > product.stock:
        return Response(
            {"error": f"Only {product.stock} items available in stock"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Get or create cart for user
    cart, _ = Cart.objects.get_or_create(user=request.user)

    # Check if item already exists in cart
    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
        # Validate total quantity
        if cart_item.quantity + quantity > product.stock:
            return Response(
                {
                    "error": f"Cannot add {quantity} more items. Only {product.stock - cart_item.quantity} more available"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        cart_item.quantity += quantity
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            cart=cart, product=product, quantity=quantity
        )

    return Response(
        {"message": "Item added to cart", "cart_total": cart.total_items},
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def update_cart_item(request):
    item_id = request.data.get("item_id")
    quantity = int(request.data.get("quantity", 1))

    if not item_id:
        return Response(
            {"error": "Item ID is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        cart_item = CartItem.objects.select_related("product").get(
            id=item_id, cart__user=request.user
        )
    except CartItem.DoesNotExist:
        return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)

    # Validate stock
    if quantity > cart_item.product.stock:
        return Response(
            {"error": f"Only {cart_item.product.stock} items available in stock"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if quantity < 1:
        cart_item.delete()
        cart = Cart.objects.get(user=request.user)
        return Response(
            {
                "message": "Item removed from cart",
                "cart_total": cart.total_items,
                "cart_total_price": cart.total_price,
            }
        )

    cart_item.quantity = quantity
    cart_item.save()

    return Response(
        {
            "message": "Quantity updated",
            "item_subtotal": cart_item.subtotal,
            "cart_total": cart_item.cart.total_items,
            "cart_total_price": cart_item.cart.total_price,
        }
    )


class CheckoutView(LoginRequiredMixin, TemplateView, StripeMixin):
    template_name = "cart/checkout.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            # Setup Stripe and get publishable key
            stripe_context = self.get_stripe_context()
            context.update(stripe_context)

            cart = Cart.objects.prefetch_related("items__product").get(
                user=self.request.user
            )

            if cart.items.count() == 0:
                context["cart"] = None
                return context

            # Get user's addresses
            addresses = self.request.user.addresses.all()

            context.update(
                {
                    "cart": cart,
                    "cart_items": cart.items.all(),
                    "total_price": cart.total_price,
                    "total_items": cart.total_items,
                    "delivery_charge": 50,
                    "grand_total": cart.total_price + 50,
                    "addresses": addresses,
                }
            )
        except Cart.DoesNotExist:
            context["cart"] = None
        except APIKey.DoesNotExist:
            messages.error(self.request, "Stripe API keys not configured properly")
            context["cart"] = None

        return context

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("users:login")
        return super().get(request, *args, **kwargs)


def generate_order_number():
    """Generate a unique order number"""
    return get_random_string(length=10, allowed_chars="0123456789")


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def place_order(request):
    """Handle order placement"""
    try:
        cart = request.user.cart
        if not cart.items.exists():
            return Response(
                {
                    "error": "Your cart is empty!",
                    "redirect_url": reverse("cart:cart_detail"),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get selected addresses
        shipping_address_id = request.data.get("shipping_address")
        billing_address_id = request.data.get("billing_address")

        if not shipping_address_id:
            return Response(
                {
                    "error": "Please select a shipping address",
                    "redirect_url": reverse("cart:checkout"),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get addresses from database
        shipping_address = Address.objects.get(
            id=shipping_address_id, user=request.user
        )
        billing_address = shipping_address  # Default to shipping address

        # If billing address is different
        if billing_address_id and not request.data.get("same_as_shipping"):
            billing_address = Address.objects.get(
                id=billing_address_id, user=request.user
            )

        # Create order
        order = Order.objects.create(
            user=request.user,
            shipping_address=shipping_address,
            billing_address=billing_address,
            order_number=f"ORD-{timezone.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}",
            total_amount=cart.get_total(),
            delivery_charge=Decimal("50.00"),
            payment_method=request.data.get("payment_method", "cash_on_delivery"),
            notes=request.data.get("notes", ""),
        )

        # Create order items
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.selling_price,
            )

        # Clear cart
        cart.items.all().delete()

        messages.success(request, "Order placed successfully!")
        return Response(
            {
                "message": "Order placed successfully",
                "redirect_url": reverse(
                    "orders:success", kwargs={"order_number": order.order_number}
                ),
            }
        )
    except Address.DoesNotExist:
        return Response(
            {"error": "Invalid address selected"}, status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        traceback.print_exc()
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PaymentIntentView(View, StripeMixin):
    @method_decorator(require_POST)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        try:
            # Setup Stripe
            self.setup_stripe()

            data = json.loads(request.body)
            payment_method_id = data.get("payment_method_id")
            shipping_address_id = data.get("shipping_address")

            # Calculate amount
            cart = request.user.cart
            amount = int((cart.total_price + 50) * 100)  # Convert to cents

            # Create PaymentIntent
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency="bdt",
                payment_method=payment_method_id,
                confirmation_method="manual",
                confirm=True,
                return_url=request.build_absolute_uri(reverse("cart:confirm_payment")),
            )

            # Store shipping address in session for later use
            request.session["shipping_address_id"] = shipping_address_id

            if intent.status == "requires_action":
                return JsonResponse(
                    {
                        "requires_action": True,
                        "client_secret": intent.client_secret,
                        "payment_intent_id": intent.id,
                    }
                )
            elif intent.status == "succeeded":
                # Create order and clear cart
                order = self.create_order(request, intent.id)
                return JsonResponse(
                    {
                        "success": True,
                        "redirect_url": reverse(
                            "orders:success", args=[order.order_number]
                        ),
                    }
                )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    def create_order(self, request, payment_intent_id):
        shipping_address_id = request.session.get("shipping_address_id")
        shipping_address = Address.objects.get(id=shipping_address_id)

        cart = request.user.cart
        total_amount = cart.total_price
        delivery_charge = Decimal("50.00")

        order = Order.objects.create(
            user=request.user,
            shipping_address=shipping_address,
            billing_address=shipping_address,
            payment_method="stripe",
            payment_intent_id=payment_intent_id,
            total_amount=total_amount,
            delivery_charge=delivery_charge,
            status="processing",
            order_number=f"ORD-{timezone.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}",
        )

        # Create order items
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.selling_price,
            )

        # Clear cart
        cart.items.all().delete()

        # Clear session
        if "shipping_address_id" in request.session:
            del request.session["shipping_address_id"]

        return order


class PaymentConfirmView(View, StripeMixin):
    @method_decorator(require_POST)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        try:
            # Setup Stripe
            self.setup_stripe()

            data = json.loads(request.body)
            payment_intent_id = data.get("payment_intent_id")

            intent = stripe.PaymentIntent.retrieve(payment_intent_id)

            if intent.status == "succeeded":
                # Create order and clear cart
                order = PaymentIntentView.create_order(self, request, payment_intent_id)
                return JsonResponse(
                    {
                        "success": True,
                        "redirect_url": reverse(
                            "orders:success", args=[order.order_number]
                        ),
                    }
                )
            else:
                return JsonResponse({"error": "Payment failed"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
