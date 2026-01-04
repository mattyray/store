from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('contact/', views.ContactFormView.as_view(), name='contact'),
    path('health/', views.HealthCheckView.as_view(), name='health'),
    # Newsletter
    path('newsletter/subscribe/', views.NewsletterSubscribeView.as_view(), name='newsletter-subscribe'),
    path('newsletter/unsubscribe/', views.NewsletterUnsubscribeView.as_view(), name='newsletter-unsubscribe'),
    # Gift Cards
    path('gift-cards/purchase/', views.GiftCardPurchaseView.as_view(), name='gift-card-purchase'),
    path('gift-cards/check/', views.GiftCardCheckView.as_view(), name='gift-card-check'),
]
