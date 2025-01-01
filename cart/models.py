from django.db import models
from products.models import Product
from decimal import Decimal
from django.core.exceptions import ValidationError
from django_extensions.db.models import TimeStampedModel

from users.models import User


class Cart(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())

    def get_total(self):
        return self.total_price + Decimal("50.00")


class CartItem(TimeStampedModel):
    cart = models.ForeignKey(Cart, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"

    @property
    def unit_price(self):
        return self.product.selling_price

    @property
    def subtotal(self):
        return Decimal(self.quantity) * self.unit_price

    def clean(self):
        if self.quantity > self.product.stock:
            raise ValidationError("Requested quantity exceeds available stock")
