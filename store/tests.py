from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from .models import User, Product, ProductImage, Cart, CartItem, Order, OrderItem, Payment, Inventory, Review

class AmberCastTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='patron@ambercast.com',
            email='patron@ambercast.com',
            password='testpassword123',
            first_name='Devraj',
            last_name='Sengupta',
            role='Customer'
        )
        self.product = Product.objects.create(
            product_name='Cosmic Nataraja 18"',
            sku='SKU-TEST-01',
            category='Temple Deities',
            description='Test brass statue.',
            price=Decimal('485.00'),
            stock_quantity=10,
            weight='6.2 kg',
            alloy_blend='82% Cu • 18% Zn Brass',
            patina_finish='Antique Ochre'
        )
        self.product.sync_inventory()

    def test_product_and_inventory(self):
        self.assertEqual(self.product.inventory.quantity_available, 10)
        self.assertEqual(str(self.product), 'Cosmic Nataraja 18" (SKU-TEST-01)')

    def test_cart_workflow(self):
        self.client.login(username='patron@ambercast.com', password='testpassword123')
        # Add to cart
        response = self.client.get(reverse('add_to_cart', args=[self.product.id]), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['cart_count'], 1)

        cart = Cart.objects.get(user=self.user)
        self.assertEqual(cart.total_items, 1)
        self.assertEqual(cart.total_amount, Decimal('485.00'))

    def test_checkout_workflow(self):
        self.client.login(username='patron@ambercast.com', password='testpassword123')
        self.client.get(reverse('add_to_cart', args=[self.product.id]))

        checkout_data = {
            'first_name': 'Devraj',
            'last_name': 'Sengupta',
            'phone': '9820144921',
            'shipping_address': '42/A Heritage Estate, Mumbai',
            'delivery_notes': 'Handle with care',
            'payment_method': 'online',
            'voucher_code': 'AMBER10'
        }
        response = self.client.post(reverse('checkout'), data=checkout_data)
        self.assertEqual(response.status_code, 302)

        # Check order created
        order = Order.objects.filter(user=self.user).first()
        self.assertIsNotNone(order)
        self.assertEqual(order.payment_status, 'Paid')
        
        # Check stock decremented
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 9)
        self.assertEqual(self.product.inventory.quantity_available, 9)

    def test_atelier_restock(self):
        response = self.client.post(
            reverse('atelier_quick_restock', args=[self.product.id]),
            {'amount': 5},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 15)
        self.assertEqual(self.product.inventory.quantity_available, 15)
