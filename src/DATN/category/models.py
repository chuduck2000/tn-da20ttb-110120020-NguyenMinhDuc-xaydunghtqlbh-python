from django.db import models
from django.urls import reverse

# Create your models here.


class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True, verbose_name='Tên loại')
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(max_length=255, unique=True, verbose_name='Mô tả')
    cat_image = models.ImageField(upload_to='photos/categories', blank=True, verbose_name='Hình ảnh')

    class Meta:
        db_table = ''
        managed = True
        verbose_name = 'Loại sản phẩm'
        verbose_name_plural = 'Loại sản phẩm'

    def get_url(self):
        return reverse('products_by_category', args=[self.slug])

    def __str__(self):
        return self.category_name
