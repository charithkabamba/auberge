from django.urls import path
from . import views

app_name = 'offers'

urlpatterns = [
    path('', views.OfferListView.as_view(), name='list'),
] 