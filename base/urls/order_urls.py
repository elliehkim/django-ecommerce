from django.urls import path, re_path
from base.views import order_views as views



urlpatterns = [
    path('create_payment_intent/', views.create_payment, name='create_payment_intent'),
    path('myorders/', views.getMyOrders, name='get_my_orders'),
    path('<str:pk>', views.getOrderById, name='get_order_byid'),
    path('webhooks/stripe/', views.stripe_webhook, name='stripe_webhook'),
]