from django.urls import path
from . import views

urlpatterns = [
    path('<slug:slug>/', views.shop, name='shop'),
    path('<slug:slug>/recommend/', views.recommend_shop, name='recommend'),
    path('<slug:slug>/feedback/', views.shop_feedback, name='shop_feedback'),
    path('<slug:slug>/thanks/', views.feedback_thanks, name='feedback_thanks'),
]