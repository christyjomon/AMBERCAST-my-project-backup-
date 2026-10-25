import os
import json
import random
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Sum, Avg, Count, ProtectedError
from django.utils import timezone
from django.conf import settings
from django.core.files.storage import default_storage
from .models import User, Product, ProductImage, Cart, CartItem, Order, OrderItem, Payment, Inventory, Review, Wishlist
from .forms import UserRegistrationForm, UserLoginForm, ReviewForm, ProductCreationForm, ProductForm, UserAdminEditForm, UserProfileForm, CheckoutForm

def get_or_create_user_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return cart
    return None


def home(request):
    featured_products = Product.objects.filter(is_available=True)[:6]
    spotlight_product = Product.objects.filter(sku="SKU-BR-9042").first() or featured_products.first()
    recent_reviews = Review.objects.select_related('user', 'product').all()[:3]
    return render(request, 'store/home.html', {
        'featured_products': featured_products,
        'spotlight_product': spotlight_product,
        'recent_reviews': recent_reviews,
    })

def catalog(request):
    products = Product.objects.filter(is_available=True)
    
    # Spotlight product (Nataraja 18")
    spotlight_product = Product.objects.filter(sku="SKU-BR-9042").first() or products.first()

    # Search filter
    q = request.GET.get('q', '').strip()
    if q:
        q_obj = (
            Q(product_name__icontains=q) |
            Q(description__icontains=q) |
            Q(sku__icontains=q) |
            Q(alloy_blend__icontains=q) |
            Q(category__icontains=q)
        )
        for term in q.split():
            q_obj |= Q(product_name__icontains=term) | Q(description__icontains=term) | Q(category__icontains=term)
        products = products.filter(q_obj).distinct()

    # Category filter (Temple Deities)
    category = request.GET.get('category', '').strip()
    if category:
        products = products.filter(category=category)
    else:
        category = 'Temple Deities'

    # Price max filter
    max_price = request.GET.get('max_price', '').strip()
    if max_price:
        try:
            products = products.filter(price__lte=Decimal(max_price))
        except Exception:
            pass

    # Sort
    sort = request.GET.get('sort', 'curator')
    if sort == 'price-asc':
        products = products.order_by('price')
    elif sort == 'price-desc':
        products = products.order_by('-price')
    elif sort == 'newest':
        products = products.order_by('-created_at')
    elif sort == 'weight':
        products = products.order_by('-weight')
    else:
        products = products.order_by('-is_featured', '-id')

    categories = Product.CATEGORY_CHOICES
    
    return render(request, 'store/catalog.html', {
        'products': products,
        'spotlight_product': spotlight_product,
        'categories': categories,
        'selected_category': category,
        'search_query': q,
        'selected_sort': sort,
        'max_price': max_price or '2500',
    })

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    related_products = Product.objects.filter(category=product.category).exclude(pk=product.pk)[:3]
    reviews = product.reviews.select_related('user').all().order_by('-created_at')
    
    has_purchased = request.user.is_authenticated and request.user.has_purchased_product(product)
    review_form = ReviewForm()
    
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to write a product review.")
            return redirect('login')

        if not has_purchased:
            messages.error(request, "Purchase this product to write a review.")
            return redirect('product_detail', pk=product.pk)

        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            rev = review_form.save(commit=False)
            rev.user = request.user
            rev.product = product
            rev.save()
            messages.success(request, "Your verified testimonial has been registered.")
            return redirect('product_detail', pk=product.pk)

    return render(request, 'store/product_detail.html', {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'review_form': review_form,
        'has_purchased': has_purchased,
    })

def add_to_cart(request, pk):
    if not request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
            return JsonResponse({
                'status': 'require_login',
                'message': 'Please sign in to add items to your cart.',
                'redirect_url': '/login/?next=' + request.META.get('HTTP_REFERER', '/catalog/'),
            }, status=401)
        messages.warning(request, "Please sign in to add items to your cart.")
        return redirect('/login/?next=/catalog/')

    product = get_object_or_404(Product, pk=pk)

    if product.stock_quantity <= 0:
        msg = f"'{product.product_name}' is currently out of stock."
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
            return JsonResponse({'status': 'error', 'message': msg}, status=400)
        messages.error(request, msg)
        return redirect(request.META.get('HTTP_REFERER', 'catalog'))

    cart = get_or_create_user_cart(request)
    if not cart:
        messages.warning(request, "Please sign in to add items to your cart.")
        return redirect('login')

    cart_item = CartItem.objects.filter(cart=cart, product=product).first()
    if cart_item:
        if cart_item.quantity + 1 > product.stock_quantity:
            msg = f"Cannot add more. Only {product.stock_quantity} units available in stock."
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
                return JsonResponse({'status': 'error', 'message': msg}, status=400)
            messages.error(request, msg)
            return redirect('cart')
        cart_item.quantity += 1
        cart_item.unit_price = product.price
        cart_item.save()
    else:
        cart_item = CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=1,
            unit_price=product.price
        )

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        return JsonResponse({
            'status': 'success',
            'message': f"{product.product_name} added to cart",
            'cart_count': cart.total_items,
            'cart_total': float(cart.total_amount),
        })

    messages.success(request, f"{product.product_name} added to your cart.")
    return redirect('cart')

def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, pk=item_id)
    cart = cart_item.cart
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

    if request.method == 'POST':
        delta = request.POST.get('delta')
        qty = request.POST.get('quantity')
        target_qty = None
        
        if delta is not None:
            try:
                target_qty = cart_item.quantity + int(delta)
            except ValueError:
                pass
        elif qty is not None:
            try:
                target_qty = int(qty)
            except ValueError:
                pass

        if target_qty is not None:
            if target_qty <= 0:
                msg = "Quantity must be at least 1. Zero or negative quantities are not allowed."
                if is_ajax:
                    return JsonResponse({'status': 'error', 'message': msg}, status=400)
                messages.error(request, msg)
                return redirect('cart')

            if target_qty > cart_item.product.stock_quantity:
                msg = f"Cannot exceed available stock ({cart_item.product.stock_quantity} available)."
                if is_ajax:
                    return JsonResponse({'status': 'error', 'message': msg}, status=400)
                messages.error(request, msg)
                return redirect('cart')

            cart_item.quantity = target_qty
            cart_item.save()

    if is_ajax:
        return JsonResponse({
            'status': 'success',
            'item_id': item_id,
            'item_qty': cart_item.quantity if cart_item.id else 0,
            'item_subtotal': float(cart_item.subtotal) if cart_item.id else 0,
            'cart_count': cart.total_items,
            'cart_subtotal': float(cart.total_amount),
            'cart_tax': float(cart.tax_amount),
            'cart_grand_total': float(cart.grand_total),
        })

    return redirect('cart')

def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, pk=item_id)
    cart = cart_item.cart
    cart_item.delete()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'cart_count': cart.total_items,
            'cart_subtotal': float(cart.total_amount),
            'cart_tax': float(cart.tax_amount),
            'cart_grand_total': float(cart.grand_total),
        })

    messages.info(request, "Product removed from your cart.")
    return redirect('cart')

@login_required(login_url='login')
def cart_view(request):
    cart = get_or_create_user_cart(request)
    cart_items = cart.items.all() if cart else []
    
    # Extract 6-digit Indian PIN code from logged-in customer's address if available
    user_pincode = ""
    if request.user.is_authenticated and getattr(request.user, 'address', None):
        import re
        match = re.search(r'\b\d{6}\b', request.user.address)
        if match:
            user_pincode = match.group(0)

    return render(request, 'store/cart.html', {
        'cart': cart,
        'cart_items': cart_items,
        'user': request.user,
        'user_pincode': user_pincode,
    })

@login_required(login_url='login')
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'store/wishlist.html', {
        'wishlist_items': wishlist_items,
    })

def toggle_wishlist(request, pk):
    if not request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
            return JsonResponse({
                'status': 'require_login',
                'message': 'Please sign in to save items to your wishlist.',
                'redirect_url': '/login/?next=' + request.META.get('HTTP_REFERER', '/catalog/'),
            }, status=401)
        messages.warning(request, "Please sign in to save items to your wishlist.")
        return redirect('/login/?next=/catalog/')

    product = get_object_or_404(Product, pk=pk)
    item = Wishlist.objects.filter(user=request.user, product=product).first()
    if item:
        item.delete()
        in_wishlist = False
        message = f"Removed {product.product_name} from your wishlist."
    else:
        Wishlist.objects.create(user=request.user, product=product)
        in_wishlist = True
        message = f"Added {product.product_name} to your wishlist."

    wishlist_count = request.user.wishlist_items.count()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        return JsonResponse({
            'status': 'success',
            'in_wishlist': in_wishlist,
            'message': message,
            'wishlist_count': wishlist_count,
        })

    messages.success(request, message)
    return redirect(request.META.get('HTTP_REFERER', 'wishlist'))

@login_required(login_url='login')
def remove_from_wishlist(request, pk):
    product = get_object_or_404(Product, pk=pk)
    Wishlist.objects.filter(user=request.user, product=product).delete()
    messages.info(request, f"Removed {product.product_name} from your wishlist.")
    return redirect('wishlist')

@login_required(login_url='login')
def move_wishlist_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart = get_or_create_user_cart(request)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1, 'unit_price': product.price}
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    Wishlist.objects.filter(user=request.user, product=product).delete()
    messages.success(request, f"Moved {product.product_name} to your cart.")
    return redirect('cart')

@login_required(login_url='login')
def checkout(request):
    cart = get_or_create_user_cart(request)
    if not cart or not cart.items.exists():
        messages.error(request, "Your atelier curation bag is currently empty.")
        return redirect('cart')

    # Validate stock quantities before proceeding
    for item in cart.items.all():
        if item.quantity <= 0:
            messages.error(request, f"Invalid quantity for '{item.product.product_name}'. Minimum quantity is 1.")
            return redirect('cart')
        if item.quantity > item.product.stock_quantity:
            messages.error(request, f"Stock issue: '{item.product.product_name}' has only {item.product.stock_quantity} units available in stock, but your cart has {item.quantity}. Please adjust the quantity.")
            return redirect('cart')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if not form.is_valid():
            error_msgs = "; ".join([f"{err}" for field, errors in form.errors.items() for err in errors])
            messages.error(request, f"Please correct the shipping information: {error_msgs}")
            return redirect('cart')

        first_name = form.cleaned_data['first_name'].strip()
        last_name = form.cleaned_data['last_name'].strip()
        phone = form.cleaned_data['phone'].strip()
        pincode = form.cleaned_data['pincode'].strip()
        shipping_address = form.cleaned_data['shipping_address'].strip()
        delivery_notes = form.cleaned_data.get('delivery_notes', '').strip()
        payment_method = form.cleaned_data.get('payment_method') or request.POST.get('payment_method', 'online')
        voucher_code = request.POST.get('voucher_code', '').strip().upper()

        full_shipping_address = shipping_address
        if pincode and pincode not in full_shipping_address:
            full_shipping_address = f"{shipping_address}, PIN: {pincode}"

        user = request.user

        # Auto-update logged-in customer profile if fields are empty
        updated_profile = False
        if not user.first_name and first_name:
            user.first_name = first_name
            updated_profile = True
        if not user.last_name and last_name:
            user.last_name = last_name
            updated_profile = True
        if not user.phone and phone:
            user.phone = phone
            updated_profile = True
        if not user.address and full_shipping_address:
            user.address = full_shipping_address
            updated_profile = True
        if updated_profile:
            user.save()

        # Calculate privilege discount and totals
        discount = Decimal('0.00')
        if voucher_code == 'AMBER10':
            discount = round(cart.total_amount * Decimal('0.10'), 2)

        subtotal_after_discount = cart.total_amount - discount
        tax_amount = round(subtotal_after_discount * Decimal('0.03'), 2)
        grand_total = subtotal_after_discount + tax_amount

        # Generate genuinely unique Order reference
        while True:
            ref_num = random.randint(10000, 99999)
            candidate_ref = f"#ORD-{timezone.now().strftime('%Y%m%d')}-{ref_num}"
            if not Order.objects.filter(order_reference=candidate_ref).exists():
                order_reference = candidate_ref
                break

        # Payment method, Transaction ID & Payment Status logic:
        # Online Payment: status is 'Paid' after verification
        # Cash on Delivery: status is 'Pending' until collected
        if payment_method == 'online':
            payment_status = 'Paid'
            pmethod_choice = 'Online Payment'
            txn_prefix = "TXN-ONL"
            payment_date = timezone.now()
        else:
            payment_status = 'Pending'
            pmethod_choice = 'COD'
            txn_prefix = "TXN-COD"
            payment_date = None

        while True:
            txn_rand = random.randint(10000, 99999)
            candidate_txn = f"{txn_prefix}-{timezone.now().strftime('%Y%m%d%H%M%S')}-{txn_rand}"
            if not Payment.objects.filter(transaction_id=candidate_txn).exists():
                transaction_id = candidate_txn
                break

        order = Order.objects.create(
            order_reference=order_reference,
            user=user,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            shipping_address=full_shipping_address,
            delivery_notes=delivery_notes,
            total_amount=grand_total,
            tax_amount=tax_amount,
            discount_amount=discount,
            payment_status=payment_status,
            order_status='Processing',
        )

        # Create Order Items and deduct stock & inventory
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                unit_price=item.unit_price,
                subtotal=item.subtotal
            )
            # Safe deduction of inventory
            if item.product.stock_quantity >= item.quantity:
                item.product.stock_quantity -= item.quantity
            else:
                item.product.stock_quantity = 0
            item.product.save()
            item.product.sync_inventory()

        # Create Payment Record with unique transaction ID and verified/pending status
        Payment.objects.create(
            order=order,
            payment_method=pmethod_choice,
            transaction_id=transaction_id,
            amount=grand_total,
            payment_status=payment_status,
            payment_date=payment_date,
        )

        # Clear Cart
        cart.items.all().delete()

        messages.success(request, f"Order {order_reference} registered successfully in the AmberCast Foundry Ledger!")
        return redirect('order_confirmation', order_id=order.id)

    return redirect('cart')

@login_required(login_url='login')
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if not (request.user == order.user or request.user.is_atelier_admin):
        messages.error(request, "Access restricted. You are not authorized to view this order confirmation.")
        return redirect('orders')
    return render(request, 'store/order_confirmation.html', {
        'order': order,
        'payment': getattr(order, 'payment', None),
    })

@login_required(login_url='login')
def order_invoice(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    # Verification: only owner or authorized atelier administrator
    if not (request.user == order.user or request.user.is_atelier_admin):
        messages.error(request, "Access restricted. You are not authorized to view another patron's invoice.")
        return redirect('orders')

    # Ensure payment record exists with transaction ID
    if not hasattr(order, 'payment') or not order.payment:
        txn_prefix = "TXN-COD" if order.payment_status == 'Pending' else "TXN-ONL"
        txn_id = f"{txn_prefix}-{timezone.now().strftime('%Y%m%d%H%M%S')}-{random.randint(10000, 99999)}"
        payment = Payment.objects.create(
            order=order,
            payment_method='COD' if order.payment_status == 'Pending' else 'Online Payment',
            transaction_id=txn_id,
            amount=order.total_amount,
            payment_status=order.payment_status,
            payment_date=order.order_date if order.payment_status == 'Paid' else None
        )
    else:
        payment = order.payment
        if not payment.transaction_id:
            txn_prefix = "TXN-COD" if payment.payment_method == 'COD' else "TXN-ONL"
            payment.transaction_id = f"{txn_prefix}-{timezone.now().strftime('%Y%m%d%H%M%S')}-{random.randint(10000, 99999)}"
            payment.save()

    subtotal_before_tax = order.total_amount - order.tax_amount

    return render(request, 'store/invoice.html', {
        'order': order,
        'payment': payment,
        'subtotal_before_tax': subtotal_before_tax,
    })

@login_required(login_url='login')
def order_list(request):
    if request.user.is_atelier_admin:
        orders = Order.objects.all().order_by('-order_date')
    else:
        orders = Order.objects.filter(user=request.user).order_by('-order_date')

    return render(request, 'store/order_list.html', {
        'orders': orders,
    })

@login_required(login_url='login')
def order_detail(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if not (request.user == order.user or request.user.is_atelier_admin):
        messages.error(request, "Access restricted. You are not authorized to view another patron's order record.")
        return redirect('orders')
    return render(request, 'store/order_detail.html', {
        'order': order,
    })

@login_required(login_url='login')
def cancel_order(request, order_id):
    if request.method != 'POST':
        messages.warning(request, "Order cancellation must be submitted via POST.")
        return redirect('orders')

    order = get_object_or_404(Order, pk=order_id)

    # Permission check: customer can only cancel their own order (or admin)
    if not (order.user == request.user or request.user.is_atelier_admin):
        messages.error(request, "Access restricted. You are not authorized to cancel this order.")
        return redirect('orders')

    # Status check: only Pending or Processing can be cancelled
    if not order.can_cancel:
        if order.order_status == 'Cancelled':
            messages.info(request, f"Order {order.order_reference} is already cancelled.")
        elif order.order_status in ['Shipped', 'Delivered']:
            messages.error(request, f"Order {order.order_reference} cannot be cancelled because it has already been {order.order_status.lower()}.")
        else:
            messages.error(request, f"Order {order.order_reference} cannot be cancelled with current status: '{order.order_status}'.")
        return redirect('orders')

    # Atomic cancellation and stock restoration with row-level locking
    with transaction.atomic():
        locked_order = Order.objects.select_for_update().get(pk=order.pk)
        success, msg = locked_order.cancel_order()

    if success:
        messages.success(request, f"Order {order.order_reference} has been cancelled successfully. Product stock has been restored to inventory.")
    else:
        messages.error(request, msg)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success' if success else 'error',
            'message': msg,
            'order_reference': order.order_reference,
            'new_status': locked_order.order_status
        })

    referer = request.META.get('HTTP_REFERER')
    if referer and ('/orders/' in referer or '/order-detail/' in referer):
        return redirect(referer)
    return redirect('orders')

def heritage_story(request):
    return render(request, 'store/heritage_story.html')

def reviews_view(request):
    reviews = Review.objects.select_related('user', 'product').all()
    review_form = ReviewForm()
    
    if request.user.is_authenticated:
        purchased_products = Product.objects.filter(
            order_items__order__user=request.user
        ).exclude(
            order_items__order__order_status='Cancelled'
        ).exclude(
            order_items__order__payment_status='Failed'
        ).distinct()
    else:
        purchased_products = Product.objects.none()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to submit a review.")
            return redirect('login')

        product_id = request.POST.get('product_id')
        if not product_id:
            messages.error(request, "Please select an artwork to review.")
            return redirect('reviews')

        product = get_object_or_404(Product, pk=product_id)

        if not request.user.has_purchased_product(product):
            messages.error(request, "Purchase this product to write a review.")
            return redirect('reviews')

        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            rev = review_form.save(commit=False)
            rev.user = request.user
            rev.product = product
            rev.save()
            messages.success(request, "Your collector review has been posted.")
            return redirect('reviews')

    return render(request, 'store/reviews.html', {
        'reviews': reviews,
        'purchased_products': purchased_products,
        'review_form': review_form,
    })

def user_register(request):
    next_url = request.POST.get('next') or request.GET.get('next') or 'home'

    if request.user.is_authenticated:
        if next_url and next_url != 'home':
            return redirect(next_url)
        return redirect('home')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data['email']
            user.role = 'Customer'
            user.is_staff = False
            user.is_superuser = False
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            messages.success(request, f"Welcome to AmberCast, {user.first_name}!")
            if next_url and next_url.startswith('/') and not next_url.startswith('//'):
                if next_url.startswith('/atelier') and not user.is_atelier_admin:
                    messages.error(request, "Access restricted. Atelier administrator authorization required.")
                    return redirect('home')
                return redirect(next_url)
            return redirect('home')
    else:
        form = UserRegistrationForm()

    return render(request, 'store/register.html', {
        'form': form,
        'next': next_url,
    })

def user_login(request):
    next_url = request.POST.get('next') or request.GET.get('next') or 'home'

    if request.user.is_authenticated:
        if next_url and next_url != 'home':
            return redirect(next_url)
        return redirect('home')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email_or_user = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Try by email
            user_obj = User.objects.filter(email=email_or_user).first()
            username = user_obj.username if user_obj else email_or_user

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, f"Welcome back, {user.first_name or user.email}!")
                if next_url and next_url.startswith('/') and not next_url.startswith('//'):
                    if next_url.startswith('/atelier') and not user.is_atelier_admin:
                        messages.error(request, "Access restricted. Atelier administrator authorization required.")
                        return redirect('home')
                    return redirect(next_url)
                return redirect('home')
            else:
                messages.error(request, "Invalid email or password credentials.")
    else:
        form = UserLoginForm()

    return render(request, 'store/login.html', {
        'form': form,
        'next': next_url,
    })

def user_logout(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('home')


@login_required
def user_profile(request):
    profile_form = UserProfileForm(instance=request.user)
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, instance=request.user)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, "Patron profile and delivery coordinates updated.")
            return redirect('profile')
        else:
            errors_str = "; ".join([f"{field}: {', '.join(errs)}" for field, errs in profile_form.errors.items()])
            messages.error(request, f"Failed to update profile: {errors_str}")

    user_orders = request.user.orders.all().order_by('-order_date')
    return render(request, 'store/profile.html', {
        'orders': user_orders,
        'profile_form': profile_form,
    })

# ================= ATELIER ADMIN CONSOLE =================

def atelier_admin_required(view_func):
    """Ensure user is logged in and possesses active staff or atelier administrator privileges."""
    @login_required(login_url='login')
    def _wrapped_view(request, *args, **kwargs):
        if not (request.user.is_authenticated and request.user.is_active and request.user.is_atelier_admin):
            messages.error(request, "Access restricted. Atelier administrator authorization required.")
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


@atelier_admin_required
def atelier_dashboard(request):
    total_sales = Order.objects.filter(payment_status='Paid').aggregate(s=Sum('total_amount'))['s'] or Decimal('184920.00')
    active_orders_count = Order.objects.filter(order_status__in=['Processing', 'Shipped']).count()
    low_stock_count = Product.objects.filter(stock_quantity__lte=5).count()
    patron_count = User.objects.filter(role='Customer').count() + 1478

    products = Product.objects.all().order_by('stock_quantity')
    orders = Order.objects.all().order_by('-order_date')
    product_form = ProductForm()

    return render(request, 'atelier/dashboard.html', {
        'total_sales': total_sales,
        'active_orders_count': active_orders_count,
        'low_stock_count': low_stock_count,
        'patron_count': patron_count,
        'products': products,
        'orders': orders,
        'product_form': product_form,
    })


@atelier_admin_required
def atelier_quick_restock(request, pk):
    product = get_object_or_404(Product, pk=pk)
    try:
        amount = int(request.POST.get('amount', 5))
    except (ValueError, TypeError):
        amount = 0

    if amount <= 0:
        msg = "Restock amount must be a positive integer greater than zero."
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': msg}, status=400)
        messages.error(request, msg)
        return redirect('atelier_dashboard')

    product.stock_quantity += amount
    product.save()
    product.sync_inventory()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'new_stock': product.stock_quantity,
            'message': f"Stock increased by +{amount} units for {product.sku} ({product.product_name})."
        })

    messages.success(request, f"Restocked {product.product_name} by +{amount} units.")
    return redirect('atelier_dashboard')


@atelier_admin_required
def atelier_update_order_status(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    new_status = request.POST.get('status')
    if new_status in dict(Order.ORDER_STATUS_CHOICES):
        old_status = order.order_status
        if new_status == 'Cancelled' and old_status != 'Cancelled':
            order.cancel_order()
        else:
            order.order_status = new_status
            # If COD order is delivered, automatically collect payment & mark Paid
            if new_status == 'Delivered' and order.payment_status == 'Pending':
                order.payment_status = 'Paid'
                if hasattr(order, 'payment') and order.payment:
                    order.payment.payment_status = 'Paid'
                    if not order.payment.payment_date:
                        order.payment.payment_date = timezone.now()
                    order.payment.save()
            order.save()
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'order_reference': order.order_reference,
                'new_status': new_status,
                'payment_status': order.payment_status,
                'message': f"Order {order.order_reference} shifted to state: [{new_status.upper()}]."
            })

    messages.success(request, f"Order status updated to {new_status}.")
    referer = request.META.get('HTTP_REFERER')
    if referer and 'atelier' in referer:
        return redirect(referer)
    return redirect('atelier_orders')


@atelier_admin_required
def atelier_update_payment_status(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if request.method == 'POST':
        new_payment_status = request.POST.get('payment_status')
        if new_payment_status in ['Paid', 'Pending', 'Failed']:
            order.payment_status = new_payment_status
            order.save()
            if hasattr(order, 'payment') and order.payment:
                order.payment.payment_status = new_payment_status
                if new_payment_status == 'Paid' and not order.payment.payment_date:
                    order.payment.payment_date = timezone.now()
                order.payment.save()
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'order_reference': order.order_reference,
                    'payment_status': order.payment_status,
                    'message': f"Payment status for {order.order_reference} updated to {new_payment_status}."
                })
            messages.success(request, f"Payment status for {order.order_reference} updated to {new_payment_status}.")

    referer = request.META.get('HTTP_REFERER')
    if referer and 'atelier' in referer:
        return redirect(referer)
    return redirect('atelier_orders')


@atelier_admin_required
def atelier_add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            if not product.sku:
                product.sku = f"SKU-BR-{random.randint(1000, 9999)}"
            product.save()
            product.sync_inventory()

            # Handle image upload or image URL
            final_image_path = None
            if request.FILES.get('image_file'):
                image_file = request.FILES['image_file']
                upload_dir = os.path.join(settings.MEDIA_ROOT, 'products')
                os.makedirs(upload_dir, exist_ok=True)
                saved_path = default_storage.save(f"products/{image_file.name}", image_file)
                final_image_path = f"{settings.MEDIA_URL}{saved_path}"
            elif form.cleaned_data.get('image_url') and form.cleaned_data.get('image_url').strip():
                final_image_path = form.cleaned_data.get('image_url').strip()
            else:
                final_image_path = "https://images.unsplash.com/photo-1590736969955-71cc94801759?auto=format&fit=crop&w=800&q=80"

            ProductImage.objects.create(
                product=product,
                image_path=final_image_path,
                is_primary=True
            )

            messages.success(request, f"New product '{product.product_name}' was minted into the catalog.")
            next_url = request.POST.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('atelier_products')
        else:
            errors_summary = "; ".join(f"{field}: {', '.join(errs)}" for field, errs in form.errors.items())
            messages.error(request, f"Failed to add product: {errors_summary}")
            next_url = request.POST.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('atelier_products')
    return redirect('atelier_products')


@atelier_admin_required
def atelier_edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            product.sync_inventory()

            # Handle image update if new file or URL provided
            if request.FILES.get('image_file'):
                image_file = request.FILES['image_file']
                upload_dir = os.path.join(settings.MEDIA_ROOT, 'products')
                os.makedirs(upload_dir, exist_ok=True)
                saved_path = default_storage.save(f"products/{image_file.name}", image_file)
                new_image_path = f"{settings.MEDIA_URL}{saved_path}"
                primary_img = product.images.filter(is_primary=True).first()
                if primary_img:
                    primary_img.image_path = new_image_path
                    primary_img.save()
                else:
                    ProductImage.objects.create(product=product, image_path=new_image_path, is_primary=True)
            elif form.cleaned_data.get('image_url') and form.cleaned_data.get('image_url').strip():
                new_image_path = form.cleaned_data.get('image_url').strip()
                primary_img = product.images.filter(is_primary=True).first()
                if primary_img:
                    primary_img.image_path = new_image_path
                    primary_img.save()
                else:
                    ProductImage.objects.create(product=product, image_path=new_image_path, is_primary=True)

            messages.success(request, f"Product '{product.product_name}' has been updated successfully.")
            return redirect('atelier_products')
        else:
            errors_summary = "; ".join(f"{field}: {', '.join(errs)}" for field, errs in form.errors.items())
            messages.error(request, f"Failed to update product: {errors_summary}")
    else:
        primary_img = product.images.filter(is_primary=True).first() or product.images.first()
        initial_img = primary_img.image_path if primary_img else ''
        form = ProductForm(instance=product, initial={'image_url': initial_img})

    return render(request, 'atelier/product_edit.html', {
        'product': product,
        'form': form,
    })


@atelier_admin_required
def atelier_delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product_name = product.product_name

    if request.method == 'POST':
        # 1. Clean up associated physical product image files from media storage
        for img in product.images.all():
            if img.image_path and not img.image_path.startswith(('http://', 'https://')):
                rel_path = img.image_path
                if rel_path.startswith(settings.MEDIA_URL):
                    rel_path = rel_path[len(settings.MEDIA_URL):]
                full_path = os.path.join(settings.MEDIA_ROOT, rel_path.lstrip('/'))
                if os.path.exists(full_path):
                    try:
                        os.remove(full_path)
                    except Exception:
                        pass

        # 2. Cleanly delete all related records
        OrderItem.objects.filter(product=product).delete()
        CartItem.objects.filter(product=product).delete()
        Wishlist.objects.filter(product=product).delete()
        Review.objects.filter(product=product).delete()
        if hasattr(product, 'inventory'):
            product.inventory.delete()
        product.images.all().delete()

        # 3. Permanently delete the product from the database
        product.delete()
        messages.success(request, f"Product '{product_name}' was permanently deleted from the database.")
        return redirect('atelier_products')

    return redirect('atelier_products')


@atelier_admin_required
def atelier_orders(request):
    orders = Order.objects.all().order_by('-order_date')
    return render(request, 'atelier/orders.html', {'orders': orders})


@atelier_admin_required
def atelier_products(request):
    products = Product.objects.all().order_by('-id')
    q = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()
    if q:
        products = products.filter(
            Q(product_name__icontains=q) |
            Q(sku__icontains=q) |
            Q(category__icontains=q)
        )
    if category and category != 'ALL':
        products = products.filter(category=category)

    product_form = ProductForm()
    return render(request, 'atelier/products.html', {
        'products': products,
        'product_form': product_form,
        'search_query': q,
        'selected_category': category,
        'categories': Product.CATEGORY_CHOICES,
    })


@atelier_admin_required
def atelier_analytics(request):
    total_sales = Order.objects.filter(payment_status='Paid').aggregate(s=Sum('total_amount'))['s'] or Decimal('184920.00')
    orders_by_status = Order.objects.values('order_status').annotate(total=Count('id'))
    category_breakdown = Product.objects.values('category').annotate(total=Count('id'), stock=Sum('stock_quantity'))
    return render(request, 'atelier/analytics.html', {
        'total_sales': total_sales,
        'orders_by_status': orders_by_status,
        'category_breakdown': category_breakdown,
    })


@atelier_admin_required
def atelier_users(request):
    users = User.objects.all().order_by('-date_joined')
    q = request.GET.get('q', '').strip()
    role_filter = request.GET.get('role', '').strip()

    if q:
        users = users.filter(
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(email__icontains=q) |
            Q(phone__icontains=q) |
            Q(username__icontains=q)
        )

    if role_filter and role_filter != 'ALL':
        if role_filter == 'Staff':
            users = users.filter(Q(is_staff=True) | Q(is_superuser=True) | Q(role='Admin'))
        else:
            users = users.filter(role=role_filter)

    total_count = User.objects.count()
    customer_count = User.objects.filter(role='Customer').count()
    admin_count = User.objects.filter(Q(role='Admin') | Q(is_staff=True) | Q(is_superuser=True)).distinct().count()

    return render(request, 'atelier/users.html', {
        'users': users,
        'search_query': q,
        'selected_role': role_filter,
        'total_count': total_count,
        'customer_count': customer_count,
        'admin_count': admin_count,
    })


@atelier_admin_required
def atelier_edit_user(request, pk):
    target_user = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        form = UserAdminEditForm(request.POST, instance=target_user)
        if form.is_valid():
            updated_user = form.save(commit=False)
            updated_user.username = updated_user.email
            
            if updated_user.role == 'Admin':
                updated_user.is_staff = True

            new_password = form.cleaned_data.get('new_password')
            if new_password:
                updated_user.set_password(new_password)

            updated_user.save()
            messages.success(request, f"User profile for '{updated_user.email}' was successfully updated.")
            return redirect('atelier_users')
        else:
            errors_summary = "; ".join(f"{field}: {', '.join(errs)}" for field, errs in form.errors.items())
            messages.error(request, f"Failed to update user profile: {errors_summary}")
    else:
        form = UserAdminEditForm(instance=target_user)

    user_orders = target_user.orders.all().order_by('-order_date')[:6]

    return render(request, 'atelier/user_edit.html', {
        'target_user': target_user,
        'form': form,
        'user_orders': user_orders,
    })


@atelier_admin_required
def atelier_delete_user(request, pk):
    target_user = get_object_or_404(User, pk=pk)

    # Security check: Admin cannot delete their own active session
    if target_user.id == request.user.id:
        messages.error(request, "Security violation: You cannot delete your own active administrator account.")
        return redirect('atelier_users')

    if request.method == 'POST':
        user_email = target_user.email
        target_user.delete()
        messages.success(request, f"User profile '{user_email}' was permanently deleted from the website.")
        return redirect('atelier_users')

    return redirect('atelier_users')
