from django.db import models, transaction
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from decimal import Decimal

class User(AbstractUser):
    ROLE_CHOICES = (
        ('Customer', 'Customer'),
        ('Admin', 'Admin'),
    )
    email = models.EmailField(unique=True, help_text="User email address used for login")
    phone = models.CharField(max_length=20, blank=True, null=True, help_text="User contact number")
    address = models.TextField(blank=True, null=True, help_text="User delivery address")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Customer')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.email

    @property
    def is_atelier_admin(self):
        return (self.role == 'Admin' or self.is_staff or self.is_superuser) and self.is_active

    def has_purchased_product(self, product):
        """Verify customer has actually purchased this specific product."""
        if not self.is_authenticated:
            return False
        return self.orders.filter(
            items__product=product
        ).exclude(order_status='Cancelled').exclude(payment_status='Failed').exists()


class Product(models.Model):
    CATEGORY_CHOICES = (
        ('Temple Deities', 'Temple Deities'),
    )

    product_name = models.CharField(max_length=150, help_text="Name of the handcrafted brass product")
    sku = models.CharField(max_length=50, unique=True, help_text="Unique artisan inventory SKU code")
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default='Temple Deities')
    description = models.TextField(help_text="Detailed product description and iconography notes", blank=True, default="")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Current selling price in INR")
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Original retail price before guild privilege")
    stock_quantity = models.IntegerField(default=0, help_text="Available quantity in stock")
    is_available = models.BooleanField(default=True, help_text="Indicates whether the product can be purchased")
    
    # Artisanal Specifications
    weight = models.CharField(max_length=50, default="3.5 kg", blank=True, help_text="Physical weight (e.g. 4.2 kg)")
    dimensions = models.CharField(max_length=100, default='14" x 10"', blank=True, help_text='Dimensions (e.g. 18.5" x 14.2")')
    alloy_blend = models.CharField(max_length=120, default="85-88% Copper CuZn Solid Brass", blank=True, help_text="Metallurgical alloy composition")
    patina_finish = models.CharField(max_length=100, default="Antique Brown Patina", blank=True, help_text="Surface finish/patina")
    casting_technique = models.CharField(max_length=120, default="Lost-Wax Sand Casting (Cire Perdue)", blank=True, help_text="Foundry technique")
    provenance = models.CharField(max_length=150, default="Swamimalai / Thanjavur Bronze Guild", blank=True, help_text="Artisanal guild provenance")
    is_featured = models.BooleanField(default=False, help_text="Display on storefront hero showcase")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f"{self.product_name} ({self.sku})"

    @property
    def primary_image_url(self):
        primary_img = self.images.filter(is_primary=True).first()
        if primary_img:
            return primary_img.image_path
        first_img = self.images.first()
        if first_img:
            return first_img.image_path
        return "https://images.unsplash.com/photo-1590736969955-71cc94801759?auto=format&fit=crop&w=800&q=80"

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            avg = sum(r.rating for r in reviews) / reviews.count()
            return round(avg, 1)
        return 5.0

    @property
    def review_count(self):
        return self.reviews.count()

    def sync_inventory(self):
        # Keeps Table 8 Inventory in sync
        inv, _ = Inventory.objects.get_or_create(product=self)
        inv.quantity_available = self.stock_quantity
        inv.save()

    def save(self, *args, **kwargs):
        if not self.category or self.category != 'Temple Deities':
            self.category = 'Temple Deities'
        super().save(*args, **kwargs)


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image_path = models.CharField(max_length=500, help_text="Stored image file path or URL")
    is_primary = models.BooleanField(default=False, help_text="Indicates the main product image")

    def __str__(self):
        return f"Image for {self.product.product_name} ({'Primary' if self.is_primary else 'Alt'})"


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user.email}"

    @property
    def total_amount(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def tax_amount(self):
        # 3% GST on brass metalcraft as shown in UI
        return round(Decimal(self.total_amount) * Decimal('0.03'), 2)

    @property
    def grand_total(self):
        return round(Decimal(self.total_amount) + Decimal(self.tax_amount), 2)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"{self.quantity}x {self.product.product_name}"

    @property
    def subtotal(self):
        return self.quantity * self.unit_price


class Order(models.Model):
    PAYMENT_STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Failed', 'Failed'),
        ('COD', 'COD (Cash On Delivery)'),
    )

    ORDER_STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    )

    order_reference = models.CharField(max_length=50, unique=True, help_text="Unique order ledger reference e.g. #ORD-9801")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_date = models.DateTimeField(auto_now_add=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    shipping_address = models.TextField()
    delivery_notes = models.CharField(max_length=255, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    payment_status = models.CharField(max_length=30, choices=PAYMENT_STATUS_CHOICES, default='Pending')
    order_status = models.CharField(max_length=30, choices=ORDER_STATUS_CHOICES, default='Processing')
    stock_restored = models.BooleanField(default=False, help_text="Indicates whether inventory stock was restored after order cancellation")

    class Meta:
        ordering = ['-order_date']

    def __str__(self):
        return f"{self.order_reference} - {self.user.email}"

    @property
    def can_cancel(self):
        """Customers can only cancel their order when status is Pending or Processing."""
        return self.order_status in ['Pending', 'Processing']

    def cancel_order(self):
        """
        Cancels the order and restores exact product quantities to inventory.
        Guarantees that stock restoration happens exactly once.
        Returns: tuple (success: bool, message: str)
        """
        if not self.can_cancel:
            if self.order_status == 'Cancelled':
                return False, f"Order {self.order_reference} is already cancelled."
            return False, f"Order {self.order_reference} cannot be cancelled because it has already been {self.order_status.lower()}."

        with transaction.atomic():
            if not self.stock_restored:
                for item in self.items.select_related('product').all():
                    if item.product:
                        # Lock and update product stock
                        product = Product.objects.select_for_update().get(pk=item.product.pk)
                        product.stock_quantity += item.quantity
                        product.save()
                        product.sync_inventory()
                self.stock_restored = True

            self.order_status = 'Cancelled'
            # If payment was pending, update payment status
            if self.payment_status in ['Pending', 'COD']:
                self.payment_status = 'Failed'
                if hasattr(self, 'payment') and self.payment:
                    self.payment.payment_status = 'Failed'
                    self.payment.save()
            self.save()

        return True, f"Order {self.order_reference} has been cancelled successfully. Product stock has been restored to inventory."

    @property
    def transaction_id(self):
        if hasattr(self, 'payment') and self.payment and self.payment.transaction_id:
            return self.payment.transaction_id
        return None

    @property
    def invoice_number(self):
        ref = self.order_reference.replace('#', '').strip()
        return f"INV-{ref}"

    @property
    def is_paid(self):
        return self.payment_status == 'Paid'

    @property
    def payment_method_name(self):
        if hasattr(self, 'payment') and self.payment and self.payment.payment_method:
            return self.payment.get_payment_method_display()
        return "Cash on Delivery" if self.payment_status == 'Pending' else "Online Payment"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        prod_name = self.product.product_name if self.product else "Deleted Product"
        return f"{self.quantity}x {prod_name} in {self.order.order_reference}"


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ('COD', 'Cash on Delivery'),
        ('Online Payment', 'Online Payment'),
    )
    PAYMENT_STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Failed', 'Failed'),
        ('COD', 'COD'),
    )

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=150, unique=True, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=30, choices=PAYMENT_STATUS_CHOICES, default='Pending')
    payment_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Payment {self.payment_method} for {self.order.order_reference} ({self.payment_status})"


class Inventory(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='inventory')
    quantity_available = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Inventories"

    def __str__(self):
        return f"Inventory: {self.product.product_name} ({self.quantity_available} units)"


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(help_text="Rating value, 1 to 5")
    comment = models.TextField(blank=True, null=True, help_text="Customer review/comment")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.user.email} on {self.product.product_name} ({self.rating}/5)"

    @property
    def is_verified_purchase(self):
        """Check if the review is linked to a genuine completed purchase by the author."""
        if not self.user_id or not self.product_id:
            return False
        return self.user.has_purchased_product(self.product)


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlist_items')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-created_at']

    def __str__(self):
        return f"Wishlist item {self.product.product_name} for {self.user.email}"

