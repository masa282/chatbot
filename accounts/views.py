from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import CustomUserCreationForm

# Create your views here.
class SignUpView(CreateView):
    template_name = "accounts/signup.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("accounts:login")