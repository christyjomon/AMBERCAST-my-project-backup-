from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Product, ProductImage, Cart, CartItem, Order, OrderItem, Payment, Inventory, Review

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'phone', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    ordering = ('email',)
    fieldsets = UserAdmin.fieldsets + (
        ('Artisan Guild Info', {'fields': ('phone', 'address', 'role')}),
    )

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class InventoryInline(admin.StackedInline):
    model = Inventory
    can_delete = False

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'sku', 'category', 'price', 'stock_quantity', 'is_available', 'is_featured')
    list_filter = ('category', 'is_available', 'is_featured')
    search_fields = ('product_name', 'sku', 'description', 'alloy_blend')
    inlines = [ProductImageInline, InventoryInline]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.sync_inventory()

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'is_primary', 'image_path')
    list_filter = ('is_primary',)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('subtotal',)

class PaymentInline(admin.StackedInline):
    model = Payment
    can_delete = False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_reference', 'user', 'order_date', 'total_amount', 'payment_status', 'order_status')
    list_filter = ('payment_status', 'order_status', 'order_date')
    search_fields = ('order_reference', 'user__email', 'first_name', 'last_name', 'phone')
    inlines = [OrderItemInline, PaymentInline]

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'total_items', 'total_amount')

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity_available', 'last_updated')
    search_fields = ('product__product_name', 'product__sku')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'payment_method', 'amount', 'payment_status', 'payment_date', 'transaction_id')
    list_filter = ('payment_method', 'payment_status')
    search_fields = ('order__order_reference', 'transaction_id')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('product__product_name', 'user__email', 'comment')
