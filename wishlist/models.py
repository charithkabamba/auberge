from django.db import models
from django_extensions.db.models import TimeStampedModel
from users.models import User
from products.models import Product


class Wishlist(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlist")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "product")
        ordering = ["-created"]

    def __str__(self):
        return f"{self.user.name}'s wishlist item - {self.product.name}"
