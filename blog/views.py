from django.contrib import messages

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
import json

from django.urls import reverse_lazy

from .models import *

from .forms import CreateUserForm, AccountForm

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.views.generic import FormView
from django.contrib.auth.views import LogoutView, LoginView
from django.contrib.auth import logout

from django.db.models import Q

from django.db.models import Count


import random

from taggit.models import Tag

from django.contrib.auth.decorators import login_required






def homePage(request, tag_slug=None):
    products = Product.objects.filter(status='published')
    tag =None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        products = Product.objects.filter(tags__in=[tag])

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, coplete=False)

        order_items_count = order.get_total_products

    else:
        order_items_count = 0


    # Paginate Site With 6 Items Per A Page
    paginator = Paginator(products, 8)
    page = request.GET.get('page')

    # Post Of Certain Page
    try:
        products = paginator.page(page)

    # If Page Not Integer
    except PageNotAnInteger:
        products = paginator.page(1)

    # If Page NOt Exists
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    context = {
        'products': products,
        'page': page,
        'order_items_count':  order_items_count,
    }
    return render(request, 'blog/partials/content.html', context)


def productDetail(request, pk, slug):
    product = get_object_or_404(Product, id=pk, slug=slug, status='published')

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, coplete=False)
        order_items_count = order.get_total_products

        user_ip = request.user.customer.ip_address
        if user_ip not in product.hits.all():
            product.hits.add(user_ip)
    else:
        order_items_count = 0

    product_tags = product.tags.values_list('id', flat=True)
    similar_products = Product.objects.filter(tags__in=product_tags, status='published').exclude(id=product.id)
    # print(similar_products)
    similar_products = similar_products.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]
    context = {
        'product': product,
        'similar_products': similar_products,
        'order_items_count': order_items_count,

    }
    return render(request, 'blog/partials/product_detail.html', context)
def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, coplete=False)
        items = OrderItem.objects.filter(order=order)
        delivery = Delivery.objects.filter(active=True)

        # Product Charges (static for now or can be dynamic)
        product_charges = 100  # Example static charge
        total_price = order.get_total_price  # No parentheses here as it's a property
        total_price_with_charges = total_price + product_charges

        # Default shipping fee (3000)
        shipping_fee = 3000

        if request.method == "POST":
            now = timezone.now()
            code = request.POST['code']
            
            # Coupon logic removed as requested

        order_items_count = order.get_total_products

        context = {
            'items': items,
            'order': order,
            'order_items_count': order_items_count,
            'delivery': delivery,
            'product_charges': product_charges,
            'total_price_with_charges': total_price_with_charges,  # Add this to pass the new total
            'shipping_fee': shipping_fee  # Pass the default shipping fee to the template
        }

        return render(request, 'blog/partials/cart.html', context)


# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Order, OrderItem

def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, coplete=False)
        items = OrderItem.objects.filter(order=order)

        # Check if customer has filled in all necessary information
        if not (customer.first_name and customer.last_name and customer.address and customer.email and customer.phone):
            messages.error(request, 'Complete your personal information')
            return redirect('blog:cart')

    else:
        items = []
        order = {
            'get_total_price': 0,
            'get_total_products': 0,
        }
        return redirect('blog:login')

    # Adding shipping fee
    shipping_fee = 2  # Example shipping fee

    # Calculate total price including shipping fee
    total_price = order.get_total_price + shipping_fee
    
    if not order:
        # Handle case when order is not available
        return redirect('blog:cart')
    
    # Use order details and customer info for payment
    order_total = order.get_last_total_price
    customer_email = customer.email
    customer_phone = customer.phone
    customer_address = customer.address
    customer_name = f"{customer.first_name} {customer.last_name}"
    
    products_list = ', '.join([f"{item.product.title} x {item.quantity}" for item in items])
    
    
    
    context = {
        'items': items,
        'order': order,
        'customer': customer,
        'shipping_fee': shipping_fee,
        'total_price': total_price,
        'order_total': order_total,
        'customer_email': customer_email,
        'customer_name': customer_name,
        'products_list': products_list,
        'customer_phone': customer_phone,
        'customer_address': customer_address,
        'tx_ref': f"txref-{random.randint(100000, 999999)}",
    }

    return render(request, 'blog/partials/checkout.html', context)
print("items")


# @login_required
# def payment(request):
#     customer = request.user.customer
#     order, created = Order.objects.get_or_create(customer=customer, coplete=False)

    
    # if not order:
    #     # Handle case when order is not available
    #     return redirect('blog:cart')
    
    # # Use order details and customer info for payment
    # order_total = order.get_last_total_price
    # customer_email = customer.email
    # customer_phone = customer.phone
    # customer_address = customer.address
    # customer_name = f"{customer.first_name} {customer.last_name}"

#     context = {
        # 'order_total': order_total,
        # 'customer_email': customer_email,
        # 'customer_name': customer_name,
        # 'customer_phone': customer_phone,
        # 'customer_address': customer_address,
        # 'tx_ref': f"txref-{random.randint(100000, 999999)}",  # Generate a unique reference for the transaction
#     }
    
#     return render(request, 'blog/partials/payment.html', context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=request.user.customer, coplete=False)
    orderItem, created = OrderItem.objects.get_or_create(product=product, order=order)


    if action == "add":
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == "remove":
        orderItem.quantity = (orderItem.quantity - 1)
    elif action == "delete":
        orderItem.delete()

    orderItem.save()
    if action == "delete":
        orderItem.delete()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('update item', safe=False)


class registerPage(FormView):
    template_name = 'blog/account/register.html'
    form_class = CreateUserForm
    success_url = reverse_lazy('blog:login')

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('blog:home')
        return super().get(*args, **kwargs)


    def form_valid(self, form):
        user = form.save()
        email = form.cleaned_data['email']
        customer = Customer.objects.create(user=user, email=email)
        return super().form_valid(form)


class loginPage(LoginView):
    template_name = 'blog/account/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('blog:home')

    def form_invalid(self, form):
        messages.error(self.request, 'Username or password is Incorrect')
        return super().form_invalid(self)


@login_required
def logoutPage(request):
    logout(request)
    return redirect('blog:login')


@login_required
def accountPage(request):
    customer = request.user.customer
    order_history = Order.objects.filter(customer=customer, coplete=True)
    if request.method == "POST":
        accForm = AccountForm(data=request.POST)
        if accForm.is_valid():
            accForm = AccountForm(data=request.POST)
            if accForm.is_valid():
                cd = accForm.cleaned_data
                customer.first_name = cd['first_name']
                customer.last_name = cd['last_name']
                customer.email = cd['email']
                customer.phone = cd['phone']
                customer.address = cd['address']
                image = request.FILES.get('image')
                if image:
                    customer.image = image
                customer.save()
                return redirect('blog:account')
    else:
        accForm = AccountForm()
    context = {
        'customer': customer,
        'accForm': accForm,
        'order_history': order_history,
    }
    return render(request, 'blog/account/account.html', context)


def post_search(request):
    if 'query' in request.GET:
        query = request.GET.get('query')
        lookup = Q(title_icontains=query) | Q(descriptionicontains=query) | Q(tagsname_icontains=query)
        products = Product.objects.filter(lookup, status='published')
    else:
        products = {}
    context = {
        'products': products,
    }
    return render(request, 'blog/partials/content.html', context)

# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required
# from .models import Order
# import random



def privacy_policy(request):
    return render(request, 'blog/partials/privacy_policy.html')


# from mailersend import emails

# def send_payment_confirmation_email(transaction):
#     # Extract details from the transaction
#     customer = transaction.customer
#     products = transaction.items.all()  # Assuming `items` is a related model
#     address = customer.address
#     total_price = transaction.total_price
#     shipping_fee = transaction.shipping_fee
#     discount = transaction.coupons.discount if transaction.coupons else 0
#     tx_ref = transaction.ref

#     # Format product details
#     product_details = "\n".join([
#         f"{item.product.title} x {item.quantity}" for item in products
#     ])

#     # Prepare MailerSend
#     mailer = emails.NewEmail()
#     mail_body = {}

#     mail_from = {
#         "name": "Your Company Name",
#         "email": "info@yourdomain.com",
#     }

#     recipients = [
#         {
#             "name": f"{customer.first_name} {customer.last_name}",
#             "email": customer.email,
#         }
#     ]

#     mailer.set_mail_from(mail_from, mail_body)
#     mailer.set_mail_to(recipients, mail_body)
#     mailer.set_subject(f"Payment Confirmation - Transaction #{tx_ref}", mail_body)
#     mailer.set_template("k68zxl2q7r9lj905", mail_body)  # Replace with your template ID

#     # Populate variables for the email template
#     mail_body["variables"] = [
#         {
#             "email": customer.email,
#             "substitutions": [
#                 {"var": "customer.first_name", "value": customer.first_name},
#                 {"var": "address", "value": address},
#                 {"var": "products", "value": product_details},
#                 {"var": "quantity", "value": len(products)},  # Total unique products
#                 {"var": "tx_ref", "value": tx_ref},
#                 {"var": "order.coupons.discount", "value": f"₦{discount:.2f}"},
#                 {"var": "shipping_fee", "value": f"₦{shipping_fee:.2f}"},
#                 {"var": "total_price", "value": f"₦{total_price:.2f}"},
#             ],
#         }
#     ]

#     try:
#         mailer.send(mail_body)
#         print("Payment confirmation email sent successfully.")
#     except Exception as e:
#         print(f"Error sending email: {e}")


# from django.http import JsonResponse, HttpResponse
# from django.shortcuts import redirect
# from django.views.decorators.csrf import csrf_exempt
# import requests
# import logging
# from .models import Order

# # Set up logging
# logger = logging.getLogger(__name__)

# @csrf_exempt
# def payment_callback(request):
#     """
#     Handles the payment callback from Flutterwave.
#     """
#     tx_ref = request.GET.get('tx_ref')  # Transaction reference sent by Flutterwave
#     status = request.GET.get('status')  # Status of the transaction (successful, failed, etc.)
#     transaction_id = request.GET.get('transaction_id')  # Flutterwave transaction ID

#     # Ensure all required parameters are present
#     if not (tx_ref and status and transaction_id):
#         logger.error("Missing required parameters: tx_ref, status, or transaction_id")
#         return JsonResponse({'error': 'Missing required parameters'}, status=400)

#     try:
#         # Retrieve the order from the database using tx_ref
#         order = Order.objects.get(tx_ref=tx_ref)
#         expected_amount = order.amount  # Amount expected for this transaction
#         logger.info(f"Order found for tx_ref {tx_ref}")
#     except Order.DoesNotExist:
#         logger.error(f"Order not found for tx_ref {tx_ref}")
#         return JsonResponse({'error': 'Order not found'}, status=404)

#     if status == 'successful':
#         # Verify the transaction with Flutterwave
#         url = f'https://api.flutterwave.com/v3/transactions/{transaction_id}/verify'
#         headers = {
#             "Authorization": "FLWSECK-96372794d5a323c1b258703359c8b0dd-194178c2d60vt-X",  # Replace with your secret key
#         }

#         response = requests.get(url, headers=headers)
#         if response.status_code == 200:
#             response_data = response.json()
#             logger.info(f"Flutterwave verification response: {response_data}")

#             # Validate the response
#             if (response_data['status'] == 'success' and
#                     response_data['data']['amount'] == expected_amount and
#                     response_data['data']['currency'] == "NGN"):  # Adjust currency as needed

#                 # Extract meta fields
#                 meta = response_data['data'].get('meta', {})
#                 customer_phone = meta.get('customer_phone', 'N/A')
#                 customer_address = meta.get('customer_address', 'N/A')

#                 # Log the meta data
#                 logger.info(f"Meta Data - Phone: {customer_phone}, Address: {customer_address}")

#                 # Mark the order as complete
#                 order.complete = True
#                 order.transaction_id = transaction_id
#                 order.save()
#                 logger.info(f"Order {tx_ref} marked as complete")

#                 return redirect('payment_success')  # Redirect to success page
#             else:
#                 logger.warning(f"Transaction verification failed for tx_ref {tx_ref}")
#                 return redirect('payment_error')  # Redirect to failure page
#         else:
#             logger.error(f"Transaction verification failed with status code {response.status_code}")
#             return JsonResponse({'error': 'Transaction verification failed'}, status=400)
#     else:
#         logger.warning(f"Payment failed for tx_ref {tx_ref} with status {status}")
#         return redirect('payment_error')
#  # Redirect to a failure page



from django.shortcuts import render

def payment_success(request):
    return render(request, 'blog/partials/payment_success.html')

def payment_error(request):
    return render(request, 'blog/partials/payment_error.html')
