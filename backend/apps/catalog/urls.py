from django.urls import path

from . import views

app_name = 'catalog'

urlpatterns = [
    path('collections/', views.CollectionListView.as_view(), name='collection-list'),
    path('collections/<slug:slug>/', views.CollectionDetailView.as_view(), name='collection-detail'),
    path('photos/', views.PhotoListView.as_view(), name='photo-list'),
    path('photos/featured/', views.FeaturedPhotosView.as_view(), name='photo-featured'),
    path('photos/<slug:slug>/', views.PhotoDetailView.as_view(), name='photo-detail'),
    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('products/<slug:slug>/', views.ProductDetailView.as_view(), name='product-detail'),
]
