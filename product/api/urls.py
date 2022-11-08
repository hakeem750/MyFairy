from django.urls import path
from .views import ProductListView, ProductDetailView

app_name = "product"

urlpatterns = [
    path("product", ProductListView.as_view(), name="product-list"),
    path("product/<slug:slug>/", ProductDetailView.as_view(), name="product-slug-show"),
]
