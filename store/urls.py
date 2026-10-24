from django.urls import path
from . import views

urlpatterns = [
    # Storefront & Catalog
    path('', views.home, name='home'),
    path('catalog/', views.catalog, name='catalog'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    
    # Shopping Cart & Checkout
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    
    # Wishlist
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/toggle/<int:pk>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('wishlist/remove/<int:pk>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/move-to-cart/<int:pk>/', views.move_wishlist_to_cart, name='move_wishlist_to_cart'),

    
    # Orders & Heritage & Reviews
    path('orders/', views.order_list, name='orders'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('heritage/', views.heritage_story, name='heritage_story'),
    path('reviews/', views.reviews_view, name='reviews'),
    
    # User Authentication & Profile
    path('register/', views.user_register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.user_profile, name='profile'),
    
    # Atelier Admin & Operations Dashboard
    path('atelier/', views.atelier_dashboard, name='atelier_dashboard'),
    path('atelier/restock/<int:pk>/', views.atelier_quick_restock, name='atelier_quick_restock'),
    path('atelier/order-status/<int:order_id>/', views.atelier_update_order_status, name='atelier_update_order_status'),
    path('atelier/add-product/', views.atelier_add_product, name='atelier_add_product'),
    path('atelier/orders/', views.atelier_orders, name='atelier_orders'),
    path('atelier/products/', views.atelier_products, name='atelier_products'),
    path('atelier/analytics/', views.atelier_analytics, name='atelier_analytics'),
]
