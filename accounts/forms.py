from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Profile  # <--- Import the new Profile model

class CustomUserCreationForm(UserCreationForm):
    """
    A custom form that inherits from UserCreationForm and adds
    email, fields with custom validation.
    """
    
    # 1. Define the email field explicitly so we can make it required
    email = forms.EmailField(required=True, help_text="Required. A valid email address.")

    class Meta(UserCreationForm.Meta):
        model = User
        # 2. Add fields to this list so they appear on the page
        fields = ('username', 'email')

    def clean_username(self):
        """
        Custom validation for username.
        """
        username = self.cleaned_data.get('username')
        
        # Rule 1: Minimum length
        if len(username) < 5:
            raise ValidationError("Username must be at least 5 characters long.")
            
        return username

# --- NEW FORM FOR BIRTHDAY ---
class BirthdayForm(forms.ModelForm):
    birthday = forms.DateField(
        required=True,
        help_text="Required. Enter your birthday!",
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    class Meta:
        model = Profile
        fields = ['birthday']