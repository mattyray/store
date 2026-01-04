from django.urls import path

from . import views

app_name = 'payments'

urlpatterns = [
    path('checkout/', views.CreateCheckoutSessionView.as_view(), name='checkout'),
    path('webhooks/stripe/', views.StripeWebhookView.as_view(), name='stripe-webhook'),
    path('order/', views.OrderLookupView.as_view(), name='order-lookup'),
]
