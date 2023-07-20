from django.urls import path
from knox import views as knox_views

from . import views

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", knox_views.LogoutView.as_view(), name="logout"),
    path("logoutall/", knox_views.LogoutAllView.as_view(), name="logoutall"),
    path(
        "register/", views.RegisterViewSet.as_view({"post": "create"}), name="register"
    ),
    path("profile/", views.ProfileViewSet.as_view({"get": "retrieve"}), name="profile"),
    path(
        "change-password/",
        views.ChangePasswordView.as_view({"put": "update"}),
        name="change-password",
    ),
]
