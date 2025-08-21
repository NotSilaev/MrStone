from rest_framework import status
from rest_framework.test import APITestCase

from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.text import slugify

from apps.store.models import Category, Product
from apps.store.serializers import CategorySerializer, ProductSerializer

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
        response = self.client.post(url, data, format='multipart')
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
        response = self.client.patch(url, data, format='json')     
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
        response = self.client.delete(url, format='json')     
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
        response = self.client.post(url, data, format='multipart')
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
        response = self.client.patch(url, data, format='json')     
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
        response = self.client.delete(url, format='json')     
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)     

        # Try to get deleted product
        response = self.client.get(url, format='json')     
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
