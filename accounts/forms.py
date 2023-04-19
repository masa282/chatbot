from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django import forms

class CustomUserCreationForm(UserCreationForm):
    error_messages = {
        "password_mismatch": ("The two password fields didn’t match."),
    }

    username = forms.CharField(
        label=('Username'),
        max_length=30,
        widget=forms.TextInput(attrs={"autocomplete": "username",
                                      #"class": "input-form",
                                      "id": "username",
                                      "name": "username",
                                      'required': True}),
    )

    email = forms.EmailField(
        label=("Email"),
        max_length=127,
        widget=forms.EmailInput(attrs={"autocomplete": "email",
                                       #"class": "input-form",
                                       "id": "email",
                                       "name": "email",
                                       'required': True}),
    )

    password1 = forms.CharField(
        label=("Password"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password",
                                          #"class": "input-form",
                                          "id": "password",
                                          "name": "password",
                                          'required': True}),
        strip=False,
    )

    password2 = forms.CharField(
        label=("Password confirmation"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password",
                                          #"class": "input-form",
                                          "id":"confirm-password",
                                          "name":"confirm-password",
                                          'required': True}),
        strip=False,
        help_text=("Enter the same password as before, for verification."),
    )

    class Meta:
        model = CustomUser
        fields = ["username", "email", "password1", "password2"]