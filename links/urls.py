from django.urls import path
from . import views


urlpatterns = [
    path('create/', views.create_link, name='create-link'),
    path('', views.links, name='links'),
    path('delete/', views.delete_link, name='delete_link'),
]