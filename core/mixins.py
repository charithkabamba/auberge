from django.conf import settings
from djstripe.models import APIKey
from djstripe.enums import APIKeyType
import stripe


class StripeMixin:
    def setup_stripe(self):
        """Configure Stripe with API keys from djstripe"""
        try:
            # Get Stripe keys from djstripe
            publishable_key = APIKey.objects.get(type=APIKeyType.publishable).secret
            secret_key = APIKey.objects.get(type=APIKeyType.secret).secret
            
            # Configure stripe with secret key
            stripe.api_key = secret_key
            
            return publishable_key, secret_key
        except APIKey.DoesNotExist:
            raise Exception("Stripe API keys not configured properly")

    def get_stripe_context(self):
        """Get Stripe publishable key for templates"""
        publishable_key, _ = self.setup_stripe()
        return {"stripe_publishable_key": publishable_key}
