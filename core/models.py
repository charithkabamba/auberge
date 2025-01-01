from django.db import models
from django.utils import timezone

CURRENCY_CHOICES = [
    ("BDT", "Bangladeshi Taka"),
]


class SiteSettings(models.Model):
    # General Settings
    site_name = models.CharField(max_length=100, default="WOWY")
    site_logo = models.ImageField(upload_to="site/", null=True, blank=True)
    favicon = models.ImageField(upload_to="site/", null=True, blank=True)
    contact_email = models.EmailField(null=True, blank=True)
    contact_phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    # Payment Settings
    paypal_client_id = models.CharField(max_length=255, null=True, blank=True)
    paypal_secret = models.CharField(max_length=255, null=True, blank=True)
    currency = models.CharField(max_length=3, default="BDT", choices=CURRENCY_CHOICES)

    # Email Settings
    smtp_host = models.CharField(max_length=255, null=True, blank=True)
    smtp_port = models.IntegerField(null=True, blank=True)
    smtp_user = models.CharField(max_length=255, null=True, blank=True)
    smtp_password = models.CharField(max_length=255, null=True, blank=True)
    email_from = models.EmailField(null=True, blank=True)

    # Privacy Settings
    privacy_last_updated = models.DateField(default=timezone.now)
    # Terms Settings
    terms_last_updated = models.DateField(default=timezone.now)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def update_general_settings(self, **kwargs):
        for key, value in kwargs.items():
            if value is not None:  # Only update if value is provided
                setattr(self, key, value)
        self.save()

    def update_payment_settings(self, **kwargs):
        for key, value in kwargs.items():
            if value is not None:  # Only update if value is provided
                setattr(self, key, value)
        self.save()

    def update_email_settings(self, **kwargs):
        for key, value in kwargs.items():
            if value is not None:  # Only update if value is provided
                setattr(self, key, value)
        self.save()
