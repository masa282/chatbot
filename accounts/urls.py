from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth import views as auth_view


app_name = "accounts"

urlpatterns = [
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("login/", auth_view.LoginView.as_view(
        template_name = "accounts/login.html",
        success_url = reverse_lazy("chat:index")), name="login"),
    path("logout/", auth_view.LogoutView.as_view(), name="logout"),
    path("mypage/", views.MypageView.as_view(), name="mypage"),
]