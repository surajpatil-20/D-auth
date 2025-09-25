from django.urls import path
from . import views
from django.contrib import admin

urlpatterns = [
    path('', views.home_view, name="home"),
    path("logout/", views.logout_view, name="logout"),
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("activate/<uidb64>/<token>/", views.activate_view, name="activate"),
]
