from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import status

from django.http import Http404
from django.db.utils import IntegrityError
from django.utils.text import slugify
from django.db import transaction

from utils import makeResponseData, makeModelFilterKwargs

from apps.auth.access import checkAuthToken
from apps.store.models import Category, Product, ProductImage, Order
from apps.store.serializers import CategorySerializer, ProductSerializer, OrderSerializer
from apps.store.schemas import ProductListOffsetScheme

import json
import uuid
from pydantic import ValidationError


class CategoryList(APIView):
    def get(self, request: Request) -> Response:
        categories = Category.objects.all()
        serialized_categories = CategorySerializer(categories, many=True).data
        response_data = makeResponseData(
            status=200,
            message='OK',
            details={'categories': serialized_categories}
        )
        return Response(response_data, status=status.HTTP_200_OK)

    @checkAuthToken
    def post(self, request: Request) -> Response:
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            response_data = makeResponseData(
                status=201,
                message='Created',
                details={'category': serializer.data}
            )
            return Response(response_data, status=status.HTTP_201_CREATED)


class CategoryDetail(APIView):
    def getObject(self, category_slug: str) -> Category:
        try:
            return Category.objects.get(slug=category_slug)
        except Category.DoesNotExist:
            raise Http404

    def get(self, request: Request, category_slug: str) -> Response:
        category = self.getObject(category_slug)
        serialized_category = CategorySerializer(category).data
        response_data = makeResponseData(
            status=200,
            message='OK',
            details={'category': serialized_category}
        )
        return Response(response_data, status=status.HTTP_200_OK)

    @checkAuthToken
    def patch(self, request: Request, category_slug: str) -> Response:
        category = self.getObject(category_slug)
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            response_data = makeResponseData(
                status=200,
                message='OK',
                details={'category': serializer.data}
            )
            return Response(response_data, status=status.HTTP_200_OK)

    @checkAuthToken
    def delete(self, request: Request, category_slug: str) -> Response:
        category = self.getObject(category_slug)
        category.delete()
        response_data = makeResponseData(status=204, message='No Content')
        return Response(response_data, status=status.HTTP_204_NO_CONTENT)


class ProductList(APIView):
    def get(self, request: Request) -> Response:
        offset = request.GET.get('offset')
        if offset:
            try:
                offset = json.loads(offset)
                offset = ProductListOffsetScheme(**offset)
            except (TypeError, json.decoder.JSONDecodeError):
                response_data = {
                    'errors': [makeResponseData(status=400, message='Offset must be a valid JSON string')]
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            except ValidationError as e:
                response_data = {
                    'errors': [makeResponseData(status=400, message='Offset validation error', details=e.errors())]
                }
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        else:
            offset = ProductListOffsetScheme(start=0, end=5)
        
        products = Product.objects.all()[offset.start:offset.end]
        serialized_products = ProductSerializer(products, many=True).data

        response_data = makeResponseData(
            status=200,
            message='OK',
            details={'products': serialized_products}
        )
        return Response(response_data, status=status.HTTP_200_OK)

    @checkAuthToken
    def post(self, request: Request) -> Response:
        data = request.data

        with transaction.atomic():
            serializer = ProductSerializer(data=data)
            if serializer.is_valid(raise_exception=True):
                product = serializer.save()

            images = request.FILES.getlist('images')
            for image in images:
                ProductImage.objects.create(
                    product=product,
                    image=image
                )

            response_data = makeResponseData(
                status=201,
                message='Created',
                details={'product': serializer.data}
            )
            return Response(response_data, status=status.HTTP_201_CREATED)


class ProductDetail(APIView):
    def getObject(self, product_slug: str) -> Product:
        try:
            return Product.objects.get(slug=product_slug)
        except Product.DoesNotExist:
            raise Http404

    def get(self, request: Request, product_slug: str) -> Response:
        product = self.getObject(product_slug)
        serialized_product = ProductSerializer(product).data
        response_data = makeResponseData(
            status=200,
            message='OK',
            details={'product': serialized_product}
        )
        return Response(response_data, status=status.HTTP_200_OK)

    @checkAuthToken
    def patch(self, request: Request, product_slug: str) -> Response:
        product = self.getObject(product_slug)
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            response_data = makeResponseData(
                status=200,
                message='OK',
                details={'product': serializer.data}
            )
            return Response(response_data, status=status.HTTP_200_OK)

    @checkAuthToken
    def delete(self, request: Request, product_slug: str) -> Response:
        product = self.getObject(product_slug)
        product.delete()
        response_data = makeResponseData(status=204, message='No Content')
        return Response(response_data, status=status.HTTP_204_NO_CONTENT)


class OrderList(APIView):
    def get(self, request: Request) -> Response:
        orders = Order.objects.all()

        filters = ('contact', 'contact_type')
        query_params = request.query_params
        filter_kwargs = makeModelFilterKwargs(filters, query_params)
        if filter_kwargs:
            orders = orders.filter(**filter_kwargs)

        serialized_orders = OrderSerializer(orders, many=True).data
        response_data = makeResponseData(
            status=200,
            message='OK',
            details={'orders': serialized_orders}
        )
        return Response(response_data, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            response_data = makeResponseData(
                status=201,
                message='Created',
                details={'order': serializer.data}
            )
            return Response(response_data, status=status.HTTP_201_CREATED)


class OrderDetail(APIView):
    def getObject(self, order_id: str) -> Order:
        try:
            order_id = uuid.UUID(order_id).hex
            return Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            raise Http404

    def get(self, request: Request, order_id: str) -> Response:
        order = self.getObject(order_id)
        serialized_order = OrderSerializer(order).data
        response_data = makeResponseData(
            status=200,
            message='OK',
            details={'order': serialized_order}
        )
        return Response(response_data, status=status.HTTP_200_OK)

    @checkAuthToken
    def patch(self, request: Request, order_id: str) -> Response:
        order = self.getObject(order_id)
        serializer = OrderSerializer(order, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            response_data = makeResponseData(
                status=200,
                message='OK',
                details={'order': serializer.data}
            )
            return Response(response_data, status=status.HTTP_200_OK)

    @checkAuthToken
    def delete(self, request: Request, order_id: str) -> Response:
        order = self.getObject(order_id)
        order.delete()
        response_data = makeResponseData(status=204, message='No Content')
        return Response(response_data, status=status.HTTP_204_NO_CONTENT)
