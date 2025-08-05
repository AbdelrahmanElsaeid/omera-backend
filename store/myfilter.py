from .models import Product
from django_filters import rest_framework as filters
import urllib.parse
from .models import Category

class ProductFilter(filters.FilterSet):
    color = filters.CharFilter(field_name='color_product__name', lookup_expr='exact')
    brand__title = filters.CharFilter(field_name='brand__title_en', lookup_expr='exact')
    category__title = filters.CharFilter(field_name='category__title_en', lookup_expr='exact')

   

    class Meta:
        model = Product
        fields = {
            #'brand': ['in'],
            "title_en": ["icontains"],
            #"category": ["exact"],
            #"brand": ["exact"],
            "rating": ["exact"],
            #"price_EGP": ["lte", "gte", "range"],
            #"price_AED": ["lte", "gte", "range"],
        }
