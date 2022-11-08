from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.text import slugify
import itertools, uuid
from django.urls import reverse
from django.utils import timezone
from index.model.user import User


ORDER_TRACKING_CHOICES = (
    ("Pending", "Pending"),
    ("Processing", "Processing"),
    ("Dispatched", "Dispatched"),
    ("Shipped", "Shipped"),
    ("Delivered", "Delivered"),
)

DELIVERY_OPTION_CHOICES = (
    ("Pickup Available", "Pickup Available"),
    ("Delivery Available", "Delivery Available"),
    ("Both", "Both"),
)

PRICE_OPTION_CHOICES = (
    ("Fixed Price", "Fixed Price"),
    ("Sliding Scale Depending On Volume", "Sliding Scale Depending On Volume"),
    ("Contact Us", "Contact Us"),
)

ATTACHMENT_TYPE_OPTIONS = (
    ("Image", "Image"),
    ("Video", "Video"),
)

PRODUCT_CONDITION = (
    ("New", "New"),
    ("Refurbished", "Refurbished"),
)

CATEGORY = (
    ("Sanitary Kits", "Sanitary Kits"),
    ("Contraceptives", "Contraceptives"),
    ("Fashion", "Fashion"),
    ("Others", "Others"),
)

SIZE = (
    ("Small", "Small"),
    ("Medium", "Medium"),
    ("Large", "Large"),
    ("Extra Large", "Extra Large"),
)


class Product(models.Model):

    color = models.CharField(max_length=100, null=False, default="")
    title = models.CharField(max_length=200, null=False, default="")
    subtitle = models.CharField(max_length=200, null=False, default="")
    description = models.TextField()
    category = models.CharField(
        max_length=100, choices=CATEGORY, default="Sanitary Kits"
    )
    size = models.CharField(max_length=200, choices=SIZE, default="Medium")
    duration = models.IntegerField(default=30)
    initial_stock = models.IntegerField(validators=[MinValueValidator(0)])
    current_stock = models.IntegerField(validators=[MinValueValidator(0)])
    price = models.DecimalField(decimal_places=2, max_digits=9, default=100.0)
    discount = models.DecimalField(decimal_places=2, max_digits=9, default=1.0)

    payment_plan_acceptance_option = models.CharField(max_length=200)
    slug = models.SlugField(null=False, unique=True, editable=False)

    is_active = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    def display_image(self):
        return self.images()[0] if len(self.images()) > 0 else None

    def get_absolute_url(self):
        kwargs = {"slug": self.slug}
        return reverse("product-slug-show", kwargs=kwargs)

    def average_rating(self):
        total_rating = 0
        for review in self.review_set.all():
            total_rating += review.rating

        return total_rating / self.review_set.all().count()

    def images(self):
        images_paths = []
        for attachment in self.attachment_set.filter(attachment_type="Image"):
            if attachment.file and hasattr(attachment.file, "url"):
                images_paths.append(attachment.file.url)
        return images_paths

    def reviews(self):
        return self.review_set.all()

    def generate_slug(self):
        value = self.title
        slug_candidate = slug_original = slugify(value, allow_unicode=True)
        for i in itertools.count(1):
            if not Product.objects.filter(slug=slug_candidate).exists():
                break
            slug_candidate = "{}-{}".format(slug_original, i)

        self.slug = slug_candidate

    def save(self, *args, **kwargs):
        if not self.pk:
            self.generate_slug()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.subtitle


class Address(models.Model):
    user = models.ForeignKey(User, default=None, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, null=False, default="N/A")
    last_name = models.CharField(max_length=255, null=False, default="N/A")
    line_1 = models.CharField(max_length=255, null=False, default="N/A")
    line_2 = models.CharField(max_length=255, null=True, blank=True, default="N/A")
    city = models.CharField(max_length=255, null=False, default="N/A")
    zipcode = models.CharField(max_length=255, null=False, default="N/A")
    state = models.CharField(max_length=255, null=False, default="N/A")
    country = models.CharField(max_length=255, null=False, default="United Kingdom")
    is_shipping_address = models.BooleanField(default=False)
    is_default_address = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)


class CreditCard(models.Model):
    user = models.ForeignKey(User, default=None, on_delete=models.CASCADE)
    card_number = models.CharField(null=False, max_length=20)
    brand = models.CharField(null=True, blank=True, max_length=20)
    exp_month = models.IntegerField(
        null=False, validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    exp_year = models.IntegerField(
        null=False, validators=[MinValueValidator(1900), MaxValueValidator(2100)]
    )
    name_on_card = models.CharField(null=True, blank=True, max_length=255)

    def display_number(self):
        print(str(self.card_number)[-4:])
        return "XXXX XXXX XXXX " + str(self.card_number)[-4:]


class Review(models.Model):
    product = models.ForeignKey(
        Product, null=True, default=None, on_delete=models.CASCADE
    )
    user = models.ForeignKey(User, default=None, on_delete=models.CASCADE)
    review = models.CharField(max_length=300)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)


class ProductCountViews(models.Model):
    user = models.IntegerField(null=True)
    session = models.CharField(max_length=100, null=True)  # For Anonymous users
    product = models.ForeignKey(
        Product, default=None, on_delete=models.CASCADE, null=False
    )
    slug = models.SlugField(null=True)
    view_counts = models.IntegerField(default=None)


class Attachment(models.Model):
    product = models.ForeignKey(Product, default=None, on_delete=models.CASCADE)
    attachment_type = models.CharField(
        max_length=200, choices=ATTACHMENT_TYPE_OPTIONS, default="Image"
    )
    file = models.FileField(
        upload_to="myfairy/product_attachments", null=True, blank=False
    )

    def url(self):
        return self.file.url if self.file and hasattr(self.file, "url") else None


CURRENCY_OPTIONS = (("USD", "USD"),)

ORDER_TRACKING_CHOICES = (
    ("Pending", "Pending"),
    ("Processing", "Processing"),
    ("Dispatched", "Dispatched"),
    ("Shipped", "Shipped"),
    ("Delivered", "Delivered"),
)


class Cart(models.Model):
    user = models.ForeignKey(User, default=None, on_delete=models.CASCADE)

    def total(self):
        total = 0
        for item in self.cartitem_set.all():
            item_price = item.price
            total += item_price
        return total

    def grand_total(self):
        return Decimal(self.total())  # + self.endless_factory_cut()

    def items_count(self):
        count = 0
        for item in self.cartitem_set.all():
            count += item.quantity
        return count

    def is_empty(self):
        return self.cartitem_set.count() == 0

    def cart_items(self):
        return self.cartitem_set.all()

    def reset(self):
        for cartitem in self.cartitem_set.all():
            cartitem.delete()


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, default=None, on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, null=True, default=None, on_delete=models.CASCADE
    )
    quantity = models.IntegerField(
        validators=[MinValueValidator(1)], null=False, default=1
    )
    price = models.DecimalField(
        validators=[MinValueValidator(0)],
        null=False,
        default=0,
        decimal_places=2,
        max_digits=10,
    )

    def products(self):
        return self.product

    def subtotal(self):
        return self.product.price * self.quantity


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


class Order(models.Model):
    number = models.CharField(max_length=32, editable=False, null=False, unique=True)
    item_total = models.DecimalField(
        validators=[MinValueValidator(0)],
        null=False,
        default=0,
        decimal_places=2,
        max_digits=10,
    )
    total = models.DecimalField(
        validators=[MinValueValidator(0)],
        null=False,
        default=0,
        decimal_places=2,
        max_digits=10,
    )
    user = models.ForeignKey(
        User, default=None, on_delete=models.CASCADE, blank=True, null=True
    )
    tracking_number = models.CharField(
        max_length=32, null=True, blank=True, default="N/A"
    )
    shipping_address = models.ForeignKey(
        Address,
        on_delete=models.CASCADE,
        related_name="shipping_address",
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(auto_now=True)
    special_instructions = models.TextField()
    is_shipped = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)
    currency = models.CharField(
        null=False, editable=False, default="USD", max_length=32
    )
    cost_price = models.DecimalField(
        validators=[MinValueValidator(0)],
        null=False,
        default=0,
        decimal_places=2,
        max_digits=10,
    )

    def transaction(self):
        return self.transaction_set.first()

    def set_line_items_from_cart(self, cart, order_number, buyer):

        for item in cart.cartitem_set.all():
            try:
                business_source = item.variant.product.business_source
                option_type = item.variant.product.option_type.name
                option_value = item.variant.option_value.value
                line_item = LineItem(
                    order=self,
                    user=buyer,
                    variant=item.variant,
                    business_source=business_source,
                    quantity=item.quantity,
                    price=item.price,
                    cost_price=item.cost_price,
                    option_type=option_type,
                    option_value=option_value,
                    order_number=order_number,
                )
                line_item.save()
                variant = line_item.variant
                variant.save()
            except Exception as e:

                try:
                    business_source = item.product.business_source
                except Exception as e:
                    business_source = ""
                    log.info(
                        str(
                            "AN INNER ERROR OCCURED WHILE SETTING BUSINESS SOURCE IN INNER EXCEPTION "
                        )
                        + str(e)
                    )
                option_type = ""
                option_value = ""

                line_item = LineItem(
                    order=self,
                    user=buyer,
                    product=item.product,
                    variant=item.variant,
                    business_source=business_source,
                    quantity=item.quantity,
                    price=item.price,
                    cost_price=item.cost_price,
                    option_type=option_type,
                    option_value=option_value,
                    order_number=order_number,
                )
                line_item.save()
                try:
                    product = line_item.product
                    log.info(f"Product Previous stock {item.quantity}")
                    product.current_stock -= line_item.quantity
                    log.info(
                        f"Product Quantity ordered to subtracy from stock {line_item.quantity}"
                    )
                    log.info(f"product Current stock {product.current_stock}")
                    product.save()
                except Exception as e:
                    log.error(
                        str(
                            "An error occured while decrementing non variant product stock "
                        )
                        + str(e)
                    )

    def set_transaction(self, user, charge, card_number, save_card, time_range):

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
        exchange_rate_fee = ExchangeRate.get_exchange_rate_and_fee(charge)

        if exchange_rate_fee["status"]:
            transaction.exchange_rate = exchange_rate_fee["exchange_rate"]
            transaction.transaction_fee = exchange_rate_fee["transaction_fee"]
        else:
            transaction.exchange_rate = 0.00
            transaction.transaction_fee = 0.00

        credit_card = CreditCard.objects.filter(
            user=user, card_number=card_number
        ).first()
        if credit_card != None:
            transaction.credit_card = credit_card
            transaction.save()
        else:
            if save_card:
                credit_card = CreditCard(
                    user_id=user.id,
                    card_number=card_number,
                    exp_month=charge["payment_method_details"]["card"]["exp_month"],
                    exp_year=charge["payment_method_details"]["card"]["exp_year"],
                    brand=charge["payment_method_details"]["card"]["brand"],
                    name_on_card=charge["billing_details"]["name"],
                )
                credit_card.save()
                print(save_card)
                transaction.credit_card = credit_card
        transaction.save()

    def items_count(self):
        quantity = 0
        for item in self.lineitem_set.all():
            quantity += item.quantity
        return quantity

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


# Create your models here.
class LineItem(models.Model):
    order = models.ForeignKey(Order, default=None, null=True, on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, default=None, null=True, on_delete=models.CASCADE
    )
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
    cost_price = models.DecimalField(
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
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    def item_total(self):
        return self.price

    def buyer_default_address(self):
        return self.user.default_address()
