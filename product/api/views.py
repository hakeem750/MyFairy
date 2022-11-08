from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, filters
from index.helper import Helper, get_data
from product.models import Product
from .serializers import ProductListSerializer, ProductDetailSerializer


class ProductListView(APIView):
    def get(self, request):
        q = request.GET.get("q")
        auth = Helper(request).is_autheticated()
        if auth["status"]:
            if q == "Sanitary Kits":
                product = Prodcut.objects.filter(category=q)
                serializer = ProductListSerializer(product, many=True)

                return Response(
                    {
                        "status": True,
                        "message": "Products fetched successfully",
                        "data": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
            elif q == "Contraceptives":
                product = Prodcut.objects.filter(category=q)
                serializer = ProductListSerializer(product, many=True)

                return Response(
                    {
                        "status": True,
                        "message": "Products fetched successfully",
                        "data": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
            elif q == "Fashion":
                product = Prodcut.objects.filter(category=q)
                serializer = ProductListSerializer(product, many=True)

                return Response(
                    {
                        "status": True,
                        "message": "Products fetched successfully",
                        "data": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
            elif q == "Others":
                product = Prodcut.objects.filter(category=q)
                serializer = ProductListSerializer(product, many=True)

                return Response(
                    {
                        "status": True,
                        "message": "Products fetched successfully",
                        "data": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )

        else:
            return Response(
                {"status": False, "message": "Unathorised"},
                status=status.HTTP_200_OK,
            )


class ProductDetailView(APIView):
    def get(self, request, slug):

        auth = Helper(request).is_autheticated()
        if auth["status"]:
            product = Prodcut.object.get(slug=slug)
            serializer = ProductDetailSerializer(product)
            return Response(
                {
                    "status": True,
                    "message": "Products fetched successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"status": False, "message": "Unathorised"},
                status=status.HTTP_200_OK,
            )
