from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from carts.models import CartItem
from .forms import OrderForm
import datetime
import json
from .models import Order, Payment, OrderProduct
from store.models import Product
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
# Create your views here.

def payments(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])

            payment_method = body['payment_method']
            transID = body.get('transID', '')

            payment = Payment(
                user=request.user,
                payment_id=transID,
                payment_method=payment_method,
                amount_paid=order.order_total,
                status=body['status'],
            )
            payment.save()

            order.payment = payment
            order.is_ordered = True
            order.save()

            cart_items = CartItem.objects.filter(user=request.user)

            for item in cart_items:
                orderproduct = OrderProduct()
                orderproduct.order_id = order.id
                orderproduct.payment = payment
                orderproduct.user_id = request.user.id
                orderproduct.product_id = item.product_id
                orderproduct.quantity = item.quantity
                orderproduct.product_price = item.product.price
                orderproduct.ordered = True
                orderproduct.save()

                cart_item = CartItem.objects.get(id=item.id)
                product_variation = cart_item.variations.all()
                orderproduct = OrderProduct.objects.get(id=orderproduct.id)
                orderproduct.variations.set(product_variation)
                orderproduct.save()

                product = Product.objects.get(id=item.product_id)
                product.stock -= item.quantity
                product.save()

            CartItem.objects.filter(user=request.user).delete()

            mail_subject = "Cảm ơn bạn đã đặt hàng!"
            message = render_to_string('orders/order_received.html', {
                'user': request.user,
                'order': order,
            })
            to_email = request.user.email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            data = {
                'order_number': order.order_number,
                'transID': payment.payment_id,
            }

            return JsonResponse(data)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=400)

def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity
        discount = round(subtotal * 0.10, 2) if subtotal > 1000 else 0

        payment = Payment.objects.get(payment_id=transID) if transID != 'COD' else None
        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': transID,
            'payment': payment,
            'subtotal': subtotal,
            'discount': discount,
        }
        return render(request, 'orders/order_complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')

def place_order(request):
    current_user = request.user

    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    grand_total = 0
    total = 0
    quantity = 0
    discount = 0
    
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity

    
    if total > 1000:
        discount = round(total * 0.10, 2)
        ship = 0 
    elif total > 500:
        ship = 0  
    else:
        ship = 10  

    grand_total = total - discount + ship

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order()
            data.user = current_user
            data.full_name = form.cleaned_data['full_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address = form.cleaned_data['address']
            data.city = form.cleaned_data['city']
            data.district = form.cleaned_data['district']
            data.ward = form.cleaned_data['ward']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.ship = ship
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            current_date = f"{datetime.date.today().day}{datetime.date.today().month}{datetime.date.today().year}"
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)

            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'ship': ship,
                'grand_total': grand_total,
                'discount': discount,
            }
            return render(request, 'orders/payments.html', context)
    else:
        form = OrderForm()

    context = {
        'form': form,
        'cart_items': cart_items,
        'total': total,
        'ship': ship,
        'grand_total': grand_total,
        'discount': discount,
    }
    return render(request, 'store/checkout.html', context)

# def payments(request):
#     if request.method == 'POST':
#         body = json.loads(request.body)
#         try:
#             order = Order.objects.get(
#                 user=request.user, is_ordered=False, order_number=body['orderID'])

#             payment = Payment(
#                 user=request.user,
#                 payment_id=body['transID'],
#                 payment_method=body['payment_method'],
#                 amount_paid=order.order_total,
#                 status=body['status'],
#             )
#             payment.save()

#             order.payment = payment
#             order.is_ordered = True
#             order.save()

#             cart_items = CartItem.objects.filter(user=request.user)

#             for item in cart_items:
#                 orderproduct = OrderProduct()
#                 orderproduct.order_id = order.id
#                 orderproduct.payment = payment
#                 orderproduct.user_id = request.user.id
#                 orderproduct.product_id = item.product_id
#                 orderproduct.quantity = item.quantity
#                 orderproduct.product_price = item.product.price
#                 orderproduct.ordered = True
#                 orderproduct.save()

#             # Clear the cart after saving order products
#             cart_items.delete()

#             return JsonResponse({'status': 'Payment successful'})
#         except Exception as e:
#             return JsonResponse({'status': 'Payment failed', 'error': str(e)})
#     return JsonResponse({'status': 'Invalid request method'})
# chatGPT


# chatGPT

# def place_order(request):
#     current_user = request.user

#     cart_items = CartItem.objects.filter(user=current_user)
#     cart_count = cart_items.count()
#     if cart_count <= 0:
#         return redirect('store')

#     grand_total = 0
#     ship = 0
#     for cart_item in cart_items:
#         total += (cart_item.product.price*cart_item.quantity)
#         quantity += cart_item.quantity
#     ship = (2*total)/100
#     grand_total = total + ship

#     if request.method == 'POST':
#         form = OrderForm(request.POST)
#         if form.is_valid():

#             data = Order()
#             data.user = current_user
#             data.full_name = form.cleaned_data['full_name']
#             data.phone = form.cleaned_data['phone']
#             data.email = form.cleaned_data['email']
#             data.address = form.cleaned_data['address']
#             data.city = form.cleaned_data['city']
#             data.district = form.cleaned_data['district']
#             data.ward = form.cleaned_data['ward']
#             data.order_note = form.cleaned_data['order_note']
#             data.order_total = grand_total
#             data.ship = ship
#             data.ip = request.META.get('REMOTE_ADDR')
#             data.save()

#             dt = int(datetime.date.today().strftime('%d'))
#             mt = int(datetime.date.today().strftime('%m'))
#             yr = int(datetime.date.today().strftime('%Y'))
#             d = datetime.date(dt, mt, yr)
#             current_date = d.strftime("%d%m%Y")
#             order_number = current_date + str(data.id)
#             data.order_number = order_number
#             data.save()
#             return redirect('checkout')
#     else:
#         return redirect('checkout')

