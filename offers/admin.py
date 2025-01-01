from django.contrib import admin
from .models import Offer

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['title', 'offer_type', 'discount_value', 'start_date', 'end_date', 'is_active']
    list_filter = ['offer_type', 'is_active']
    search_fields = ['title', 'description']
    filter_horizontal = ['products'] 