from django.db import models
from django.db.models import Avg, Count
from django.urls import reverse
from django.core.validators import MinValueValidator
from category.models import Category
from accounts.models import Account


class Product(models.Model):
    product_name = models.CharField(max_length=200, unique=True, verbose_name='Tên sản phẩm')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='Slug')
    description = models.TextField(max_length=1000, blank=True, verbose_name='Mô tả')
    price = models.PositiveIntegerField(verbose_name='Giá')
    images = models.ImageField(max_length=200, unique=True, verbose_name='Hình ảnh')
    stock = models.PositiveIntegerField(validators=[MinValueValidator(0)], verbose_name='Tồn kho')  # Ensure value is always >= 0
    is_available = models.BooleanField(default=True, verbose_name='Có sẵn')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Danh mục')
    created_date = models.DateTimeField(auto_now=True, verbose_name='Ngày tạo')
    modified_date = models.DateTimeField(auto_now=True, verbose_name='Ngày sửa đổi')
    promotions = models.PositiveIntegerField(default=0, blank=True, null=True, verbose_name='Khuyến mãi')  # Default value is 0

    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])

    def reduce_stock(self, quantity):
        if self.stock >= quantity:
            self.stock -= quantity
            self.save()
        else:
            raise ValueError("Không đủ hàng trong kho")

    def __str__(self):
        return self.product_name
    
    def averageReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg
    
    def countReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(count=Count('id'))
        count = 0
        if reviews['count'] is not None:
            count = int(reviews['count'])
        return count

    @property
    def is_discounted(self):
        return self.promotions > 0

    class Meta:
        verbose_name = 'Sản phẩm'
        verbose_name_plural = 'Sản phẩm'


class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(variation_category='color', is_active=True)

    def sizes(self):
        return super(VariationManager, self).filter(variation_category='size', is_active=True)

variation_category_choice = (
    ('color', 'Màu sắc'),
    ('size', 'Kích thước'),
)


class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Sản phẩm')
    variation_category = models.CharField(max_length=100, choices=variation_category_choice, verbose_name='Loại biến thể')
    variation_value = models.CharField(max_length=100, verbose_name='Giá trị biến thể')
    is_active = models.BooleanField(default=True, verbose_name='Hoạt động')
    created_date = models.DateTimeField(auto_now=True, verbose_name='Ngày tạo')

    objects = VariationManager()

    def __str__(self):
        return self.variation_value

    class Meta:
        verbose_name = 'Biến thể'
        verbose_name_plural = 'Biến thể'


class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Sản phẩm')
    user = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name='Người dùng')
    subject = models.CharField(max_length=100, blank=True, verbose_name='Chủ đề')
    review = models.TextField(max_length=500, blank=True, verbose_name='Đánh giá')
    rating = models.FloatField(validators=[MinValueValidator(0)], verbose_name='Điểm đánh giá')
    ip = models.CharField(max_length=20, blank=True, verbose_name='Địa chỉ IP')
    status = models.BooleanField(default=True, verbose_name='Trạng thái')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Ngày cập nhật')

    def __str__(self):
        return self.subject

    class Meta:
        verbose_name = 'Đánh giá'
        verbose_name_plural = 'Đánh giá'
