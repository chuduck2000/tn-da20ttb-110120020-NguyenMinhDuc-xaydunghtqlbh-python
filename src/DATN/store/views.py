from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, ReviewRating
from orders.models import OrderProduct
from category.models import Category
from carts.models import CartItem
from django.db.models import Q
from .forms import ReviewForm
from django.urls import resolve
from carts.views import _cart_id
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse
from .forms import ReviewForm 
from django.contrib import messages 

def store(request, category_slug=None):
    categories = None
    products = None

    if category_slug:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(
            category=categories, is_available=True)
        paginator = Paginator(products, 9)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        paginator = Paginator(products, 9)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()

    context = {
        'products': paged_products,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)


def product_detail(request, category_slug, product_slug):
    # category = get_object_or_404(Category, slug=category_slug)
    # single_product = get_object_or_404(
    #     Product, category=category, slug=product_slug)
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    except Exception as e:
        raise e
    
    if request.user.is_authenticated:
        try:
            orderproduct = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
    else:
        orderproduct = None
        
    reviews = ReviewRating.objects.filter(product_id = single_product.id, status = True)

    context = {
        'single_product': single_product,
        'products': Product.objects.filter(is_available=True),  # Sản phẩm khác
        'orderproduct': orderproduct,
        'in_cart': in_cart,
        'reviews': reviews,
    }
    return render(request, 'store/product_detail.html', context)


def search(request):
    products = []  # Cho danh sách trống
    product_count = 0  # Cho product = 0

    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by(
                '-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count = products.count()

    context = {
        'products': products,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)

def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Cảm ơn bạn! Đánh giá của bạn đã được cập nhật')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Cảm ơn bạn! đánh giá của bạn đã được gửi.')
                return redirect(url)

def discounted_products(request):
    products = Product.objects.filter(promotions__gt=0, is_available=True)
    paginator = Paginator(products, 9)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    product_count = products.count()

    current_path = resolve(request.path_info).url_name
    context = {
        'products': paged_products,
        'product_count': product_count,
        'current_path': current_path,
    }
    return render(request, 'store/discounted_products.html', context)

def new_products(request):

    products = Product.objects.filter(is_available=True).order_by('-created_date')
    paginator = Paginator(products, 9)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    product_count = products.count()

    current_path = resolve(request.path_info).url_name
    context = {
        'products': paged_products,
        'product_count': product_count,
        'current_path': current_path,
    }
    return render(request, 'store/new_products.html', context)

def stat(request):
    return render(request,'store/stat.html')

