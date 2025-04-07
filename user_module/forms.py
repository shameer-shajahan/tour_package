from django import forms
from .models import CustomUser , Card  # Import your CustomUser model
from django import forms
from packager_module.models import Booking
from django.utils import timezone
from django.core.validators import MinValueValidator
from django import forms
from packager_module.models import Packager

class UserRegistrationForm(forms.ModelForm):
    """Custom registration form with role selection"""
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    role = forms.ChoiceField(choices=[('user', 'Regular User'), ('packager', 'Packager')])
    
    class Meta:
        model = CustomUser  # Use CustomUser instead of User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password != confirm_password:
            raise forms.ValidationError("Passwords don't match")
        
        return cleaned_data

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Packager
        fields = ['rating', 'reviews']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rating'].widget.attrs.update({'min': 0, 'max': 5})  # Optional: For rating validation

class BookingForm(forms.ModelForm):
    travel_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text='Select your travel date'
    )
    
    num_travelers = forms.IntegerField(
        validators=[MinValueValidator(1)],
        initial=1,
        help_text='Number of travelers (minimum 1)'
    )
    
    special_requests = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        help_text='Any special requests or notes'
    )

    class Meta:
        model = Booking
        fields = ['travel_date', 'num_travelers', 'special_requests']

class UserProfileForm(forms.ModelForm):
    """
    Form for updating user profile information
    """
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=100, required=False)
    last_name = forms.CharField(max_length=100, required=False)
    phone = forms.CharField(max_length=10, required=False)
    
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email' , 'phone']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('This email is already in use by another account.')
        return email
    
class CardForm(forms.ModelForm):
    card_number = forms.CharField(
        label='Card Number',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'XXXX XXXX XXXX XXXX',
            'maxlength': '19'
        }),
        required=True
    )
    card_holder = forms.CharField(
        label='Card Holder Name',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Name as it appears on card'
        }),
        required=True
    )
    expiry_date = forms.CharField(
        label='Expiration Date',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'MM/YY',
            'maxlength': '5'
        }),
        required=True
    )
    cvv = forms.CharField(
        label='CVV',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'XXX',
            'maxlength': '4'
        }),
        required=True
    )

    class Meta:
        model = Card
        fields = ['card_number', 'card_holder', 'expiry_date', 'cvv']
        
    def clean_card_number(self):
        card_number = self.cleaned_data.get('card_number')
        # Remove spaces if any
        card_number = card_number.replace(" ", "")
        # Basic validation - check if all digits
        if not card_number.isdigit():
            raise forms.ValidationError("Card number should contain only digits")
        # Check length
        if len(card_number) < 13 or len(card_number) > 19:
            raise forms.ValidationError("Invalid card number length")
        return card_number
        
    def clean_expiry_date(self):
        expiry_date = self.cleaned_data.get('expiry_date')
        # Check format
        if not '/' in expiry_date:
            raise forms.ValidationError("Expiry date should be in MM/YY format")
        try:
            month, year = expiry_date.split('/')
            month = int(month)
            year = int(year)
            # Check if month is valid
            if month < 1 or month > 12:
                raise forms.ValidationError("Month should be between 1 and 12")
        except ValueError:
            raise forms.ValidationError("Expiry date should be in MM/YY format")
        return expiry_date
        
    def clean_cvv(self):
        cvv = self.cleaned_data.get('cvv')
        # Check if all digits
        if not cvv.isdigit():
            raise forms.ValidationError("CVV should contain only digits")
        # Check length
        if len(cvv) < 3 or len(cvv) > 4:
            raise forms.ValidationError("CVV should be 3 or 4 digits")
        return cvv