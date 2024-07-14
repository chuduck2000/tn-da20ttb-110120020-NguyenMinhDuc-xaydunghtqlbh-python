from django.db import models
from accounts.models import Account
from store.models import Product, Variation
from django.core.validators import MinValueValidator

class Payment(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name='Người dùng')
    payment_id = models.CharField(max_length=100, verbose_name='Mã thanh toán')
    payment_method = models.CharField(max_length=100, verbose_name='Phương thức thanh toán')
    amount_paid = models.CharField(max_length=100, verbose_name='Số tiền đã thanh toán')
    status = models.CharField(max_length=100, verbose_name='Trạng thái')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')

    def __str__(self):
        return self.payment_id

    class Meta:
        verbose_name = 'Thanh toán'
        verbose_name_plural = 'Thanh toán'


class Order(models.Model):
    STATUS = (
        ('New', 'Mới'),
        ('Accepted', 'Đã chấp nhận'),
        ('Completed', 'Hoàn thành'),
        ('Cancelled', 'Đã hủy'),
    )

    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, verbose_name='Người dùng')
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Thanh toán')
    order_number = models.CharField(max_length=50, verbose_name='Số đơn hàng')
    full_name = models.CharField(max_length=50, verbose_name='Họ và tên')
    phone = models.CharField(max_length=50, verbose_name='Số điện thoại')
    email = models.EmailField(max_length=50, verbose_name='Email')
    address = models.CharField(max_length=50, verbose_name='Địa chỉ')
    city = models.CharField(max_length=50, verbose_name='Thành phố')
    district = models.CharField(max_length=50, verbose_name='Quận/Huyện')
    ward = models.CharField(max_length=50, verbose_name='Phường/Xã')
    order_note = models.CharField(max_length=100, blank=True, verbose_name='Ghi chú đơn hàng')
    order_total = models.FloatField(verbose_name='Tổng đơn hàng')
    ship = models.FloatField(verbose_name='Phí vận chuyển')
    status = models.CharField(max_length=10, choices=STATUS, default='New', verbose_name='Trạng thái')
    ip = models.CharField(blank=True, max_length=20, verbose_name='Địa chỉ IP')
    is_ordered = models.BooleanField(default=False, verbose_name='Đã đặt hàng')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Ngày cập nhật')

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = 'Đơn hàng'
        verbose_name_plural = 'Đơn hàng'


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='Đơn hàng')
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Thanh toán')
    user = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name='Người dùng')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Sản phẩm')
    variations = models.ManyToManyField(Variation, blank=True, verbose_name='Biến thể')
    quantity = models.IntegerField(validators=[MinValueValidator(0)], verbose_name='Số lượng')
    product_price = models.FloatField(verbose_name='Giá sản phẩm')
    ordered = models.BooleanField(default=False, verbose_name='Đã đặt hàng')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Ngày cập nhật')

    def __str__(self):
        return self.product.product_name

    class Meta:
        verbose_name = 'Sản phẩm đặt hàng'
        verbose_name_plural = 'Sản phẩm đặt hàng'
