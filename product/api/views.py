import stripe
from django_countries import countries
from django.db.models import Q
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from index.helper import Helper, get_data
from index.model.user import User
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    CreateAPIView,
    UpdateAPIView,
    DestroyAPIView,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from .serializers import (
    ProductSerializer,
    OrderSerializer,
    ProductDetailSerializer,
    AddressSerializer,
    CreditCardSerializer,
    BankSerializer,
    PaymentSerializer,
    VariationDetailSerializer,
    RefundSerializer,
)
from product.models import (
    Product,
    OrderProduct,
    Order,
    Address,
    Payment,
    Coupon,
    Refund,
    # UserProfile,
    Variation,
    Bank,
    CreditCard,
    ProductVariation,
    Refunds,
)


class RefundTransactions(object):
    def __init__(self, charge_id, refund_id=""):

        self.charge_id = charge_id
        self.refund_id = refund_id

    def create_refund(self):
        response = stripe.Refund.create(
            charge=self.charge_id,
        )
        return response

    def retrieve_refund(self):
        response = stripe.Refund.retrieve(
            self.refund_id,
        )
        return response

    def update_refund(self, metadata):
        response = stripe.Refund.modify(
            self.refund_id,
            metadata=metadata,
        )
        return response

    def cancel_refund(self):
        response = stripe.Refund.cancel(
            self.refund_id,
        )
        return response

    def list_refunds(self, q, data_obj, singlecharge, limit, source="local_db"):
        if singlecharge:
            if source == "stripe":
                response = stripe.Refund.list(charge=self.charge_id, limit=limit)
                return response
            elif source == "local_db":
                if type(int(q)) == int:
                    if data_obj == "":
                        refunds = Refunds.objects.filter(customer=q)
                        serializer = RefundSerializer(refunds, many=True)
                    else:
                        refunds = Refunds.objects.filter(
                            customer=q,
                            amount=data_obj.amount,
                            currency=data_obj.currency,
                            status=data_obj.status,
                            created_at__range=[data_obj.start_date, data_obj.end_date],
                        )
                        serializer = RefundSerializer(refunds, many=True)
                return serializer.data
        else:
            if source == "stripe":
                if q == "":
                    response = stripe.Refund.list(limit=limit)
                    return response

            if source == "local_db":
                if q == "":
                    refunds = Refunds.objects.all()[:limit]
                    serializer = RefundSerializer(refunds, many=True)
                    return serializer.data


class UserIDView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({"userID": request.user.id}, status=HTTP_200_OK)


# class ProductListView(ListAPIView):
#     permission_classes = (AllowAny,)
#     serializer_class = ProductSerializer
#     queryset = Product.objects.all()


class ProductListView(APIView):
    def get(self, request):
        q = request.GET.get("category")
        prod = Product.objects.filter(category=q)
        serializer = ProductSerializer(prod, many=True)
        return Response({"status": True, "data": serializer.data})


class ProductDetailView(RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ProductDetailSerializer
    queryset = Product.objects.all()


class BankView(APIView):
    def post(self, request, *args, **kwargs):
        auth = Helper(request).is_autheticated()
        if auth["status"]:
            user = User.objects.filter(id=auth["payload"]["id"]).first()
            data = request.data
            serializer = BankSerializer(data=data)

            if serializer.is_valid():
                serializer.save(user=user)

                return Response(
                    {"status": True, "data": serializer.data},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"status": False, "message": serializer.errors},
                    status=status.HTTP_200_OK,
                )
        else:
            return Response(
                {"status": False, "message": "Unathorised"},
                status=status.HTTP_200_OK,
            )

    def get(self, request, *args, **kwargs):

        auth = Helper(request).is_autheticated()
        if auth["status"]:
            user = User.objects.filter(id=auth["payload"]["id"]).first()
            bank = get_object_or_404(Bank, user=user)
            serializer = BankSerializer(bank)
            return Response(
                {"status": True, "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"status": False, "message": "Unathorised"},
                status=status.HTTP_200_OK,
            )

    def put(self, request, *args, **kwargs):
        auth = Helper(request).is_autheticated()
        if auth["status"]:
            user = User.objects.filter(id=auth["payload"]["id"]).first()
            data = request.data
            bank = get_object_or_404(Bank, user=user)
            serializer = BankSerializer(data=data, partial=True)
            if serializer.is_valid():
                serializer.instance = bank
                serializer.save()

                return Response(
                    {"status": True, "data": serializer.data},
                    status=status.HTTP_200_OK,
                )

            else:
                return Response(
                    {"status": False, "message": "Unathorised"},
                    status=status.HTTP_200_OK,
                )

        else:
            return Response(
                {"status": False, "message": "Unathorised"},
                status=status.HTTP_200_OK,
            )

    def delete(self, request, *args, **kwargs):
        auth = Helper(request).is_autheticated()
        if auth["status"]:
            user = User.objects.filter(id=auth["payload"]["id"]).first()

            bank = get_object_or_404(Bank, user=user)
            bank.delete()
            return Response(
                {"status": True, "message": "Data has been deleted"},
                status=status.HTTP_204_NO_CONTENT,
            )

        else:
            return Response(
                {"status": False, "message": "Unathorised"},
                status=status.HTTP_200_OK,
            )


class CreditcardView(APIView):
    def post(self, request, *args, **kwargs):
        auth = Helper(request).is_autheticated()
        if auth["status"]:
            user = User.objects.filter(id=auth["payload"]["id"]).first()
            data = request.data
            serializer = CreditCardSerializer(data=data)

            if serializer.is_valid():
                serializer.save(user=user)

                return Response(
                    {"status": True, "data": serializer.data},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"status": False, "message": serializer.errors},
                    status=status.HTTP_200_OK,
                )
        else:
            return Response(
                {"status": False, "message": "Unathorised"},
                status=status.HTTP_200_OK,
            )

    def get(self, request, *args, **kwargs):
        auth = Helper(request).is_autheticated()
        if auth["status"]:
            user = User.objects.filter(id=auth["payload"]["id"]).first()
            crd = get_object_or_404(CreditCard, user=user)
            serializer = CreditCardSerializer(crd)
            return Response(
                {"status": True, "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"status": False, "message": "Unathorised"},
                status=status.HTTP_200_OK,
            )

    def put(self, request, *args, **kwargs):
        auth = Helper(request).is_autheticated()
        if auth["status"]:
            user = User.objects.filter(id=auth["payload"]["id"]).first()
            data = request.data
            crd = get_object_or_404(CreditCard, user=user)
            serializer = CreditCardSerializer(data=data, partial=True)
            if serializer.is_valid():
                serializer.instance = crd
                serializer.save()

                return Response(
                    {"status": True, "data": serializer.data},
                    status=status.HTTP_200_OK,
                )

            else:
                return Response(
                    {"status": False, "message": "Unathorised"},
                    status=status.HTTP_200_OK,
                )
        else:
            return Response(
                {"status": False, "message": "Unathorised"},
                status=status.HTTP_200_OK,
            )

    def delete(self, request, *args, **kwargs):
        auth = Helper(request).is_autheticated()
        if auth["status"]:
            user = User.objects.filter(id=auth["payload"]["id"]).first()
            crd = get_object_or_404(CreditCard, user=user)
            crd.delete()
            return Response(
                {"status": True, "message": "Data has been deleted"},
                status=status.HTTP_204_NO_CONTENT,
            )
        else:
            return Response(
                {"status": False, "message": "Unathorised"},
                status=status.HTTP_200_OK,
            )


class OrderQuantityUpdateView(APIView):
    def post(self, request, *args, **kwargs):
        auth = Helper(request).is_autheticated()
        if auth["status"]:
            user = User.objects.filter(id=auth["payload"]["id"]).first()
            slug = request.data.get("slug", None)
            if slug is None:
                return Response({"message": "Invalid data"}, status=HTTP_200_OK)

            product = get_object_or_404(Product, slug=slug)
            order_qs = Order.objects.filter(user=user, ordered=False)
            if order_qs.exists():
                order = order_qs[0]
                # check if the order product is in the order
                if order.products.filter(product__slug=product.slug).exists():
                    order_product = OrderProduct.objects.filter(
                        product=product, user=user, ordered=False
                    )[0]
                    if order_product.quantity > 1:
                        order_product.quantity -= 1
                        order_product.save()
                    else:
                        order.products.remove(order_product)
                    return Response(status=HTTP_200_OK)
                else:
                    return Response(
                        {"message": "This item was not in your cart"},
                        status=HTTP_200_OK,
                    )
            else:
                return Response(
                    {"message": "You do not have an active order"},
                    status=HTTP_200_OK,
                )
        else:
            return Response(
                {"status": False, "message": "Unathorised"},
                status=status.HTTP_200_OK,
            )


# class OrderItemDeleteView(DestroyAPIView):
#     permission_classes = (IsAuthenticated,)
#     queryset = OrderItem.objects.all()


class OrderItemDeleteView(APIView):
    def delete(self, request, pk, *args, **kwargs):

        auth = Helper(request).is_autheticated()
        if auth["status"]:
            prod = OrderProduct.objects.get(pk=pk)
            prod.delete()
            return Response(
                {"status": True, "message": "Product has been removed"},
                status=status.HTTP_204_NO_CONTENT,
            )

        else:
            return Response(
                {"status": False, "message": "Unathorised"},
                status=status.HTTP_200_OK,
            )


class AddToCartView(APIView):
    def post(self, request, *args, **kwargs):
        auth = Helper(request).is_autheticated()
        if auth["status"]:
            user = User.objects.filter(id=auth["payload"]["id"]).first()

            slug = request.data.get("slug", None)
            variations = request.data.get("variations", [])
            qty = request.data.get("quantity", 1)
            if slug is None:
                return Response({"message": "Invalid request"}, status=HTTP_200_OK)

            product = get_object_or_404(Product, slug=slug)

            minimum_variation_count = Variation.objects.filter(product=product).count()
            if len(variations) < minimum_variation_count:
                return Response(
                    {"message": "Please specify the required variation types"},
                    status=HTTP_200_OK,
                )

            order_product_qs = OrderProduct.objects.filter(
                product=product, user=user, ordered=False
            )
            for v in variations:
                order_product_qs = order_product_qs.filter(
                    Q(product_variations__exact=v)
                )

            if order_product_qs.exists():
                order_product = order_product_qs.first()
                order_product.quantity = qty
                order_product.save()
            else:
                order_product = OrderProduct.objects.create(
                    product=product, user=user, ordered=False
                )
                order_product.product_variations.add(*variations)
                order_product.quantity = qty
                order_product.save()

            order_qs = Order.objects.filter(user=user, ordered=False)
            if order_qs.exists():
                order = order_qs[0]
                if order.products.filter(product__id=order_product.product.id).exists():
                    order.products.remove(order_product)
                    order.save()
                    return Response(
                        {"status": True, "message": "Product removed to cart"},
                        status=HTTP_200_OK,
                    )
                else:
                    order.products.add(order_product)
                    order.save()
                    return Response(
                        {"status": True, "message": "Product added from cart"},
                        status=HTTP_200_OK,
                    )

            else:
                ordered_date = timezone.now()
                order = Order.objects.create(user=user, ordered_date=ordered_date)
                order.products.add(order_product)
                order.save()
                return Response(
                    {"status": True, "message": "Product added to cart"},
                    status=HTTP_200_OK,
                )
        else:
            return Response(
                {"status": False, "message": "Unathorised"},
                status=status.HTTP_200_OK,
            )


# class OrderDetailView(RetrieveAPIView):
#     serializer_class = OrderSerializer
#     permission_classes = (IsAuthenticated,)

#     def get_object(self):
#         try:
#             order = Order.objects.get(user=self.request.user, ordered=False)
#             return order
#         except ObjectDoesNotExist:
#             raise Http404("You do not have an active order")
#             # return Response({"message": "You do not have an active order"}, status=HTTP_200_OK)


class OrderDetailView(APIView):
    def get(self, request, *args, **kwargs):
        auth = Helper(request).is_autheticated()

        if auth["status"]:
            user = User.objects.filter(id=auth["payload"]["id"]).first()
            order = Order.objects.filter(user=user, ordered=False)
            if order.exists():

                serializer = OrderSerializer(order.first())
                return Response(
                    {"status": True, "data": serializer.data},
                    status=status.HTTP_200_OK,
                )

            else:
                return Response(
                    {"status": False, "message": "You do not have an active order"},
                    status=status.HTTP_200_OK,
                )
        else:
            return Response(
                {"status": False, "message": "Unathorised"},
                status=status.HTTP_200_OK,
            )


class PaymentView(APIView):
    def post(self, request, *args, **kwargs):
        auth = Helper(request).is_autheticated()
        if auth["status"]:
            user = User.objects.filter(id=auth["payload"]["id"]).first()

            order = Order.objects.get(user=user, ordered=False)
            token = request.data.get("stripeToken")
            billing_address_id = request.data.get("selectedBillingAddress")
            shipping_address_id = request.data.get("selectedShippingAddress")

            billing_address = Address.objects.get(id=billing_address_id)
            shipping_address = Address.objects.get(id=shipping_address_id)
            time_sent = get_timezone_datetime()

            if user.stripe_customer_id != "" and user.stripe_customer_id is not None:
                customer = stripe.Customer.retrieve(user.stripe_customer_id)
                customer.sources.create(source=token)

            else:
                customer = stripe.Customer.create(
                    email=user.email,
                )
                customer.sources.create(source=token)
                user.stripe_customer_id = customer["id"]
                user.one_click_purchasing = True
                user.save()

            amount = int(order.get_total() * 100)

            try:

                # charge the customer because we cannot charge the token more than once
                charge = stripe.Charge.create(
                    amount=amount,  # cents
                    currency="usd",
                    customer=user.stripe_customer_id,
                )
                time_arrived = get_timezone_datetime()
                time_range = [time_sent, time_arrived]
                # charge once off on the token
                # charge = stripe.Charge.create(
                #     amount=amount,  # cents
                #     currency="usd",
                #     source=token
                # )

                # create the payment
                payment = Payment()
                payment.stripe_charge_id = charge["id"]
                payment.user = user
                payment.amount = order.get_total()
                payment.save()

                # assign the payment to the order

                order_products = order.items.all()
                order_products.update(ordered=True)
                for item in order_products:
                    item.save()

                order.ordered = True
                order.payment = payment
                order.billing_address = billing_address
                order.shipping_address = shipping_address
                # order.ref_code = create_ref_code()
                order_number = order.save()
                order.set_line_items_from_cart(cart, order_number, user)
                order.set_transaction(user, charge, time_range)

                return Response(status=HTTP_200_OK)

            except stripe.error.CardError as e:
                body = e.json_body
                err = body.get("error", {})
                return Response(
                    {"message": f"{err.get('message')}"}, status=HTTP_200_OK
                )

            except stripe.error.RateLimitError as e:
                # Too many requests made to the API too quickly
                messages.warning(self.request, "Rate limit error")
                return Response({"message": "Rate limit error"}, status=HTTP_200_OK)

            except stripe.error.InvalidRequestError as e:
                print(e)
                # Invalid parameters were supplied to Stripe's API
                return Response({"message": "Invalid parameters"}, status=HTTP_200_OK)

            except stripe.error.AuthenticationError as e:
                # Authentication with Stripe's API failed
                # (maybe you changed API keys recently)
                return Response({"message": "Not authenticated"}, status=HTTP_200_OK)

            except stripe.error.APIConnectionError as e:
                # Network communication with Stripe failed
                return Response({"message": "Network error"}, status=HTTP_200_OK)

            except stripe.error.StripeError as e:
                # Display a very generic error to the user, and maybe send
                # yourself an email
                return Response(
                    {
                        "message": "Something went wrong. You were not charged. Please try again."
                    },
                    status=HTTP_200_OK,
                )

            except Exception as e:
                # send an email to ourselves
                return Response(
                    {"message": "A serious error occurred. We have been notifed."},
                    status=HTTP_200_OK,
                )

            return Response({"message": "Invalid data received"}, status=HTTP_200_OK)
        else:
            return Response(
                {"status": False, "message": "Unathorised"},
                status=status.HTTP_200_OK,
            )


class AddCouponView(APIView):
    def post(self, request, *args, **kwargs):
        auth = Helper(request).is_autheticated()
        if auth["status"]:
            user = User.objects.filter(id=auth["payload"]["id"]).first()
            code = request.data.get("code", None)
            if code is None:
                return Response(
                    {"message": "Invalid data received"}, status=HTTP_200_OK
                )
            order = Order.objects.get(user=user, ordered=False)
            coupon = get_object_or_404(Coupon, code=code)
            order.coupon = coupon
            order.save()
            return Response(status=HTTP_200_OK)
        else:
            return Response(
                {"status": False, "message": "Unathorised"},
                status=status.HTTP_200_OK,
            )


class CountryListView(APIView):
    def get(self, request):
        return Response(countries, status=HTTP_200_OK)


class AddressListView(APIView):
    def get(self, request):
        auth = Helper(request).is_autheticated()
        address_type = request.query_params.get("address_type", None)
        if auth["status"]:
            user = User.objects.filter(id=auth["payload"]["id"]).first()
            address = Address.objects.filter(user=user, address_type=address_type)
            serializer = AddressSerializer(address, many=True)

            return Response(
                {
                    "status": True,
                    "message": "Address Feteched Successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"status": False, "message": "Unathorised"},
                status=status.HTTP_200_OK,
            )


class AddressCreateView(APIView):
    def post(self, request):
        auth = Helper(request).is_autheticated()
        if auth["status"]:
            user = User.objects.filter(id=auth["payload"]["id"]).first()
            data = get_data(request.POST)
            serializer = AddressSerializer(data=data)
            if serializer.is_valid():
                serializer.save(user=user)

                return Response(
                    {
                        "status": True,
                        "message": "Address Feteched Successfully",
                        "data": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"status": False, "message": serializer.errors},
                    status=status.HTTP_200_OK,
                )
        else:
            return Response(
                {"status": False, "message": "Unathorised"},
                status=status.HTTP_200_OK,
            )


# class AddressUpdateView(UpdateAPIView):
#     permission_classes = (IsAuthenticated,)
#     serializer_class = AddressSerializer
#     queryset = Address.objects.all()


class AddressUpdateView(APIView):
    def put(self, request, pk):
        auth = Helper(request).is_autheticated()
        if auth["status"]:
            data = get_data(request.POST)
            address = get_object_or_404(Address, pk=pk)
            serializer = AddressSerializer(data=data, partial=True)

            if serializer.is_valid():
                serializer.instance = address
                serializer.save()

                return Response(
                    {
                        "status": True,
                        "message": "Address Feteched Successfully",
                        "data": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"status": False, "message": serializer.errors},
                    status=status.HTTP_200_OK,
                )
        else:
            return Response(
                {"status": False, "message": "Unathorised"},
                status=status.HTTP_200_OK,
            )


class AddressDeleteView(APIView):
    def delete(self, request, pk, *args, **kwargs):

        auth = Helper(request).is_autheticated()
        if auth["status"]:
            prod = Address.objects.get(pk=pk)
            prod.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        else:
            return Response(
                {"status": False, "message": "Unathorised"},
                status=status.HTTP_200_OK,
            )


# class PaymentListView(ListAPIView):
#     permission_classes = (IsAuthenticated,)
#     serializer_class = PaymentSerializer

#     def get_queryset(self):
#         return Payment.objects.filter(user=self.request.user)


class PaymentListView(APIView):
    def put(self, request):
        auth = Helper(request).is_autheticated()
        if auth["status"]:
            user = User.objects.filter(id=auth["payload"]["id"]).first()
            p = Payment.objects.filter(user=user)
            serializer = PaymentSerializer(p, many=True)
            return Response(
                {
                    "status": True,
                    "message": "Address Feteched Successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        else:
            return Response(
                {"status": False, "message": "Unathorised"},
                status=status.HTTP_200_OK,
            )
