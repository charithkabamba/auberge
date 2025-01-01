from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('api/list/', views.CartListAPIView.as_view(), name='cart'),
    path('api/add/', views.add_to_cart, name='add'),
    path('api/update/', views.update_cart_item, name='update'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('api/place-order/', views.place_order, name='place_order'),
    path('create-payment-intent/', views.PaymentIntentView.as_view(), name='create_payment_intent'),
    path('confirm-payment/', views.PaymentConfirmView.as_view(), name='confirm_payment'),
]
