from django.db import models
from django.db.models import Min
from django_filters import rest_framework as filters
from rest_framework import generics
from rest_framework.filters import OrderingFilter

from .models import Collection, Photo
from .serializers import (
    CollectionListSerializer,
    CollectionDetailSerializer,
    PhotoListSerializer,
    PhotoDetailSerializer,
)


class PhotoFilter(filters.FilterSet):
    """Filter for photos."""
    collection = filters.CharFilter(field_name='collection__slug')
    location = filters.CharFilter(field_name='location_tag', lookup_expr='iexact')
    orientation = filters.ChoiceFilter(choices=Photo.ORIENTATION_CHOICES)
    material = filters.CharFilter(method='filter_by_material')
    min_price = filters.NumberFilter(method='filter_min_price')
    max_price = filters.NumberFilter(method='filter_max_price')
    featured = filters.BooleanFilter(field_name='is_featured')

    class Meta:
        model = Photo
        fields = ['collection', 'location', 'orientation', 'featured']

    def filter_by_material(self, queryset, name, value):
        """Filter photos that have variants in the specified material."""
        return queryset.filter(
            variants__material=value,
            variants__is_available=True
        ).distinct()

    def filter_min_price(self, queryset, name, value):
        """Filter photos with variants >= min price."""
        return queryset.filter(
            variants__price__gte=value,
            variants__is_available=True
        ).distinct()

    def filter_max_price(self, queryset, name, value):
        """Filter photos with variants <= max price."""
        return queryset.filter(
            variants__price__lte=value,
            variants__is_available=True
        ).distinct()


class CollectionListView(generics.ListAPIView):
    """List all active collections."""
    queryset = Collection.objects.filter(is_active=True)
    serializer_class = CollectionListSerializer


class CollectionDetailView(generics.RetrieveAPIView):
    """Get a single collection with its photos."""
    queryset = Collection.objects.filter(is_active=True)
    serializer_class = CollectionDetailSerializer
    lookup_field = 'slug'


class PhotoListView(generics.ListAPIView):
    """List all active photos with filtering."""
    serializer_class = PhotoListSerializer
    filterset_class = PhotoFilter
    filter_backends = [filters.DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['created_at', 'title', 'min_price']
    ordering = ['-created_at']

    def get_queryset(self):
        return Photo.objects.filter(is_active=True).select_related('collection').annotate(
            min_price=Min('variants__price', filter=models.Q(variants__is_available=True))
        )


class PhotoDetailView(generics.RetrieveAPIView):
    """Get a single photo with all variants."""
    queryset = Photo.objects.filter(is_active=True).select_related('collection')
    serializer_class = PhotoDetailSerializer
    lookup_field = 'slug'


class FeaturedPhotosView(generics.ListAPIView):
    """List featured photos for homepage."""
    queryset = Photo.objects.filter(is_active=True, is_featured=True).select_related('collection')
    serializer_class = PhotoListSerializer
    pagination_class = None
