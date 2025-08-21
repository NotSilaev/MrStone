from django.db import models
from django.utils.text import slugify
from django_resized import ResizedImageField

from apps.store import utils


class Category(models.Model):
    id = models.BigAutoField(primary_key=True)
    slug = models.SlugField(max_length=100, unique=True)
    title = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)
    image = ResizedImageField(
        upload_to=utils.getCategoryImageLocation,
        force_format='WEBP',
        quality=90,
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'categories'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Product(models.Model):
    id = models.BigAutoField(primary_key=True)
    slug = models.SlugField(max_length=100, unique=True)
    title = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available_quantity = models.IntegerField(default=0, blank=True)

    class Meta:
        db_table = 'products'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ProductImage(models.Model):
    id = models.BigAutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = ResizedImageField(
        upload_to=utils.getProductImageLocation,
        force_format='WEBP',
        quality=90,
        blank=True
    )

    class Meta:
        db_table = 'product_images'
