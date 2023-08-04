from django.urls import path
from . import views


urlpatterns = [
    path('update/', views.update_review, name='updatereview'),
    path('', views.send_review, name='sendreview'),
    path('custom/', views.custom_sms, name='custom_sms'),
]