from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView
from .forms import CustomUserCreationForm
from .models import CustomUser
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

# Create your views here.
class SignUpView(CreateView):
    template_name = "accounts/signup.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("accounts:login")

    def form_valid(self, form):
        user = form.save()
        self.object = user
        return super().form_valid(form)

    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)
    

@method_decorator(login_required, name='dispatch')
class MypageView(ListView):
    template_name = "accounts/mypage.html"

    def get_queryset(self):
        #queryset =.objects.filter(user=self.request.user)
        #return queryset
        pass