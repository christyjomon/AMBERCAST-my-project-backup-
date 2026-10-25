import re
from django import forms
from django.core.validators import EmailValidator
from django.contrib.auth import authenticate
from .models import User, Product, Review, Order

def validate_name(value, field_name="Name"):
    """
    Allow alphabets and spaces only.
    Remove leading/trailing spaces and prevent blank or whitespace-only input.
    """
    if not value or not str(value).strip():
        raise forms.ValidationError(f"{field_name} cannot be empty or contain only spaces.")
    cleaned = re.sub(r'\s+', ' ', str(value).strip())
    if not re.fullmatch(r'^[A-Za-z ]+$', cleaned):
        raise forms.ValidationError(f"{field_name} must contain only alphabets and spaces.")
    return cleaned

def validate_mobile(value):
    """
    Accept exactly 10 digits; reject alphabets and special characters.
    """
    if not value or not str(value).strip():
        raise forms.ValidationError("Mobile number is required.")
    raw = str(value).strip()
    # Normalize optional country code prefix for Pan-India numbers
    if raw.startswith('+91'):
        raw = raw[3:].strip()
    elif raw.startswith('91') and len(raw) == 12:
        raw = raw[2:].strip()

    if re.search(r'[a-zA-Z]', raw):
        raise forms.ValidationError("Mobile number cannot contain alphabets.")
    if re.search(r'[^0-9\s]', raw):
        raise forms.ValidationError("Mobile number cannot contain special characters.")

    digits_only = re.sub(r'\s+', '', raw)
    if not re.fullmatch(r'^\d{10}$', digits_only):
        raise forms.ValidationError("Mobile number must be exactly 10 digits.")
    return digits_only

def validate_pincode(value):
    """
    Accept exactly 6 digits for Indian addresses; reject invalid formats.
    """
    if not value or not str(value).strip():
        raise forms.ValidationError("PIN code is required for address verification.")
    raw = str(value).strip()
    if re.search(r'[a-zA-Z]', raw):
        raise forms.ValidationError("PIN code cannot contain alphabets.")
    digits_only = re.sub(r'\s+', '', raw)
    if not re.fullmatch(r'^\d{6}$', digits_only):
        raise forms.ValidationError("PIN code must be exactly 6 digits.")
    return digits_only

def validate_strong_password(password):
    """
    Minimum 8 characters, including uppercase, lowercase, number, and special character.
    IMPORTANT: Never strip or modify the password string!
    """
    if not password or len(password) < 8:
        raise forms.ValidationError("Password must be at least 8 characters long.")
    if not re.search(r'[A-Z]', password):
        raise forms.ValidationError("Password must include at least one uppercase letter (A-Z).")
    if not re.search(r'[a-z]', password):
        raise forms.ValidationError("Password must include at least one lowercase letter (a-z).")
    if not re.search(r'[0-9]', password):
        raise forms.ValidationError("Password must include at least one number (0-9).")
    if not re.search(r'[^A-Za-z0-9]', password):
        raise forms.ValidationError("Password must include at least one special character (e.g. !@#$%^&*).")
    return password


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full bg-surface-container-low focus:bg-surface-container-lowest text-on-surface px-space-md py-space-sm rounded font-body-md text-body-md outline-none transition-all shadow-sm focus:ring-1 focus:ring-primary',
            'placeholder': '••••••••••••',
            'required': 'required',
            'minlength': '8',
            'autocomplete': 'new-password'
        }),
        help_text="Min. 8 characters with uppercase, lowercase, number, and special character."
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full bg-surface-container-low focus:bg-surface-container-lowest text-on-surface px-space-md py-space-sm rounded font-body-md text-body-md outline-none transition-all shadow-sm focus:ring-1 focus:ring-primary',
            'placeholder': '••••••••••••',
            'required': 'required',
            'minlength': '8',
            'autocomplete': 'new-password'
        })
    )
    pincode = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-surface-container-low focus:bg-surface-container-lowest text-on-surface px-space-md py-space-sm rounded font-body-md text-body-md outline-none transition-all shadow-sm focus:ring-1 focus:ring-primary',
            'placeholder': '400006',
            'pattern': r'^[0-9]{6}$',
            'maxlength': '6',
            'minlength': '6',
            'title': 'Enter a 6-digit Indian PIN code',
            'required': 'required'
        }),
        help_text="6-digit postal PIN code"
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'address']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full bg-surface-container-low focus:bg-surface-container-lowest text-on-surface px-space-md py-space-sm rounded font-body-md text-body-md outline-none transition-all shadow-sm focus:ring-1 focus:ring-primary', 
                'placeholder': 'e.g. John',
                'pattern': r'^[A-Za-z ]+$',
                'title': 'Alphabets and spaces only',
                'required': 'required'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full bg-surface-container-low focus:bg-surface-container-lowest text-on-surface px-space-md py-space-sm rounded font-body-md text-body-md outline-none transition-all shadow-sm focus:ring-1 focus:ring-primary', 
                'placeholder': 'e.g. Doe',
                'pattern': r'^[A-Za-z ]+$',
                'title': 'Alphabets and spaces only',
                'required': 'required'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full bg-surface-container-low focus:bg-surface-container-lowest text-on-surface px-space-md py-space-sm rounded font-body-md text-body-md outline-none transition-all shadow-sm focus:ring-1 focus:ring-primary', 
                'placeholder': 'e.g. user@example.com',
                'required': 'required'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full bg-surface-container-low focus:bg-surface-container-lowest text-on-surface px-space-md py-space-sm rounded font-body-md text-body-md outline-none transition-all shadow-sm focus:ring-1 focus:ring-primary', 
                'placeholder': '9876543210',
                'pattern': r'^[0-9]{10}$',
                'maxlength': '10',
                'minlength': '10',
                'title': 'Exactly 10 digits required',
                'required': 'required'
            }),
            'address': forms.Textarea(attrs={
                'class': 'w-full bg-surface-container-low focus:bg-surface-container-lowest text-on-surface p-space-md rounded font-body-md text-body-md outline-none transition-all shadow-sm focus:ring-1 focus:ring-primary resize-none', 
                'rows': 3, 
                'placeholder': 'Delivery address street, locality, city, state',
                'required': 'required'
            }),
        }

    def clean_first_name(self):
        return validate_name(self.cleaned_data.get('first_name'), "First Name")

    def clean_last_name(self):
        return validate_name(self.cleaned_data.get('last_name'), "Last Name")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email or not email.strip():
            raise forms.ValidationError("Email address is required.")
        email = email.strip().lower()
        EmailValidator()(email)
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email address already exists. Please sign in or use a different email.")
        return email

    def clean_phone(self):
        return validate_mobile(self.cleaned_data.get('phone'))

    def clean_pincode(self):
        return validate_pincode(self.cleaned_data.get('pincode'))

    def clean_address(self):
        addr = self.cleaned_data.get('address')
        if not addr or not addr.strip():
            raise forms.ValidationError("Delivery address is required and cannot be empty.")
        return addr.strip()

    def clean_password(self):
        pwd = self.cleaned_data.get('password')
        return validate_strong_password(pwd)

    def clean(self):
        cleaned_data = super().clean()
        pwd = cleaned_data.get('password')
        cpwd = cleaned_data.get('confirm_password')
        if pwd and cpwd and pwd != cpwd:
            self.add_error('confirm_password', 'Passwords do not match. Please ensure both passwords match exactly.')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        # New users registering via public registration are always Customers
        user.role = 'Customer'
        user.is_staff = False
        user.is_superuser = False
        pincode = self.cleaned_data.get('pincode')
        if pincode and user.address and pincode not in user.address:
            user.address = f"{user.address.strip()} - {pincode}"
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    email = forms.CharField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full bg-surface-container-low focus:bg-surface-container-lowest text-on-surface px-space-md py-space-sm rounded font-body-md text-body-md outline-none transition-all shadow-sm focus:ring-1 focus:ring-primary',
            'placeholder': 'Enter your registered email address',
            'required': 'required',
            'autocomplete': 'email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full bg-surface-container-low focus:bg-surface-container-lowest text-on-surface px-space-md py-space-sm rounded font-body-md text-body-md outline-none transition-all shadow-sm focus:ring-1 focus:ring-primary',
            'placeholder': '••••••••••••',
            'required': 'required',
            'autocomplete': 'current-password'
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email or not email.strip():
            raise forms.ValidationError("Email address cannot be empty or whitespace only.")
        return email.strip().lower()

    def clean_password(self):
        pwd = self.cleaned_data.get('password')
        if not pwd:
            raise forms.ValidationError("Password is required.")
        # NEVER STRIP OR MODIFY PASSWORD!
        return pwd


class UserProfileForm(forms.ModelForm):
    pincode = forms.CharField(
        max_length=6,
        min_length=6,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-surface-container-low text-on-surface p-2.5 rounded font-body-md border border-surface-container-high focus:outline-none focus:ring-1 focus:ring-primary',
            'placeholder': 'e.g. 400006',
            'pattern': r'^[0-9]{6}$',
            'maxlength': '6',
            'minlength': '6',
            'title': 'Enter a 6-digit PIN code'
        })
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'address']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full bg-surface-container-low text-on-surface p-2.5 rounded font-body-md border border-surface-container-high focus:outline-none focus:ring-1 focus:ring-primary',
                'pattern': r'^[A-Za-z ]+$',
                'title': 'Alphabets and spaces only',
                'required': 'required'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full bg-surface-container-low text-on-surface p-2.5 rounded font-body-md border border-surface-container-high focus:outline-none focus:ring-1 focus:ring-primary',
                'pattern': r'^[A-Za-z ]+$',
                'title': 'Alphabets and spaces only',
                'required': 'required'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full bg-surface-container-low text-on-surface p-2.5 rounded font-body-md border border-surface-container-high focus:outline-none focus:ring-1 focus:ring-primary',
                'pattern': r'^[0-9]{10}$',
                'maxlength': '10',
                'minlength': '10',
                'title': 'Exactly 10 digits required',
                'required': 'required'
            }),
            'address': forms.Textarea(attrs={
                'class': 'w-full bg-surface-container-low text-on-surface p-2.5 rounded font-body-md border border-surface-container-high focus:outline-none focus:ring-1 focus:ring-primary resize-none',
                'rows': 3,
                'required': 'required'
            }),
        }

    def clean_first_name(self):
        return validate_name(self.cleaned_data.get('first_name'), "First Name")

    def clean_last_name(self):
        return validate_name(self.cleaned_data.get('last_name'), "Last Name")

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            return validate_mobile(phone)
        return phone

    def clean_pincode(self):
        pincode = self.cleaned_data.get('pincode')
        if pincode and pincode.strip():
            return validate_pincode(pincode)
        return pincode

    def clean_address(self):
        addr = self.cleaned_data.get('address')
        if not addr or not addr.strip():
            raise forms.ValidationError("Delivery address is required and cannot be blank.")
        return addr.strip()

    def save(self, commit=True):
        user = super().save(commit=False)
        pincode = self.cleaned_data.get('pincode')
        if pincode and user.address and pincode not in user.address:
            user.address = f"{user.address.strip()} - {pincode}"
        if commit:
            user.save()
        return user


class CheckoutForm(forms.Form):
    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-surface-container-low focus:bg-surface-container-lowest text-on-surface px-space-md py-space-sm rounded font-body-md text-body-md outline-none transition-all shadow-sm border border-surface-container-high focus:border-primary',
            'id': 'first_name',
            'required': 'required',
            'pattern': r'^[A-Za-z ]+$',
            'title': 'First Name can only contain letters and spaces'
        })
    )
    last_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-surface-container-low focus:bg-surface-container-lowest text-on-surface px-space-md py-space-sm rounded font-body-md text-body-md outline-none transition-all shadow-sm border border-surface-container-high focus:border-primary',
            'id': 'last_name',
            'required': 'required',
            'pattern': r'^[A-Za-z ]+$',
            'title': 'Last Name can only contain letters and spaces'
        })
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'w-full pl-14 bg-surface-container-low focus:bg-surface-container-lowest text-on-surface pr-space-md py-space-sm rounded font-body-md text-body-md outline-none transition-all shadow-sm border border-surface-container-high focus:border-primary',
            'id': 'phone',
            'required': 'required',
            'pattern': r'^[0-9]{10}$',
            'maxlength': '10',
            'minlength': '10',
            'title': 'Contact phone must be exactly 10 digits'
        })
    )
    pincode = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-surface-container-low focus:bg-surface-container-lowest text-on-surface px-space-md py-space-sm rounded font-body-md text-body-md outline-none transition-all shadow-sm border border-surface-container-high focus:border-primary',
            'id': 'pincode',
            'required': 'required',
            'placeholder': 'e.g. 682001',
            'pattern': r'^[0-9]{6}$',
            'maxlength': '6',
            'minlength': '6',
            'title': 'PIN code must be exactly 6 digits'
        })
    )
    shipping_address = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full bg-surface-container-low focus:bg-surface-container-lowest text-on-surface p-space-md rounded font-body-md text-body-md outline-none transition-all shadow-sm border border-surface-container-high focus:border-primary resize-none',
            'id': 'shipping_address',
            'required': 'required',
            'rows': 3
        })
    )
    delivery_notes = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-surface-container-low focus:bg-surface-container-lowest text-on-surface px-space-md py-space-sm rounded font-body-md text-body-md outline-none transition-all shadow-sm border border-surface-container-high focus:border-primary',
            'id': 'delivery_notes'
        })
    )
    payment_method = forms.ChoiceField(
        choices=[('online', 'Online Payment'), ('cod', 'Cash On Delivery')],
        initial='online',
        required=False
    )
    voucher_code = forms.CharField(required=False)

    def clean_first_name(self):
        return validate_name(self.cleaned_data.get('first_name'), "First Name")

    def clean_last_name(self):
        return validate_name(self.cleaned_data.get('last_name'), "Last Name")

    def clean_phone(self):
        return validate_mobile(self.cleaned_data.get('phone'))

    def clean_pincode(self):
        return validate_pincode(self.cleaned_data.get('pincode'))

    def clean_shipping_address(self):
        addr = self.cleaned_data.get('shipping_address')
        if not addr or not addr.strip():
            raise forms.ValidationError("Delivery address is required and cannot be empty.")
        return addr.strip()

    def clean_delivery_notes(self):
        notes = self.cleaned_data.get('delivery_notes')
        return notes.strip() if notes else ""


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(
                choices=[
                    (5, '★★★★★ (5 Stars - Heirloom Masterwork)'), 
                    (4, '★★★★☆ (4 Stars - Exceptional)'), 
                    (3, '★★★☆☆ (3 Stars - Satisfactory)'), 
                    (2, '★★☆☆☆ (2 Stars - Modest)'), 
                    (1, '★☆☆☆☆ (1 Star - Deficient)')
                ], 
                attrs={
                    'class': 'w-full bg-surface-container-low p-2.5 rounded text-on-surface font-body-md outline-none focus:ring-1 focus:ring-primary',
                    'required': 'required'
                }
            ),
            'comment': forms.Textarea(
                attrs={
                    'class': 'w-full bg-surface-container-low p-2.5 rounded text-on-surface font-body-md outline-none focus:ring-1 focus:ring-primary resize-none', 
                    'rows': 3, 
                    'placeholder': 'Describe the weight, casting clarity, acoustic chime or patina...',
                    'required': 'required',
                    'minlength': '5'
                }
            ),
        }

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        try:
            rating_val = int(rating)
        except (ValueError, TypeError):
            raise forms.ValidationError("Rating must be a valid integer between 1 and 5.")
        if rating_val < 1 or rating_val > 5:
            raise forms.ValidationError("Rating must be between 1 and 5 stars.")
        return rating_val

    def clean_comment(self):
        comment = self.cleaned_data.get('comment')
        if not comment or not comment.strip():
            raise forms.ValidationError("Review comment cannot be empty or contain only whitespace.")
        cleaned = comment.strip()
        if len(cleaned) < 5:
            raise forms.ValidationError("Review comment must be at least 5 characters long.")
        return cleaned


class ProductForm(forms.ModelForm):
    image_url = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-surface-container-low text-on-surface font-body-md p-2.5 rounded-lg focus:outline-none focus:ring-1 focus:ring-primary',
            'placeholder': 'https://example.com/brass-statue.jpg (or image URL)'
        })
    )
    image_file = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'w-full bg-surface-container-low text-on-surface font-body-md p-2 rounded-lg focus:outline-none focus:ring-1 focus:ring-primary text-sm file:mr-3 file:py-1 file:px-3 file:rounded file:border-0 file:text-xs file:font-semibold file:bg-primary file:text-on-primary hover:file:bg-primary-container'
        })
    )

    class Meta:
        model = Product
        fields = [
            'product_name', 'category', 'price', 'original_price', 
            'stock_quantity', 'weight', 'dimensions', 'alloy_blend', 
            'patina_finish', 'description', 'is_available'
        ]
        widgets = {
            'product_name': forms.TextInput(attrs={
                'class': 'w-full bg-surface-container-low text-on-surface font-body-md p-2.5 rounded-lg focus:outline-none focus:ring-1 focus:ring-primary', 
                'placeholder': 'e.g. Handcrafted Brass Shiva Nataraja',
                'required': 'required'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full bg-surface-container-low text-on-surface font-body-md p-2.5 rounded-lg focus:outline-none focus:ring-1 focus:ring-primary'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'w-full bg-surface-container-low text-on-surface font-body-md p-2.5 rounded-lg focus:outline-none focus:ring-1 focus:ring-primary', 
                'placeholder': '4500.00',
                'step': '0.01',
                'min': '0.01',
                'required': 'required'
            }),
            'original_price': forms.NumberInput(attrs={
                'class': 'w-full bg-surface-container-low text-on-surface font-body-md p-2.5 rounded-lg focus:outline-none focus:ring-1 focus:ring-primary', 
                'placeholder': '5200.00',
                'step': '0.01',
                'min': '0.01'
            }),
            'stock_quantity': forms.NumberInput(attrs={
                'class': 'w-full bg-surface-container-low text-on-surface font-body-md p-2.5 rounded-lg focus:outline-none focus:ring-1 focus:ring-primary', 
                'placeholder': '8',
                'min': '0',
                'step': '1',
                'required': 'required'
            }),
            'weight': forms.TextInput(attrs={
                'class': 'w-full bg-surface-container-low text-on-surface font-body-md p-2.5 rounded-lg focus:outline-none focus:ring-1 focus:ring-primary', 
                'placeholder': 'Naval Brass • 4.8 kg'
            }),
            'dimensions': forms.TextInput(attrs={
                'class': 'w-full bg-surface-container-low text-on-surface font-body-md p-2.5 rounded-lg focus:outline-none focus:ring-1 focus:ring-primary', 
                'placeholder': '18" x 7" x 5"'
            }),
            'alloy_blend': forms.TextInput(attrs={
                'class': 'w-full bg-surface-container-low text-on-surface font-body-md p-2.5 rounded-lg focus:outline-none focus:ring-1 focus:ring-primary', 
                'placeholder': 'Naval Brass CuZn39Pb3'
            }),
            'patina_finish': forms.TextInput(attrs={
                'class': 'w-full bg-surface-container-low text-on-surface font-body-md p-2.5 rounded-lg focus:outline-none focus:ring-1 focus:ring-primary', 
                'placeholder': 'Antique Ochre / Polished Brass'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full bg-surface-container-low text-on-surface font-body-md p-2.5 rounded-lg focus:outline-none focus:ring-1 focus:ring-primary resize-none', 
                'rows': 3, 
                'placeholder': 'Lost-wax casting technique infused with intricate artisanal details...'
            }),
            'is_available': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-primary rounded border-outline-variant focus:ring-primary'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ['original_price', 'stock_quantity', 'weight', 'dimensions', 'alloy_blend', 'patina_finish', 'description', 'is_available']:
            if field_name in self.fields:
                self.fields[field_name].required = False
        if not self.instance or not self.instance.pk:
            self.fields['is_available'].initial = True
            self.fields['stock_quantity'].initial = 5
            self.fields['weight'].initial = '3.5 kg'
            self.fields['dimensions'].initial = '14" x 10"'
            self.fields['alloy_blend'].initial = '85-88% Copper CuZn Solid Brass'
            self.fields['patina_finish'].initial = 'Antique Brown Patina'

    def clean_product_name(self):
        name = self.cleaned_data.get('product_name')
        if not name or not name.strip():
            raise forms.ValidationError("Product name is required and cannot be empty or contain only spaces.")
        return name.strip()

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is None:
            raise forms.ValidationError("Product price is required.")
        if price <= 0:
            raise forms.ValidationError("Product price must be a positive amount greater than ₹0.")
        return price

    def clean_original_price(self):
        original_price = self.cleaned_data.get('original_price')
        if original_price is not None and original_price <= 0:
            raise forms.ValidationError("Original price must be greater than ₹0.")
        return original_price

    def clean_stock_quantity(self):
        stock = self.cleaned_data.get('stock_quantity')
        if stock is None:
            return 0
        if stock < 0:
            raise forms.ValidationError("Stock quantity cannot be negative.")
        return stock

    def clean_weight(self):
        w = self.cleaned_data.get('weight')
        return w.strip() if w else "3.5 kg"

    def clean_dimensions(self):
        d = self.cleaned_data.get('dimensions')
        return d.strip() if d else '14" x 10"'

    def clean_alloy_blend(self):
        a = self.cleaned_data.get('alloy_blend')
        return a.strip() if a else "85-88% Copper CuZn Solid Brass"

    def clean_patina_finish(self):
        p = self.cleaned_data.get('patina_finish')
        return p.strip() if p else "Antique Brown Patina"

    def clean_description(self):
        desc = self.cleaned_data.get('description')
        if desc and desc.strip():
            return desc.strip()
        p_name = self.cleaned_data.get('product_name') or 'Handcrafted Artifact'
        return f"Exquisite handcrafted brass artifact: {p_name}."

    def clean_image_url(self):
        url = self.cleaned_data.get('image_url')
        return url.strip() if url else ""

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('stock_quantity') is None:
            cleaned_data['stock_quantity'] = 1
        if not cleaned_data.get('patina_finish'):
            cleaned_data['patina_finish'] = "Antique Brown Patina"
        if not cleaned_data.get('weight'):
            cleaned_data['weight'] = "3.5 kg"
        if not cleaned_data.get('dimensions'):
            cleaned_data['dimensions'] = '14" x 10"'
        if not cleaned_data.get('alloy_blend'):
            cleaned_data['alloy_blend'] = "85-88% Copper CuZn Solid Brass"
        if not cleaned_data.get('description'):
            p_name = cleaned_data.get('product_name') or 'Handcrafted Artifact'
            cleaned_data['description'] = f"Exquisite handcrafted brass artifact: {p_name}."
        return cleaned_data


# Backward compatibility alias
ProductCreationForm = ProductForm


class UserAdminEditForm(forms.ModelForm):
    new_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full bg-surface-container-low text-on-surface font-body-md p-2.5 rounded-lg focus:outline-none focus:ring-1 focus:ring-primary',
            'placeholder': 'Leave blank to keep existing password',
            'minlength': '8'
        }),
        help_text="Optional: Enter a new password to reset this user's password (min 8 chars with uppercase, lowercase, digit, and special character)."
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'role', 'is_active', 'is_staff']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full bg-surface-container-low text-on-surface font-body-md p-2.5 rounded-lg focus:outline-none focus:ring-1 focus:ring-primary',
                'placeholder': 'First Name',
                'pattern': r'^[A-Za-z ]+$',
                'title': 'Alphabets and spaces only'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full bg-surface-container-low text-on-surface font-body-md p-2.5 rounded-lg focus:outline-none focus:ring-1 focus:ring-primary',
                'placeholder': 'Last Name',
                'pattern': r'^[A-Za-z ]+$',
                'title': 'Alphabets and spaces only'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full bg-surface-container-low text-on-surface font-body-md p-2.5 rounded-lg focus:outline-none focus:ring-1 focus:ring-primary',
                'placeholder': 'user@example.com',
                'required': 'required'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full bg-surface-container-low text-on-surface font-body-md p-2.5 rounded-lg focus:outline-none focus:ring-1 focus:ring-primary',
                'placeholder': '9876543210',
                'pattern': r'^[0-9]{10}$',
                'maxlength': '10',
                'minlength': '10',
                'title': 'Exactly 10 digits required'
            }),
            'address': forms.Textarea(attrs={
                'class': 'w-full bg-surface-container-low text-on-surface font-body-md p-2.5 rounded-lg focus:outline-none focus:ring-1 focus:ring-primary resize-none',
                'rows': 3,
                'placeholder': 'Shipping / Contact Address'
            }),
            'role': forms.Select(attrs={
                'class': 'w-full bg-surface-container-low text-on-surface font-body-md p-2.5 rounded-lg focus:outline-none focus:ring-1 focus:ring-primary'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-primary rounded border-outline-variant focus:ring-primary'
            }),
            'is_staff': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-primary rounded border-outline-variant focus:ring-primary'
            }),
        }

    def clean_first_name(self):
        val = self.cleaned_data.get('first_name')
        if val and val.strip():
            return validate_name(val, "First Name")
        return val

    def clean_last_name(self):
        val = self.cleaned_data.get('last_name')
        if val and val.strip():
            return validate_name(val, "Last Name")
        return val

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email or not email.strip():
            raise forms.ValidationError("Email address cannot be empty.")
        email = email.lower().strip()
        EmailValidator()(email)
        existing = User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
        if existing.exists():
            raise forms.ValidationError("Another user with this email address already exists.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and phone.strip():
            return validate_mobile(phone)
        return phone

    def clean_address(self):
        addr = self.cleaned_data.get('address')
        return addr.strip() if addr else ""

    def clean_new_password(self):
        pwd = self.cleaned_data.get('new_password')
        if pwd:
            return validate_strong_password(pwd)
        return pwd
