from rest_framework import status
from rest_framework.test import APITestCase

from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.text import slugify

from apps.auth.models import User, AuthToken
from apps.auth.utils import hashAuthToken
from apps.store.models import Category, Product, Order
from apps.store.serializers import CategorySerializer, ProductSerializer, OrderSerializer

import uuid
from io import BytesIO
from PIL import Image


def getTestImage():
    bts = BytesIO()
    img = Image.new("RGB", (100, 100))
    img.save(bts, 'jpeg')
    image_id = uuid.uuid4()
    return SimpleUploadedFile(f"test-{image_id}.jpg", bts.getvalue())


class CategoryTests(APITestCase):
    def testCategoryCreation(self):
        url = reverse('category_list')

        data = {
            'title': 'Home decorations',
            'description': 'Everything for home and yard',
            'image': getTestImage(),
        }

        plain_auth_token = str(uuid.uuid4())
        auth_token_hash, auth_token_salt_hex = hashAuthToken(plain_auth_token)
        user = User.objects.create(name='test_user')
        AuthToken.objects.create(
            user=user, token_hash=auth_token_hash, salt_hex=auth_token_salt_hex
        )
        auth_header = f'Bearer {plain_auth_token}'

        response = self.client.post(url, data, format='multipart', HTTP_AUTHORIZATION=auth_header) 
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


    def testCategoryEditing(self):
        # Create category
        data = {'title': 'Garden accessories'}
        serializer = CategorySerializer(data=data)
        if serializer.is_valid():
            serializer.save()

        # Get created category
        category_slug = slugify(data.get('title'), allow_unicode=True)
        url = reverse('category_detail', kwargs={'category_slug': category_slug})
        response = self.client.get(url, format='json')     
        self.assertEqual(response.status_code, status.HTTP_200_OK)     
        
        # Change category data
        data = {
            'title': 'Accessories for garden', 
            'description': 'Everything for garden'
        }

        plain_auth_token = str(uuid.uuid4())
        auth_token_hash, auth_token_salt_hex = hashAuthToken(plain_auth_token)
        user = User.objects.create(name='test_user')
        AuthToken.objects.create(
            user=user, token_hash=auth_token_hash, salt_hex=auth_token_salt_hex
        )
        auth_header = f'Bearer {plain_auth_token}'

        # Request with incorrect auth token
        response = self.client.patch(url, data, format='json', HTTP_AUTHORIZATION=auth_header + 'extra_chars') 
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)          
        
        # Request with correct auth token
        response = self.client.patch(url, data, format='json', HTTP_AUTHORIZATION=auth_header) 
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Get edited category
        category_slug = slugify(data.get('title'), allow_unicode=True)
        url = reverse('category_detail', kwargs={'category_slug': category_slug})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def testCategoryDeletion(self):
        # Create category
        data = {'title': 'Bathroom decorations'}
        serializer = CategorySerializer(data=data)
        if serializer.is_valid():
            serializer.save()

        # Get category
        category_slug = slugify(data.get('title'), allow_unicode=True)
        url = reverse('category_detail', kwargs={'category_slug': category_slug})
        response = self.client.get(url, format='json')     
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Delete category
        plain_auth_token = str(uuid.uuid4())
        auth_token_hash, auth_token_salt_hex = hashAuthToken(plain_auth_token)
        user = User.objects.create(name='test_user')
        AuthToken.objects.create(
            user=user, token_hash=auth_token_hash, salt_hex=auth_token_salt_hex
        )
        auth_header = f'Bearer {plain_auth_token}'

        # Request with incorrect auth token
        response = self.client.delete(url, format='json', HTTP_AUTHORIZATION=auth_header + 'extra_chars') 
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)          
        
        # Request with correct auth token
        response = self.client.delete(url, format='json', HTTP_AUTHORIZATION=auth_header) 
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)   

        # Try to get deleted category
        response = self.client.get(url, format='json')     
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
   
        

class ProductTests(APITestCase):
    def testProductCreation(self):
        category = Category.objects.create(title='Living room decorations')

        url = reverse('product_list')
        data = {
            'title': 'Ornamental flowerpot',
            'description': 'Decorative floor tub made of real concrete',
            'category': category.pk,
            'price': 15_000,
            'available_quantity': 10,
            'images': (getTestImage() for i in range(0, 3))
        }

        plain_auth_token = str(uuid.uuid4())
        auth_token_hash, auth_token_salt_hex = hashAuthToken(plain_auth_token)
        user = User.objects.create(name='test_user')
        AuthToken.objects.create(
            user=user, token_hash=auth_token_hash, salt_hex=auth_token_salt_hex
        )
        auth_header = f'Bearer {plain_auth_token}'

        response = self.client.post(url, data, format='multipart', HTTP_AUTHORIZATION=auth_header) 
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


    def testProductEditing(self):
        category = Category.objects.create(title='Kitchen decorations') 

        # Create product
        data = {
            'title': 'Napkin holder',
            'description': 'Concrete napkin holder',
            'category': category.pk,
            'price': 3000,
        }
        serializer = ProductSerializer(data=data)
        if serializer.is_valid():
            serializer.save()

        # Get created product
        product_slug = slugify(data.get('title'), allow_unicode=True)
        url = reverse('product_detail', kwargs={'product_slug': product_slug})
        response = self.client.get(url, format='json')     
        self.assertEqual(response.status_code, status.HTTP_200_OK)     
        
        # Change product data
        data = {
            'title': 'Oval concrete napkin holder', 
            'description': 'Oval shaped concrete napkin holder',
            'price': 10_000,
            'available_quantity': 20,
        }

        plain_auth_token = str(uuid.uuid4())
        auth_token_hash, auth_token_salt_hex = hashAuthToken(plain_auth_token)
        user = User.objects.create(name='test_user')
        AuthToken.objects.create(
            user=user, token_hash=auth_token_hash, salt_hex=auth_token_salt_hex
        )
        auth_header = f'Bearer {plain_auth_token}'

        # Request with incorrect auth token
        response = self.client.patch(url, data, format='json', HTTP_AUTHORIZATION=auth_header + 'extra_chars') 
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)          
        
        # Request with correct auth token
        response = self.client.patch(url, data, format='json', HTTP_AUTHORIZATION=auth_header) 
        self.assertEqual(response.status_code, status.HTTP_200_OK)  

        # Get edited product
        product_slug = slugify(data.get('title'), allow_unicode=True)
        url = reverse('product_detail', kwargs={'product_slug': product_slug})
        response = self.client.get(url, format='json')     
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def testProductDeletion(self):
        category = Category.objects.create(title='Porch decorations')

        # Create product
        data = {
            'title': 'Concrete vase',
            'description': 'Handmade flower vase made of concrete',
            'category': category.pk,
            'price': 5000,
        }
        serializer = ProductSerializer(data=data)
        if serializer.is_valid():
            serializer.save()

        # Get product
        product_slug = slugify(data.get('title'), allow_unicode=True)
        url = reverse('product_detail', kwargs={'product_slug': product_slug})
        response = self.client.get(url, format='json')     
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Delete product
        plain_auth_token = str(uuid.uuid4())
        auth_token_hash, auth_token_salt_hex = hashAuthToken(plain_auth_token)
        user = User.objects.create(name='test_user')
        AuthToken.objects.create(
            user=user, token_hash=auth_token_hash, salt_hex=auth_token_salt_hex
        )
        auth_header = f'Bearer {plain_auth_token}'

        # Request with incorrect auth token
        response = self.client.delete(url, format='json', HTTP_AUTHORIZATION=auth_header + 'extra_chars') 
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)          
        
        # Request with correct auth token
        response = self.client.delete(url, format='json', HTTP_AUTHORIZATION=auth_header) 
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)     

        # Try to get deleted product
        response = self.client.get(url, format='json')     
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class OrderTests(APITestCase):
    def testOrderCreation(self):
        category = Category.objects.create(title='Home')

        products_to_create = []
        for i in range(5):
            products_to_create.append(
                Product(slug=f'test-{i}', title=f"Test product {i}", category=category, price=1000*i)
            )
        products = Product.objects.bulk_create(products_to_create)

        url = reverse('order_list')

        data = {
            'products': [product.id for product in products],
            'contact': '+7 999 888 77 66',
            'contact_type': 'phone_number'
        }

        response = self.client.post(url, data, format='multipart') 
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


    def testOrderEditing(self):
        category = Category.objects.create(title='Home')

        products_to_create = []
        for i in range(5):
            products_to_create.append(
                Product(slug=f'test-{i}', title=f"Test product {i}", category=category, price=1000*i)
            )
        products = Product.objects.bulk_create(products_to_create)

        data = {
            'products': [product.id for product in products],
            'contact': '+7 999 888 77 66',
            'contact_type': 'phone_number'
        }
        serializer = OrderSerializer(data=data)
        if serializer.is_valid():
            serializer.save()

        url = reverse('order_detail', kwargs={'order_id': serializer.data['id']})

        plain_auth_token = str(uuid.uuid4())
        auth_token_hash, auth_token_salt_hex = hashAuthToken(plain_auth_token)
        user = User.objects.create(name='test_user')
        AuthToken.objects.create(
            user=user, token_hash=auth_token_hash, salt_hex=auth_token_salt_hex
        )
        auth_header = f'Bearer {plain_auth_token}'

        data = {
            'products': [product.id for product in products[:3]],
            'contact': '@NotSilaev',
            'contact_type': 'Telegram'
        }

        # Request with incorrect auth token
        response = self.client.patch(url, data, format='json', HTTP_AUTHORIZATION=auth_header + 'extra_chars') 
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)          
        
        # Request with correct auth token
        response = self.client.patch(url, data, format='json', HTTP_AUTHORIZATION=auth_header) 
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def testOrderDeletion(self):
        category = Category.objects.create(title='Home')

        products_to_create = []
        for i in range(5):
            products_to_create.append(
                Product(slug=f'test-{i}', title=f"Test product {i}", category=category, price=1000*i)
            )
        products = Product.objects.bulk_create(products_to_create)

        data = {
            'products': [product.id for product in products],
            'contact': '+7 999 888 77 66',
            'contact_type': 'phone_number'
        }
        serializer = OrderSerializer(data=data)
        if serializer.is_valid():
            serializer.save()

        url = reverse('order_detail', kwargs={'order_id': serializer.data['id']})

        plain_auth_token = str(uuid.uuid4())
        auth_token_hash, auth_token_salt_hex = hashAuthToken(plain_auth_token)
        user = User.objects.create(name='test_user')
        AuthToken.objects.create(
            user=user, token_hash=auth_token_hash, salt_hex=auth_token_salt_hex
        )
        auth_header = f'Bearer {plain_auth_token}'

        # Request with incorrect auth token
        response = self.client.delete(url, format='json', HTTP_AUTHORIZATION=auth_header + 'extra_chars') 
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)          
        
        # Request with correct auth token
        response = self.client.delete(url, format='json', HTTP_AUTHORIZATION=auth_header) 
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)     

        # Try to get deleted product
        response = self.client.get(url, format='json')     
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
