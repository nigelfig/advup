from django.urls import path
from . import views

urlpatterns = [
    path('', views.your_stores, name='your-stores'),
    path('create/', views.create, name='create'),
]