from django.db.models.signals import post_save
from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.shortcuts import reverse
from django_countries.fields import CountryField

from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.text import slugify
from django.utils import timezone
from index.model.user import User

import os, stripe
from decouple import config
from datetime import datetime
from stripe import BalanceTransaction


stripe.api_key = config("STRIPE_SECRET_KEY")

CATEGORY = (
    ("Sanitary Kits", "Sanitary Kits"),
    ("Contraceptives", "Contraceptives"),
    ("Fashion", "Fashion"),
    ("Others", "Others"),
)

ORDER_TRACKING_CHOICES = (
    ("Pending", "Pending"),
    ("Processing", "Processing"),
    ("Dispatched", "Dispatched"),
    ("Shipped", "Shipped"),
    ("Delivered", "Delivered"),
)
CURRENCY_OPTIONS = (("usd", "USD"),)

LABEL_CHOICES = (("P", "primary"), ("S", "secondary"), ("D", "danger"))

PAYMENT_METHOD = (
    ("COS", "Cash on Delivery"),
    ("CDC", "CreditCard"),
    ("BNT", "Bank Transfer"),
)

ADDRESS_CHOICES = (
    ("B", "Billing"),
    ("S", "Shipping"),
)


class ExchangeRate(object):
    def get_exchange_rate_and_fee(charge):
        try:
            balance_transaction = (
                charge["balance_transaction"] or charge.getBalanceTransaction()
            )
            balanceTransaction = BalanceTransaction.retrieve(balance_transaction)
            exchange_rate = balanceTransaction.getExchangeRate()
            transaction_fee = balanceTransaction["fee"]
            if isinstance(float(exchange_rate), float) or isinstance(
                float(transaction_fee), float
            ):
                # return {"exchange_rate":float(exchange_rate),"transaction_fee": float(transaction_fee)}
                return {
                    "status": True,
                    "exchange_rate": float(650.00),
                    "transaction_fee": float(2.980),
                }

            return {"status": False}
        except:
            return {"status": False}


class InitiateTransaction(object):
    def __init__(self, cart, stripe_order_token):
        self.cart = cart
        self.stripe_order_token = stripe_order_token

    def create_charge(self):
        return stripe.Charge.create(
            amount=int(100 * self.cart.grand_total()),
            currency="usd",
            description="Order payment for Goods bought on Endless Factory",
            source=self.stripe_order_token,
        )


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100, null=True)
    apartment_address = models.CharField(max_length=100, null=True)
    country = CountryField(multiple=False)
    zip_code = models.CharField(max_length=100, null=True)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES, default="S")
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = "Addresses"


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.FloatField()

    def __str__(self):
        return self.code


class CreditCard(models.Model):
    user = models.ForeignKey(User, default=None, on_delete=models.CASCADE)
    card_number = models.CharField(null=False, max_length=20)
    brand = models.CharField(null=True, blank=True, max_length=20)
    exp_month = models.IntegerField(
        null=False, validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    cvv = models.CharField(max_length=3)
    exp_year = models.IntegerField(
        null=False, validators=[MinValueValidator(1900), MaxValueValidator(2100)]
    )
    fullname = models.CharField(null=True, blank=True, max_length=255)

    def display_number(self):
        print(str(self.card_number)[-4:])
        return "XXXX XXXX XXXX " + str(self.card_number)[-4:]


class Bank(models.Model):
    user = models.ForeignKey(User, default=None, on_delete=models.CASCADE)
    account_number = models.CharField(null=False, max_length=20)
    bank = models.CharField(null=True, blank=True, max_length=20)
    fullname = models.CharField(null=True, blank=True, max_length=255)


# def userprofile_receiver(sender, instance, created, *args, **kwargs):
#     if created:
#         userprofile = UserProfile.objects.create(user=instance)
class Product(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.CharField(choices=CATEGORY, max_length=20)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1, null=True)
    slug = models.SlugField()
    description = models.TextField()
    stock = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    image = models.ImageField()
    initial_stock = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    current_stock = models.IntegerField(validators=[MinValueValidator(0)], default=0)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("core:product", kwargs={"slug": self.slug})

    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart", kwargs={"slug": self.slug})

    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart", kwargs={"slug": self.slug})


class Variation(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,  # related_name="variant"
    )
    name = models.CharField(max_length=50)  # size
    stock = models.IntegerField(validators=[MinValueValidator(0)])

    class Meta:
        unique_together = ("product", "name")

    def __str__(self):
        return self.name


class ProductVariation(models.Model):
    variation = models.ForeignKey(Variation, on_delete=models.CASCADE)
    value = models.CharField(max_length=50)  # S, M, L
    attachment = models.ImageField(blank=True)

    class Meta:
        unique_together = ("variation", "value")

    def __str__(self):
        return self.value


class OrderProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_variations = models.ManyToManyField(ProductVariation)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.product.title}"

    def get_total_item_price(self):
        return self.quantity * self.product.price

    def get_total_discount_item_price(self):
        return self.quantity * self.product.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.product.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()


class Order(models.Model):
    number = models.CharField(max_length=32, editable=False, null=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    products = models.ManyToManyField(OrderProduct)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    shipping_address = models.ForeignKey(
        Address,
        related_name="shipping_address",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    billing_address = models.ForeignKey(
        Address,
        related_name="billing_address",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    payment = models.ForeignKey(
        Payment, on_delete=models.SET_NULL, blank=True, null=True
    )
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    """
    1. Item added to cart
    2. Adding a billing address
    (Failed checkout)
    3. Payment
    (Preprocessing, processing, packaging etc.)
    4. Being delivered
    5. Received
    6. Refunds
    """

    def __str__(self):
        return self.user.username

    def transaction(self):
        return self.transaction_set.first()

    def set_line_items_from_cart(self, cart, order_number, buyer):

        for item in cart.products.all():
            try:
                line_item = LineItem(
                    order=self,
                    user=buyer,
                    quantity=item.quantity,
                    price=item.product.price,
                    order_number=order_number,
                )
                line_item.save()
            except Exception as e:
                line_item = LineItem(
                    order=self,
                    user=buyer,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price,
                    order_number=order_number,
                )
                line_item.save()
            try:
                product = line_item.product
                product.current_stock -= line_item.quantity
                product.save()
            except Exception as e:
                pass
                # log.error(
                #     str(
                #         "An error occured while decrementing non variant product stock "
                #     )
                #     + str(e)
                # )

    def set_transaction(self, user, charge, time_range):

        transaction = Transaction(order=self)
        transaction.customer = user
        transaction.transaction_id = charge["id"]
        transaction.time_sent = time_range[0]
        transaction.time_arrived = time_range[1]
        transaction.amount_paid = charge["amount"]
        transaction.status = charge["paid"]
        transaction.currency = charge["currency"]
        transaction.receipt_url = charge["receipt_url"]
        transaction.payment_method = charge["payment_method"].split("_")[0]
        exchange_rate_fee = transaction.ExchangeRate.get_exchange_rate_and_fee(charge)

        if exchange_rate_fee["status"]:
            transaction.exchange_rate = exchange_rate_fee["exchange_rate"]
            transaction.transaction_fee = exchange_rate_fee["transaction_fee"]
        else:
            transaction.exchange_rate = 0.00
            transaction.transaction_fee = 0.00

        transaction.save()

    def get_total(self):
        total = 0
        for order_item in self.products.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return total

    def generate_number(self):
        last_order = Order.objects.last()
        number = "EF" + str((last_order.id if last_order is not None else 0) + 1).rjust(
            10, "0"
        )
        self.number = number
        return number

    def save(self, *args, **kwargs):
        number = None
        if not self.pk:
            number = self.generate_number()
        super().save(*args, **kwargs)
        return number


class Refunds(models.Model):

    customer = models.CharField(max_length=250, editable=False, null=False, blank=False)
    refund_id = models.CharField(max_length=250, editable=False, null=False)
    amount = models.DecimalField(
        validators=[MinValueValidator(0)],
        null=False,
        default=0,
        decimal_places=2,
        max_digits=20,
    )
    currency = models.CharField(max_length=250, default="usd", null=True, blank=True)
    related_charge = models.CharField(max_length=250, null=False, blank=False)
    refund_reason = models.TextField(
        max_length=1000, editable=False, null=True, blank=True
    )
    status = models.CharField(max_length=32, editable=False, null=False, blank=False)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)


class OrderTracking(models.Model):

    tracking_number = models.CharField(max_length=250, default="", unique=True)
    order_created_at = models.CharField(max_length=250, default="")
    processed_at = models.CharField(max_length=250, default="")
    processing_comment = models.CharField(max_length=250, default="")
    dispatched_at = models.CharField(max_length=250, default="")
    dispatched_comment = models.CharField(max_length=250, default="")
    shipped_at = models.CharField(max_length=250, default="")
    shipping_comment = models.CharField(max_length=250, default="")
    delivered_at = models.CharField(max_length=250, default="")
    delivery_comment = models.CharField(max_length=250, default="")
    active_status = models.CharField(
        max_length=500, choices=ORDER_TRACKING_CHOICES, default="Pending"
    )


class Transaction(models.Model):

    customer = models.ForeignKey(
        User, default=None, blank=False, on_delete=models.CASCADE, null=False
    )
    transaction_id = models.CharField(
        max_length=32, editable=False, null=False
    )  # Stripe charge id
    time_sent = models.DateTimeField(null=True, blank=True)
    time_arrived = models.DateTimeField(null=True, blank=True)
    order = models.ForeignKey(Order, default=None, on_delete=models.CASCADE)
    credit_card = models.ForeignKey(
        CreditCard, default=None, blank=True, on_delete=models.CASCADE, null=True
    )
    payment_method = models.CharField(max_length=150, editable=False, null=False)
    currency = models.CharField(
        max_length=50, default="usd", editable=False, null=False
    )
    amount_paid = models.DecimalField(
        validators=[MinValueValidator(0)],
        null=False,
        default=0,
        decimal_places=2,
        max_digits=30,
    )
    transaction_fee = models.DecimalField(
        validators=[MinValueValidator(0)],
        null=False,
        default=0,
        decimal_places=2,
        max_digits=20,
    )
    exchange_rate = models.DecimalField(
        validators=[MinValueValidator(0)],
        null=False,
        default=0,
        decimal_places=2,
        max_digits=10,
    )
    receipt_url = models.CharField(
        max_length=250, editable=False, null=True, blank=True
    )
    status = models.CharField(max_length=32, editable=False, null=True, blank=True)

    def card_number_last_4(self):
        return self.credit_card.display_number()

    def card_brand(self):
        return self.credit_card.brand

    def card_expiry_month(self):
        return self.credit_card.exp_month

    def card_expiry_month(self):
        return self.credit_card.exp_month

    def card_expiry_year(self):
        return self.credit_card.exp_year

    def get_customer_id_via_charge_id(self, charge_id):
        return self.objects.filter(transaction_id=charge_id).customer


class LineItem(models.Model):
    order = models.ForeignKey(Order, default=None, null=True, on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, default=None, null=True, on_delete=models.CASCADE
    )
    product_variations = models.ManyToManyField(ProductVariation)
    ordertracking = models.ForeignKey(
        OrderTracking, default=None, null=True, on_delete=models.CASCADE
    )
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    courier_agency = models.CharField(
        max_length=32, null=True, blank=True, default="N/A"
    )
    tracking_number = models.CharField(
        max_length=32, null=True, blank=True, default="N/A"
    )
    quantity = models.IntegerField(
        validators=[MinValueValidator(0)], null=False, default=0
    )
    price = models.DecimalField(
        validators=[MinValueValidator(0)],
        null=False,
        default=0,
        decimal_places=2,
        max_digits=10,
    )
    order_status_desc = models.CharField(max_length=250, default="")
    order_status = models.CharField(
        max_length=100, choices=ORDER_TRACKING_CHOICES, default="Pending"
    )
    order_number = models.CharField(max_length=100, default="N/A")
    number = models.CharField(max_length=100, default="N/A")
    expected_delivery_timeframe = models.CharField(max_length=500, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def item_total(self):
        return self.price

    def buyer_default_address(self):
        return self.user.default_address()


class Review(models.Model):
    product = models.ForeignKey(
        Product, null=True, default=None, on_delete=models.CASCADE
    )
    user = models.ForeignKey(User, default=None, on_delete=models.CASCADE)
    review = models.CharField(max_length=300, default=None)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"{self.pk}"
