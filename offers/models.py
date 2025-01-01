from django.db import models
from django_extensions.db.models import TimeStampedModel
from products.models import Product


class Offer(TimeStampedModel):
    class OfferType(models.TextChoices):
        PERCENTAGE = "percentage", "Percentage"
        FIXED = "fixed", "Fixed Amount"
        BUY_GET = "buy_get", "Buy X Get Y"

    title = models.CharField(max_length=200)
    description = models.TextField()
    offer_type = models.CharField(
        max_length=20, choices=OfferType.choices, default=OfferType.PERCENTAGE
    )
    discount_value = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Percentage or fixed amount"
    )
    buy_quantity = models.PositiveIntegerField(
        default=1, help_text="For Buy X Get Y offers"
    )
    get_quantity = models.PositiveIntegerField(
        default=0, help_text="For Buy X Get Y offers"
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    products = models.ManyToManyField(Product, related_name="offers", blank=True)
    min_purchase_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )
    usage_limit = models.PositiveIntegerField(default=0, help_text="0 for unlimited")
    image = models.ImageField(upload_to="offers/", null=True, blank=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return self.title

    @property
    def is_expired(self):
        from django.utils import timezone

        return timezone.now() > self.end_date

    @property
    def is_started(self):
        from django.utils import timezone

        return timezone.now() >= self.start_date

    @property
    def is_available(self):
        return self.is_active and self.is_started and not self.is_expired
