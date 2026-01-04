from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('contact/', views.ContactFormView.as_view(), name='contact'),
    path('health/', views.HealthCheckView.as_view(), name='health'),
]
