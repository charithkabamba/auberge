from django.db import models
from django.contrib.auth import get_user_model
from django_extensions.db.models import TimeStampedModel
from users.models import User, Address
from products.models import Product
from decimal import Decimal

User = get_user_model()


class Order(TimeStampedModel):
    class StatusChoices(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        SHIPPED = "shipped", "Shipped"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"

    class PaymentStatusChoices(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        FAILED = "failed", "Failed"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    shipping_address = models.ForeignKey(
        Address, on_delete=models.PROTECT, related_name="shipping_orders"
    )
    billing_address = models.ForeignKey(
        Address,
        on_delete=models.PROTECT,
        related_name="billing_orders",
        null=True,
        blank=True,
    )
    order_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(
        max_length=20, choices=StatusChoices.choices, default=StatusChoices.PENDING
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatusChoices.choices,
        default=PaymentStatusChoices.PENDING,
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_charge = models.DecimalField(
        max_digits=10, decimal_places=2, default=50.00
    )
    payment_method = models.CharField(max_length=20, default="cash_on_delivery")
    notes = models.TextField(blank=True, null=True)
    payment_intent_id = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f"Order #{self.order_number}"

    @property
    def grand_total(self):
        return self.total_amount + self.delivery_charge

    @property
    def readable_payment_method(self):
        return self.payment_method.replace("_", " ").title()


class OrderItem(TimeStampedModel):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(
        max_digits=10, decimal_places=2
    )  # Price at time of order

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def subtotal(self):
        return Decimal(self.quantity) * self.price
