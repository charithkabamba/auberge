from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('success/<str:order_number>/', views.order_success, name='success'),
    path('api/<int:order_id>/cancel/', views.cancel_order, name='cancel'),
]
