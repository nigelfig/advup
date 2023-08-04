from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='home'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
    path('login/', views.login, name='login'),
]