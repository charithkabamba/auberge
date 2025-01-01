from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'status', 'payment_status', 'total_amount', 'created']
    list_filter = ['status', 'payment_status']
    search_fields = ['order_number', 'user__name', 'user__email']
    inlines = [OrderItemInline] 