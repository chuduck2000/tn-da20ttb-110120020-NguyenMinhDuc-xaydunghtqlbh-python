from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class MyAccountManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if not email:
            raise ValueError('User must have an email address')

        if not username:
            raise ValueError('User must have an username')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
        )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)
        return user


class Account(AbstractBaseUser):
    username = models.CharField(max_length=50, unique=True, verbose_name='Tên người dùng')
    email = models.EmailField(max_length=50, unique=True, verbose_name='Email')
    phone_number = models.CharField(max_length=50, blank=True, null=True, verbose_name='Số điện thoại')

    date_joined = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tham gia')
    last_login = models.DateTimeField(auto_now_add=True, verbose_name='Lần đăng nhập cuối')
    is_admin = models.BooleanField(default=False, verbose_name='Là quản trị viên')
    is_staff = models.BooleanField(default=False, verbose_name='Là nhân viên')
    is_active = models.BooleanField(default=False, verbose_name='Hoạt động')
    is_superadmin = models.BooleanField(default=False, verbose_name='Là quản trị tối cao')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = MyAccountManager()
    
    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True
        
    class Meta:
        verbose_name = 'Tài khoản'
        verbose_name_plural = 'Tài khoản'


class UserProfile(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE, verbose_name='Người dùng')
    address = models.CharField(blank=True, max_length=100, verbose_name='Địa chỉ')
    profile_picture = models.ImageField(blank=True, upload_to='userprofile', verbose_name='Ảnh đại diện')

    city = models.CharField(blank=True, max_length=100, verbose_name='Thành phố')
    district = models.CharField(blank=True, max_length=100, verbose_name='Quận/Huyện')
    ward = models.CharField(blank=True, max_length=100, verbose_name='Phường/Xã')

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'Thông tin người dùng'
        verbose_name_plural = 'Thông tin người dùng'