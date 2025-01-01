from django.views.generic import ListView
from .models import Offer
from django.utils import timezone

class OfferListView(ListView):
    template_name = 'offers/list.html'
    context_object_name = 'offers'

    def get_queryset(self):
        return Offer.objects.filter(
            is_active=True,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        ).select_related() 