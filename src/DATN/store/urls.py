from django.urls import path
from . import views

urlpatterns = [
    path('', views.store, name='store'),
    path('category/<slug:category_slug>/',
         views.store, name='products_by_category'),
    path('category/<slug:category_slug>/<slug:product_slug>/',
         views.product_detail, name='product_detail'),
    path('search/', views.search, name='search'),
    path('submit_review/<int:product_id>/', views.submit_review, name='submit_review'),
    path('discounts/', views.discounted_products, name='discounted_products'),
    path('new-products/', views.new_products, name='new_products'),
    path('stat/', views.stat, name='stat'),

]
