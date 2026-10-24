from django import forms
from django.contrib.auth import authenticate
from .models import User, Product, Review, Order

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full bg-surface-container-low focus:bg-surface-container-lowest text-on-surface px-space-md py-space-sm rounded font-body-md text-body-md outline-none transition-all shadow-sm focus:ring-1 focus:ring-primary',
        'placeholder': '••••••••••••'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full bg-surface-container-low focus:bg-surface-container-lowest text-on-surface px-space-md py-space-sm rounded font-body-md text-body-md outline-none transition-all shadow-sm focus:ring-1 focus:ring-primary',
        'placeholder': '••••••••••••'
    }))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'role']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'w-full bg-surface-container-low focus:bg-surface-container-lowest text-on-surface px-space-md py-space-sm rounded font-body-md text-body-md outline-none transition-all shadow-sm focus:ring-1 focus:ring-primary', 'placeholder': 'e.g. Devraj'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full bg-surface-container-low focus:bg-surface-container-lowest text-on-surface px-space-md py-space-sm rounded font-body-md text-body-md outline-none transition-all shadow-sm focus:ring-1 focus:ring-primary', 'placeholder': 'e.g. Sengupta'}),
            'email': forms.EmailInput(attrs={'class': 'w-full bg-surface-container-low focus:bg-surface-container-lowest text-on-surface px-space-md py-space-sm rounded font-body-md text-body-md outline-none transition-all shadow-sm focus:ring-1 focus:ring-primary', 'placeholder': 'devraj@heritage.com'}),
            'phone': forms.TextInput(attrs={'class': 'w-full bg-surface-container-low focus:bg-surface-container-lowest text-on-surface px-space-md py-space-sm rounded font-body-md text-body-md outline-none transition-all shadow-sm focus:ring-1 focus:ring-primary', 'placeholder': '+91 98201 44921'}),
            'address': forms.Textarea(attrs={'class': 'w-full bg-surface-container-low focus:bg-surface-container-lowest text-on-surface p-space-md rounded font-body-md text-body-md outline-none transition-all shadow-sm focus:ring-1 focus:ring-primary resize-none', 'rows': 3, 'placeholder': 'Delivery address with PIN/Postal Code'}),
            'role': forms.Select(attrs={'class': 'w-full bg-surface-container-low focus:bg-surface-container-lowest text-on-surface px-space-md py-space-sm rounded font-body-md text-body-md outline-none transition-all shadow-sm focus:ring-1 focus:ring-primary'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        pwd = cleaned_data.get('password')
        cpwd = cleaned_data.get('confirm_password')
        if pwd and cpwd and pwd != cpwd:
            self.add_error('confirm_password', 'Passwords do not match.')
        return cleaned_data


class UserLoginForm(forms.Form):
    email = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'w-full bg-surface-container-low focus:bg-surface-container-lowest text-on-surface px-space-md py-space-sm rounded font-body-md text-body-md outline-none transition-all shadow-sm focus:ring-1 focus:ring-primary',
        'placeholder': 'Enter your registered email address'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full bg-surface-container-low focus:bg-surface-container-lowest text-on-surface px-space-md py-space-sm rounded font-body-md text-body-md outline-none transition-all shadow-sm focus:ring-1 focus:ring-primary',
        'placeholder': '••••••••••••'
    }))


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(5, '★★★★★ (5 Stars - Heirloom Masterwork)'), (4, '★★★★☆ (4 Stars - Exceptional)'), (3, '★★★☆☆ (3 Stars - Satisfactory)'), (2, '★★☆☆☆ (2 Stars - Modest)'), (1, '★☆☆☆☆ (1 Star - Deficient)')], attrs={'class': 'w-full bg-surface-container-low p-2.5 rounded text-on-surface font-body-md outline-none focus:ring-1 focus:ring-primary'}),
            'comment': forms.Textarea(attrs={'class': 'w-full bg-surface-container-low p-2.5 rounded text-on-surface font-body-md outline-none focus:ring-1 focus:ring-primary resize-none', 'rows': 3, 'placeholder': 'Describe the weight, casting clarity, acoustic chime or patina...'}),
        }


class ProductCreationForm(forms.ModelForm):
    image_url = forms.URLField(required=False, widget=forms.URLInput(attrs={
        'class': 'w-full bg-surface-container-low text-on-surface font-body-md p-2.5 rounded-lg focus:outline-none focus:ring-1 focus:ring-primary',
        'placeholder': 'https://example.com/brass-statue.jpg (Optional image URL)'
    }))

    class Meta:
        model = Product
        fields = ['product_name', 'category', 'price', 'original_price', 'stock_quantity', 'weight', 'dimensions', 'alloy_blend', 'patina_finish', 'description']
        widgets = {
            'product_name': forms.TextInput(attrs={'class': 'w-full bg-surface-container-low text-on-surface font-body-md p-2.5 rounded-lg focus:outline-none focus:ring-1 focus:ring-primary', 'placeholder': 'e.g. Amber Solaris Pendant Light'}),
            'category': forms.Select(attrs={'class': 'w-full bg-surface-container-low text-on-surface font-body-md p-2.5 rounded-lg focus:outline-none focus:ring-1 focus:ring-primary'}),
            'price': forms.NumberInput(attrs={'class': 'w-full bg-surface-container-low text-on-surface font-body-md p-2.5 rounded-lg focus:outline-none focus:ring-1 focus:ring-primary', 'placeholder': '1850.00'}),
            'original_price': forms.NumberInput(attrs={'class': 'w-full bg-surface-container-low text-on-surface font-body-md p-2.5 rounded-lg focus:outline-none focus:ring-1 focus:ring-primary', 'placeholder': '2100.00'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'w-full bg-surface-container-low text-on-surface font-body-md p-2.5 rounded-lg focus:outline-none focus:ring-1 focus:ring-primary', 'placeholder': '8'}),
            'weight': forms.TextInput(attrs={'class': 'w-full bg-surface-container-low text-on-surface font-body-md p-2.5 rounded-lg focus:outline-none focus:ring-1 focus:ring-primary', 'placeholder': 'Naval Brass • 4.8 kg'}),
            'dimensions': forms.TextInput(attrs={'class': 'w-full bg-surface-container-low text-on-surface font-body-md p-2.5 rounded-lg focus:outline-none focus:ring-1 focus:ring-primary', 'placeholder': '18" x 7" x 5"'}),
            'alloy_blend': forms.TextInput(attrs={'class': 'w-full bg-surface-container-low text-on-surface font-body-md p-2.5 rounded-lg focus:outline-none focus:ring-1 focus:ring-primary', 'placeholder': 'Naval Brass CuZn39Pb3'}),
            'patina_finish': forms.TextInput(attrs={'class': 'w-full bg-surface-container-low text-on-surface font-body-md p-2.5 rounded-lg focus:outline-none focus:ring-1 focus:ring-primary', 'placeholder': 'Antique Ochre / Polished Brass'}),
            'description': forms.Textarea(attrs={'class': 'w-full bg-surface-container-low text-on-surface font-body-md p-2.5 rounded-lg focus:outline-none focus:ring-1 focus:ring-primary resize-none', 'rows': 3, 'placeholder': 'Lost-wax casting technique infused with deep cognac Baltic amber gem setting...'}),
        }
