from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.db.models import Sum, Count
from django.db.models.functions import ExtractMonth
from calendar import month_name
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.utils.text import slugify
from django.http import HttpResponse
from django.db.models.functions import TruncDate
from django.db.models import Count, Sum, F
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from io import BytesIO

from categories.models import Category
from core.models import CURRENCY_CHOICES
from orders.models import Order, OrderItem
from offers.models import Offer
from products.models import Product, ProductImage
from users.models import User
from core.models import SiteSettings


def is_admin(user):
    return user.is_authenticated and user.is_superuser


@login_required
def admin_dashboard(request):
    today = timezone.now().date()
    current_year = today.year

    # Get monthly revenue for current year
    monthly_revenue = (
        Order.objects.filter(created__year=current_year, status="completed")
        .annotate(month=ExtractMonth("created"))
        .values("month")
        .annotate(revenue=Sum("total_amount"))
        .order_by("month")
    )

    # Create revenue data for all months (including 0 for months with no revenue)
    revenue_by_month = [0] * 12
    for item in monthly_revenue:
        revenue_by_month[item["month"] - 1] = float(item["revenue"] or 0)

    # Get month names
    month_names = list(month_name)[1:]  # Skip empty string at index 0

    context = {
        "pending_orders": Order.objects.filter(status="pending").count(),
        "cancelled_orders": Order.objects.filter(status="cancelled").count(),
        "processing_orders": Order.objects.filter(status="processing").count(),
        "today_income": Order.objects.filter(
            created__date=today, status="completed"
        ).aggregate(Sum("total_amount"))["total_amount__sum"]
        or 0.00,
        "recent_orders": Order.objects.order_by("-created")[:10],
        "month_names": month_names,
        "monthly_revenue": revenue_by_month,
    }

    return render(request, "users/admin/index.html", context)


@login_required
def admin_orders(request):
    # Get filter parameters
    search_query = request.GET.get("search", "")
    status_filter = request.GET.get("status", "")

    # Base queryset
    orders = Order.objects.select_related(
        "user", "shipping_address", "billing_address"
    ).all()

    # Apply filters
    if search_query:
        orders = orders.filter(
            Q(order_number__icontains=search_query)
            | Q(user__email__icontains=search_query)
            | Q(address__street_address__icontains=search_query)
        )

    if status_filter and status_filter != "all":
        orders = orders.filter(status=status_filter)

    # Pagination
    paginator = Paginator(orders, 10)  # Show 10 orders per page
    page_number = request.GET.get("page", 1)
    orders_page = paginator.get_page(page_number)

    context = {
        "orders": orders_page,
        "search_query": search_query,
        "status_filter": status_filter,
        "status_choices": Order.StatusChoices.choices,
    }

    return render(request, "users/admin/orders/index.html", context)


@login_required
@user_passes_test(is_admin)
def admin_order_detail(request, order_id):
    order = get_object_or_404(
        Order.objects.select_related(
            "shipping_address", "billing_address", "user"
        ).prefetch_related("items", "items__product"),
        id=order_id,
    )

    context = {
        "order": order,
    }
    return render(request, "users/admin/orders/detail.html", context)


@login_required
def admin_order_edit(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "users/admin/orders/edit.html", {"order": order})


@user_passes_test(is_admin)
def admin_categories(request):
    categories = Category.objects.all()
    context = {"categories": categories}
    return render(request, "users/admin/categories/index.html", context)


@user_passes_test(is_admin)
def admin_category_add(request):
    if request.method == "POST":
        name = request.POST.get("name")
        status = request.POST.get("status")
        image = request.FILES.get("image")

        category = Category.objects.create(name=name, status=status, image=image)
        messages.success(request, "Category added successfully!")
        return redirect("users:admin_categories")

    return render(request, "users/admin/categories/add.html")


@user_passes_test(is_admin)
def admin_category_edit(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == "POST":
        category.name = request.POST.get("name")
        category.status = request.POST.get("status")

        if "image" in request.FILES:
            category.image = request.FILES["image"]

        category.save()
        messages.success(request, "Category updated successfully!")
        return redirect("users:admin_categories")

    context = {"category": category}
    return render(request, "users/admin/categories/edit.html", context)


@user_passes_test(is_admin)
def admin_offers(request):
    offers = Offer.objects.all().order_by("-created")
    context = {"offers": offers}
    return render(request, "users/admin/offers/index.html", context)


@user_passes_test(is_admin)
def admin_offer_add(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        offer_type = request.POST.get("offer_type")
        discount_value = request.POST.get("discount_value")
        buy_quantity = request.POST.get("buy_quantity", 1)
        get_quantity = request.POST.get("get_quantity", 0)
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        is_active = request.POST.get("status") == "active"
        min_purchase_amount = request.POST.get("min_purchase_amount", 0)
        usage_limit = request.POST.get("usage_limit", 0)
        image = request.FILES.get("image")

        offer = Offer.objects.create(
            title=title,
            description=description,
            offer_type=offer_type,
            discount_value=discount_value,
            buy_quantity=buy_quantity,
            get_quantity=get_quantity,
            start_date=start_date,
            end_date=end_date,
            is_active=is_active,
            min_purchase_amount=min_purchase_amount,
            usage_limit=usage_limit,
            image=image,
        )
        messages.success(request, "Offer added successfully!")
        return redirect("users:admin_offers")

    return render(
        request, "users/admin/offers/add.html", {"offer_types": Offer.OfferType.choices}
    )


@user_passes_test(is_admin)
def admin_offer_edit(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)

    if request.method == "POST":
        offer.title = request.POST.get("title")
        offer.description = request.POST.get("description")
        offer.offer_type = request.POST.get("offer_type")
        offer.discount_value = request.POST.get("discount_value")
        offer.buy_quantity = request.POST.get("buy_quantity", 1)
        offer.get_quantity = request.POST.get("get_quantity", 0)
        offer.start_date = request.POST.get("start_date")
        offer.end_date = request.POST.get("end_date")
        offer.is_active = request.POST.get("status") == "active"
        offer.min_purchase_amount = request.POST.get("min_purchase_amount", 0)
        offer.usage_limit = request.POST.get("usage_limit", 0)

        if "image" in request.FILES:
            offer.image = request.FILES["image"]

        offer.save()
        messages.success(request, "Offer updated successfully!")
        return redirect("users:admin_offers")

    context = {"offer": offer, "offer_types": Offer.OfferType.choices}
    return render(request, "users/admin/offers/edit.html", context)


@user_passes_test(is_admin)
def admin_offer_delete(request, offer_id):
    if request.method == "POST":
        offer = get_object_or_404(Offer, id=offer_id)
        offer.delete()
        messages.success(request, "Offer deleted successfully!")
    return redirect("users:admin_offers")


@user_passes_test(is_admin)
def admin_products(request):
    # Get filter parameters
    search_query = request.GET.get("search", "")
    category_id = request.GET.get("category", "")

    # Base queryset
    products = (
        Product.objects.select_related("category").prefetch_related("images").all()
    )

    # Apply filters
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | Q(sku__icontains=search_query)
        )

    if category_id:
        products = products.filter(category_id=category_id)

    # Pagination
    paginator = Paginator(products, 10)  # Show 10 products per page
    page_number = request.GET.get('page', 1)
    products_page = paginator.get_page(page_number)

    # Get all categories for the filter dropdown
    categories = Category.objects.filter(status=Category.StatusChoices.ACTIVE)

    context = {
        "products": products_page,
        "categories": categories,
        "search_query": search_query,
        "selected_category": category_id,
    }
    return render(request, "users/admin/products/index.html", context)


@user_passes_test(is_admin)
def admin_product_add(request):
    if request.method == "POST":
        # Basic product info
        name = request.POST.get("name")
        description = request.POST.get("description")
        additional_details = request.POST.get("additional_details")
        category_id = request.POST.get("category")
        original_price = request.POST.get("original_price")
        selling_price = request.POST.get("selling_price")
        stock = request.POST.get("stock")
        stock_unit = request.POST.get("stock_unit")
        minimum_stock = request.POST.get("minimum_stock", 0)
        sku = request.POST.get("sku")
        is_active = request.POST.get("status") == "active"

        # Create product
        product = Product.objects.create(
            name=name,
            description=description,
            additional_details=additional_details,
            category_id=category_id,
            original_price=original_price,
            selling_price=selling_price,
            stock=stock,
            stock_unit=stock_unit,
            minimum_stock=minimum_stock,
            sku=sku,
            is_active=is_active,
            slug=slugify(name),  # You'll need to import slugify
        )

        # Handle images
        images = request.FILES.getlist("images")
        for index, image in enumerate(images):
            ProductImage.objects.create(
                product=product,
                image=image,
                is_primary=(index == 0),  # First image is primary
            )

        messages.success(request, "Product added successfully!")
        return redirect("users:admin_products")

    categories = Category.objects.filter(status=Category.StatusChoices.ACTIVE)
    context = {
        "categories": categories,
        "stock_units": Product.StockUnitChoices.choices,
    }
    return render(request, "users/admin/products/add.html", context)


@login_required
@user_passes_test(is_admin)
def admin_product_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        # Update basic info
        product.name = request.POST.get("name")
        product.description = request.POST.get("description")
        product.additional_details = request.POST.get("additional_details")
        product.category_id = request.POST.get("category")
        product.original_price = request.POST.get("original_price")
        product.selling_price = request.POST.get("selling_price")
        product.stock = request.POST.get("stock")
        product.stock_unit = request.POST.get("stock_unit")
        product.minimum_stock = request.POST.get("minimum_stock", 0)
        product.sku = request.POST.get("sku")
        product.is_active = request.POST.get("is_active") == "on"
        product.slug = slugify(request.POST.get("name"))

        # Handle primary image
        uploaded_primary_image = request.FILES.get("primary_image")
        if uploaded_primary_image:
            # If there's an existing primary image, update it
            primary_image_obj = ProductImage.objects.filter(product=product, is_primary=True).first()
            if primary_image_obj:
                primary_image_obj.image = uploaded_primary_image
                primary_image_obj.save()
            else:
                # Create new primary image
                ProductImage.objects.create(
                    product=product,
                    image=uploaded_primary_image,
                    is_primary=True
                )

        # Handle additional images
        additional_images = request.FILES.getlist("additional_images")
        for image in additional_images:
            ProductImage.objects.create(
                product=product,
                image=image,
                is_primary=False
            )

        product.save()
        messages.success(request, "Product updated successfully!")
        return redirect("users:admin_products")

    categories = Category.objects.filter(status=Category.StatusChoices.ACTIVE)
    context = {
        "product": product,
        "categories": categories,
        "stock_units": Product.StockUnitChoices.choices,
    }
    return render(request, "users/admin/products/edit.html", context)


@user_passes_test(is_admin)
def admin_product_view(request, product_id):
    product = get_object_or_404(
        Product.objects.select_related("category").prefetch_related(
            "images", "variants"
        ),
        id=product_id,
    )
    context = {
        "product": product,
    }
    return render(request, "users/admin/products/detail.html", context)


@user_passes_test(is_admin)
def admin_product_delete(request, product_id):
    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id)
        product.delete()
        messages.success(request, "Product deleted successfully!")
    return redirect("users:admin_products")


@user_passes_test(is_admin)
def admin_product_image_delete(request, image_id):
    if request.method == "POST":
        image = get_object_or_404(ProductImage, id=image_id)
        product_id = image.product.id

        # Don't delete if it's the only image
        if image.product.images.count() > 1:
            # If deleting primary image, make another image primary
            if image.is_primary:
                new_primary = image.product.images.exclude(id=image_id).first()
                if new_primary:
                    new_primary.is_primary = True
                    new_primary.save()

            image.delete()
            messages.success(request, "Product image deleted successfully!")
        else:
            messages.error(request, "Cannot delete the only product image!")

    return redirect("users:admin_product_edit", product_id=product_id)


@login_required
def update_order_status(request, order_id):
    if not request.user.is_superuser:
        messages.error(request, "You are not authorized to perform this action")
        return redirect("users:admin.orders")

    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in ["pending", "processing", "shipped", "delivered", "cancelled"]:
            order.status = new_status
            order.save()
            messages.success(request, f"Order status updated to {new_status}")
        else:
            messages.error(request, "Invalid status")

    return redirect("users:admin.order_edit", order_id=order_id)


@login_required
def generate_order_pdf(request, order_id):
    if not request.user.is_superuser:
        messages.error(request, "You are not authorized to perform this action")
        return redirect("users:admin.orders")

    order = get_object_or_404(
        Order.objects.select_related("user", "shipping_address").prefetch_related(
            "items", "items__product"
        ),
        id=order_id,
    )

    # Create a file-like buffer to receive PDF data
    buffer = BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer, pagesize=letter)

    # Draw things on the PDF
    # Header
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, 750, f"Order Invoice #{order.order_number}")

    # Order Info
    p.setFont("Helvetica", 12)
    p.drawString(50, 720, f"Date: {order.created.strftime('%d %b %Y')}")
    p.drawString(50, 700, f"Status: {order.status.upper()}")

    # Customer Info
    p.drawString(50, 670, "Customer Information:")
    p.setFont("Helvetica", 10)
    p.drawString(70, 650, f"Name: {order.user.name}")
    p.drawString(70, 635, f"Email: {order.user.email}")

    # Shipping Address
    p.setFont("Helvetica", 12)
    p.drawString(50, 605, "Shipping Address:")
    p.setFont("Helvetica", 10)
    address_lines = str(order.shipping_address).split("\n")
    y = 585
    for line in address_lines:
        p.drawString(70, y, line)
        y -= 15

    # Order Items
    data = [["Item", "Price", "Quantity", "Total"]]
    for item in order.items.all():
        data.append(
            [
                item.product.name,
                f"৳{item.price}",
                str(item.quantity),
                f"৳{item.subtotal}",
            ]
        )

    # Add totals
    data.append(["", "", "Subtotal:", f"৳{order.total_amount}"])
    data.append(["", "", "Delivery:", f"৳{order.delivery_charge or 0}"])
    data.append(["", "", "Grand Total:", f"৳{order.grand_total}"])

    table = Table(data, colWidths=[250, 100, 100, 100])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("ALIGN", (-1, 0), (-1, -1), "RIGHT"),
            ]
        )
    )

    table.wrapOn(p, 50, 50)
    table.drawOn(p, 50, 350)

    # Footer
    p.setFont("Helvetica", 8)
    p.drawString(
        50, 50, f"Generated on: {timezone.now().strftime('%d %b %Y %H:%M:%S')}"
    )

    # Close the PDF object cleanly
    p.showPage()
    p.save()

    # Get the value of the BytesIO buffer and write it to the response
    pdf = buffer.getvalue()
    buffer.close()

    # Create the HTTP response
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="order_{order.order_number}.pdf"'
    )
    response.write(pdf)

    return response


@login_required
@user_passes_test(is_admin)
def admin_customers(request):
    search_query = request.GET.get("search", "")

    # Base queryset with annotated order count and total spent
    customers = User.objects.annotate(
        order_count=Count("orders"),
        total_spent=Sum("orders__total_amount", filter=Q(orders__status="delivered")),
    )

    # Apply search filter
    if search_query:
        customers = customers.filter(
            Q(name__icontains=search_query)
            | Q(email__icontains=search_query)
            | Q(phone__icontains=search_query)
        )

    paginator = Paginator(customers, 10)
    page_number = request.GET.get("page", 1)
    customers_page = paginator.get_page(page_number)

    context = {"customers": customers_page, "search_query": search_query}
    return render(request, "users/admin/customers/index.html", context)


@login_required
@user_passes_test(is_admin)
def admin_customer_detail(request, user_id):
    customer = get_object_or_404(
        User.objects.annotate(
            order_count=Count("orders"),
            total_spent=Sum(
                "orders__total_amount", filter=Q(orders__status="delivered")
            ),
        ),
        id=user_id,
    )

    orders = Order.objects.filter(user=customer).order_by("-created")

    context = {"customer": customer, "orders": orders}
    return render(request, "users/admin/customers/detail.html", context)


@login_required
@user_passes_test(is_admin)
def admin_general_settings(request):
    if request.method == "POST":
        site_name = request.POST.get("site_name")
        site_logo = request.FILES.get("site_logo")
        favicon = request.FILES.get("favicon")
        contact_email = request.POST.get("contact_email")
        contact_phone = request.POST.get("contact_phone")
        address = request.POST.get("address")

        settings = SiteSettings.load()
        settings.update_general_settings(
            site_name=site_name,
            site_logo=site_logo,
            favicon=favicon,
            contact_email=contact_email,
            contact_phone=contact_phone,
            address=address,
        )
        messages.success(request, "General settings updated successfully")

    context = {"settings": SiteSettings.load()}
    return render(request, "users/admin/settings/general.html", context)


@login_required
@user_passes_test(is_admin)
def admin_payment_settings(request):
    if request.method == "POST":
        stripe_public_key = request.POST.get("stripe_public_key")
        stripe_secret_key = request.POST.get("stripe_secret_key")
        paypal_client_id = request.POST.get("paypal_client_id")
        paypal_secret = request.POST.get("paypal_secret")
        currency = request.POST.get("currency")

        settings = SiteSettings.load()
        settings.update_payment_settings(
            stripe_public_key=stripe_public_key,
            stripe_secret_key=stripe_secret_key,
            paypal_client_id=paypal_client_id,
            paypal_secret=paypal_secret,
            currency=currency,
        )
        messages.success(request, "Payment settings updated successfully")

    context = {"settings": SiteSettings.load(), "currencies": CURRENCY_CHOICES}
    return render(request, "users/admin/settings/payment.html", context)


@login_required
@user_passes_test(is_admin)
def admin_email_settings(request):
    if request.method == "POST":
        smtp_host = request.POST.get("smtp_host")
        smtp_port = request.POST.get("smtp_port")
        smtp_user = request.POST.get("smtp_user")
        smtp_password = request.POST.get("smtp_password")
        email_from = request.POST.get("email_from")

        settings = SiteSettings.load()
        settings.update_email_settings(
            smtp_host=smtp_host,
            smtp_port=smtp_port,
            smtp_user=smtp_user,
            smtp_password=smtp_password,
            email_from=email_from,
        )
        messages.success(request, "Email settings updated successfully")

    context = {"settings": SiteSettings.load()}
    return render(request, "users/admin/settings/email.html", context)


@login_required
@user_passes_test(is_admin)
def admin_reports(request):
    report_type = request.GET.get("type", "sales")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    # Base queryset
    orders = Order.objects.filter(status="delivered")

    # Apply date filters if provided
    if start_date:
        orders = orders.filter(created__gte=start_date)
    if end_date:
        orders = orders.filter(created__lte=end_date)

    context = {
        "report_type": report_type,
        "start_date": start_date,
        "end_date": end_date,
    }

    if report_type == "sales":
        # Daily sales report
        daily_sales = (
            orders.annotate(date=TruncDate("created"))
            .values("date")
            .annotate(total_orders=Count("id"), total_sales=Sum("total_amount"))
            .order_by("-date")
        )
        context["daily_sales"] = daily_sales

    elif report_type == "products":
        # Product performance report
        product_sales = (
            OrderItem.objects.filter(order__in=orders)
            .values("product__name")
            .annotate(
                total_quantity=Sum("quantity"),
                total_sales=Sum(F("price") * F("quantity"))  # Calculate total sales
            )
            .order_by("-total_quantity")
        )
        context["product_sales"] = product_sales

    elif report_type == "customers":
        # Customer analysis report
        customer_stats = (
            orders.values("user__name", "user__email")
            .annotate(total_orders=Count("id"), total_spent=Sum("total_amount"))
            .order_by("-total_spent")
        )
        context["customer_stats"] = customer_stats

    elif report_type == "payment":
        # Payment method analysis
        payment_stats = (
            orders.values("payment_method")
            .annotate(total_orders=Count("id"), total_amount=Sum("total_amount"))
            .order_by("-total_amount")
        )
        context["payment_stats"] = payment_stats

    return render(request, "users/admin/reports/index.html", context)
