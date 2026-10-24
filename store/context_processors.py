def cart_context(request):
    if request.user.is_authenticated:
        try:
            cart = request.user.cart
            cart_count = cart.total_items
            cart_subtotal = cart.total_amount
        except Exception:
            cart_count = 0
            cart_subtotal = 0
        try:
            wishlist_count = request.user.wishlist_items.count()
            wishlist_product_ids = list(request.user.wishlist_items.values_list('product_id', flat=True))
        except Exception:
            wishlist_count = 0
            wishlist_product_ids = []
    else:
        cart_count = 0
        cart_subtotal = 0
        wishlist_count = 0
        wishlist_product_ids = []

    return {
        'cart_count': cart_count,
        'cart_subtotal': cart_subtotal,
        'wishlist_count': wishlist_count,
        'wishlist_product_ids': wishlist_product_ids,
    }

