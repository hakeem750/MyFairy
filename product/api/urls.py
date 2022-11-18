from django.urls import path
from .views import (
    UserIDView,
    ProductListView,
    ProductDetailView,
    AddToCartView,
    OrderDetailView,
    OrderQuantityUpdateView,
    PaymentView,
    AddCouponView,
    CountryListView,
    AddressListView,
    AddressCreateView,
    AddressUpdateView,
    AddressDeleteView,
    OrderItemDeleteView,
    PaymentListView,
    BankView,
    CreditcardView,
)

app_name = "product"

urlpatterns = [
    path("user-id/", UserIDView.as_view(), name="user-id"),
    path("credit-card/", CreditcardView.as_view(), name="credit-card"),
    path("bank/", BankView.as_view(), name="bank"),
    path("countries/", CountryListView.as_view(), name="country-list"),
    path("addresses/", AddressListView.as_view(), name="address-list"),
    path("addresses/create/", AddressCreateView.as_view(), name="address-create"),
    path("addresses/<pk>/update/", AddressUpdateView.as_view(), name="address-update"),
    path("addresses/<pk>/delete/", AddressDeleteView.as_view(), name="address-delete"),
    path("products/", ProductListView.as_view(), name="product-list"),
    path("products/<pk>/", ProductDetailView.as_view(), name="product-detail"),
    path("add-to-cart/", AddToCartView.as_view(), name="add-to-cart"),
    path("order-summary/", OrderDetailView.as_view(), name="order-summary"),
    path("checkout/", PaymentView.as_view(), name="checkout"),
    path("add-coupon/", AddCouponView.as_view(), name="add-coupon"),
    path(
        "order-items/<pk>/delete/",
        OrderItemDeleteView.as_view(),
        name="order-item-delete",
    ),
    path(
        "order-item/update-quantity/",
        OrderQuantityUpdateView.as_view(),
        name="order-item-update-quantity",
    ),
    path("payments/", PaymentListView.as_view(), name="payment-list"),
]
