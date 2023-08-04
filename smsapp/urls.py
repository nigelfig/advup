from django.urls import path
from . import views


urlpatterns = [
    path('<int:reviewpk>/', views.sms_response, name='sms-sender'),
    path('comp/<int:reviewpk>/', views.computer_sms_response, name='computer-sms-sender'),
    path('campaignsender/<int:reviewpk>/', views.sms_campaign_sender, name='sms-campaign-sender'),
    path('compcustom/<int:reviewpk>/', views.computer_custom_sms_response, name='computer-custom-sms-sender'),    
]