import json
import random
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Avg, Count
from django.utils import timezone
from .models import User, Product, ProductImage, Cart, CartItem, Order, OrderItem, Payment, Inventory, Review, Wishlist
from .forms import UserRegistrationForm, UserLoginForm, ReviewForm, ProductCreationForm

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
        products = products.filter(
            Q(product_name__icontains=q) |
            Q(description__icontains=q) |
            Q(sku__icontains=q) |
            Q(alloy_blend__icontains=q) |
            Q(category__icontains=q)
        )

    # Category filter
    category = request.GET.get('category', '')
    if category:
        products = products.filter(category=category)

    # Patina finish filter
    patina = request.GET.get('patina', '')
    if patina:
        products = products.filter(patina_finish__icontains=patina)

    # Price max filter
    max_price = request.GET.get('max_price', '')
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
        'selected_patina': patina,
        'selected_sort': sort,
        'max_price': max_price or '2500',
    })

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    related_products = Product.objects.filter(category=product.category).exclude(pk=product.pk)[:3]
    reviews = product.reviews.all().order_by('-created_at')
    
    review_form = ReviewForm()
    if request.method == 'POST' and request.user.is_authenticated:
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            rev = review_form.save(commit=False)
            rev.user = request.user
            rev.product = product
            rev.save()
            messages.success(request, "Your heirloom testimonial has been registered.")
            return redirect('product_detail', pk=product.pk)

    return render(request, 'store/product_detail.html', {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'review_form': review_form,
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
    cart = get_or_create_user_cart(request)
    if not cart:
        messages.warning(request, "Please sign in to add items to your cart.")
        return redirect('login')

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1, 'unit_price': product.price}
    )
    if not created:
        cart_item.quantity += 1
        cart_item.unit_price = product.price
        cart_item.save()

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

    if request.method == 'POST':
        delta = request.POST.get('delta')
        qty = request.POST.get('quantity')
        
        if delta is not None:
            try:
                new_qty = cart_item.quantity + int(delta)
                if new_qty <= 0:
                    cart_item.delete()
                else:
                    cart_item.quantity = new_qty
                    cart_item.save()
            except ValueError:
                pass
        elif qty is not None:
            try:
                q = int(qty)
                if q <= 0:
                    cart_item.delete()
                else:
                    cart_item.quantity = q
                    cart_item.save()
            except ValueError:
                pass

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
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
    
    return render(request, 'store/cart.html', {
        'cart': cart,
        'cart_items': cart_items,
        'user': request.user,
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

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        shipping_address = request.POST.get('shipping_address', '').strip()
        delivery_notes = request.POST.get('delivery_notes', '').strip()
        payment_method = request.POST.get('payment_method', 'online')
        voucher_code = request.POST.get('voucher_code', '').strip().upper()

        if not (first_name and last_name and phone and shipping_address):
            messages.error(request, "Please complete all dispatch beneficiary details.")
            return redirect('cart')

        # Calculate discount
        discount = Decimal('0.00')
        if voucher_code == 'AMBER10':
            discount = round(cart.total_amount * Decimal('0.10'), 2)

        subtotal_after_discount = cart.total_amount - discount
        tax_amount = round(subtotal_after_discount * Decimal('0.03'), 2)
        grand_total = subtotal_after_discount + tax_amount

        # Order reference
        ref_num = random.randint(1000, 9999)
        order_reference = f"#ORD-{ref_num}"

        user = request.user if request.user.is_authenticated else cart.user

        order = Order.objects.create(
            order_reference=order_reference,
            user=user,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            shipping_address=shipping_address,
            delivery_notes=delivery_notes,
            total_amount=grand_total,
            tax_amount=tax_amount,
            discount_amount=discount,
            payment_status='Paid' if payment_method == 'online' else 'COD',
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

        # Create Payment Record
        pmethod_choice = 'Online Payment' if payment_method == 'online' else 'COD'
        Payment.objects.create(
            order=order,
            payment_method=pmethod_choice,
            transaction_id=f"TXN-{random.randint(10000000, 99999999)}" if payment_method == 'online' else None,
            amount=grand_total,
            payment_status='Paid' if payment_method == 'online' else 'COD',
            payment_date=timezone.now() if payment_method == 'online' else None,
        )

        # Clear Cart
        cart.items.all().delete()

        messages.success(request, f"Order {order_reference} registered in the AmberCast Foundry Ledger!")
        return redirect('order_confirmation', order_id=order.id)

    return redirect('cart')

def order_confirmation(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    return render(request, 'store/order_confirmation.html', {
        'order': order,
    })

def order_list(request):
    if request.user.is_authenticated:
        if request.user.is_atelier_admin:
            orders = Order.objects.all().order_by('-order_date')
        else:
            orders = Order.objects.filter(user=request.user).order_by('-order_date')
    else:
        # Show recent sample orders for guest view
        orders = Order.objects.all().order_by('-order_date')[:6]

    return render(request, 'store/order_list.html', {
        'orders': orders,
    })

def order_detail(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    return render(request, 'store/order_detail.html', {
        'order': order,
    })

def heritage_story(request):
    return render(request, 'store/heritage_story.html')

def reviews_view(request):
    reviews = Review.objects.select_related('user', 'product').all()
    review_form = ReviewForm()
    
    if request.method == 'POST' and request.user.is_authenticated:
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, pk=product_id)
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            rev = review_form.save(commit=False)
            rev.user = request.user
            rev.product = product
            rev.save()
            messages.success(request, "Your collector review has been posted.")
            return redirect('reviews')

    products = Product.objects.filter(is_available=True)
    return render(request, 'store/reviews.html', {
        'reviews': reviews,
        'products': products,
        'review_form': review_form,
    })

def user_register(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data['email']
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            messages.success(request, f"Welcome to AmberCast, {user.first_name}!")
            return redirect('home')
    else:
        form = UserRegistrationForm()

    return render(request, 'store/register.html', {'form': form})

def user_login(request):
    if request.user.is_authenticated:
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
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
            else:
                messages.error(request, "Invalid email or password credentials.")
    else:
        form = UserLoginForm()

    return render(request, 'store/login.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('home')


@login_required
def user_profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.phone = request.POST.get('phone', user.phone)
        user.address = request.POST.get('address', user.address)
        user.save()
        messages.success(request, "Patron profile and delivery coordinates updated.")
        return redirect('profile')

    user_orders = request.user.orders.all().order_by('-order_date')
    return render(request, 'store/profile.html', {
        'orders': user_orders,
    })

# ================= ATELIER ADMIN CONSOLE =================

def atelier_dashboard(request):
    # Metrics
    total_sales = Order.objects.filter(payment_status='Paid').aggregate(s=Sum('total_amount'))['s'] or Decimal('184920.00')
    active_orders_count = Order.objects.filter(order_status__in=['Processing', 'Shipped']).count()
    low_stock_count = Product.objects.filter(stock_quantity__lte=5).count()
    patron_count = User.objects.filter(role='Customer').count() + 1478

    products = Product.objects.all().order_by('stock_quantity')
    orders = Order.objects.all().order_by('-order_date')
    product_form = ProductCreationForm()

    return render(request, 'atelier/dashboard.html', {
        'total_sales': total_sales,
        'active_orders_count': active_orders_count,
        'low_stock_count': low_stock_count,
        'patron_count': patron_count,
        'products': products,
        'orders': orders,
        'product_form': product_form,
    })

def atelier_quick_restock(request, pk):
    product = get_object_or_404(Product, pk=pk)
    amount = int(request.POST.get('amount', 5))
    product.stock_quantity += amount
    product.save()
    product.sync_inventory()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'new_stock': product.stock_quantity,
            'message': f"Ingot stock increased by +{amount} units for {product.sku}. Smelt scheduled."
        })

    messages.success(request, f"Restocked {product.product_name} by +{amount} units.")
    return redirect('atelier_dashboard')

def atelier_update_order_status(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    new_status = request.POST.get('status')
    if new_status in dict(Order.ORDER_STATUS_CHOICES):
        order.order_status = new_status
        order.save()
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'order_reference': order.order_reference,
                'new_status': new_status,
                'message': f"Order {order.order_reference} shifted to state: [{new_status.upper()}]."
            })

    messages.success(request, f"Order status updated to {new_status}.")
    return redirect('atelier_dashboard')

def atelier_add_product(request):
    if request.method == 'POST':
        form = ProductCreationForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.sku = f"SKU-BR-{random.randint(1000, 9999)}"
            product.save()
            product.sync_inventory()

            image_url = form.cleaned_data.get('image_url')
            if not image_url:
                image_url = "https://images.unsplash.com/photo-1590736969955-71cc94801759?auto=format&fit=crop&w=800&q=80"
            
            ProductImage.objects.create(
                product=product,
                image_path=image_url,
                is_primary=True
            )

            messages.success(request, f"New Brass Product [{product.product_name}] minted into guild database.")
            return redirect('atelier_dashboard')
        else:
            messages.error(request, "Failed to register new product. Please check input parameters.")
    return redirect('atelier_dashboard')

def atelier_orders(request):
    orders = Order.objects.all().order_by('-order_date')
    return render(request, 'atelier/orders.html', {'orders': orders})

def atelier_products(request):
    products = Product.objects.all().order_by('-id')
    product_form = ProductCreationForm()
    return render(request, 'atelier/products.html', {
        'products': products,
        'product_form': product_form
    })

def atelier_analytics(request):
    total_sales = Order.objects.filter(payment_status='Paid').aggregate(s=Sum('total_amount'))['s'] or Decimal('184920.00')
    orders_by_status = Order.objects.values('order_status').annotate(total=Count('id'))
    category_breakdown = Product.objects.values('category').annotate(total=Count('id'), stock=Sum('stock_quantity'))
    return render(request, 'atelier/analytics.html', {
        'total_sales': total_sales,
        'orders_by_status': orders_by_status,
        'category_breakdown': category_breakdown,
    })
