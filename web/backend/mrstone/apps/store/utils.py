from django.db import models

import typing
import uuid


Category = typing.NewType('Category', models.Model)
ProductImage = typing.NewType('ProductImage', models.Model)


def getCategoryImageLocation(instance: Category, filename: str) -> str:
    image_location = f'store/categories/{instance.slug}.webp'
    return image_location
    
def getProductImageLocation(instance: ProductImage, filename: str) -> str:
    image_id = uuid.uuid4()
    image_location = f'store/products/{instance.product.slug}/{image_id}.webp'
    return image_location
