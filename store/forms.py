from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Order



class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)


# class OrderForm(forms.ModelForm):
#     class Meta:
#         model = Order
#         fields = ['address', 'phone_number', 'email']  # Add phone_number and email fields
    
#     phone_number = forms.CharField(
#         max_length=15, 
#         required=True, 
#         widget=forms.TextInput(attrs={'placeholder': 'Enter your phone number'})
#     )
#     email = forms.EmailField(
#         required=True, 
#         widget=forms.EmailInput(attrs={'placeholder': 'Enter your email address'})
#     )