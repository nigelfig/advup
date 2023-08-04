from django.urls import path
from . import views


urlpatterns = [
    path('send/', views.send_campaign, name='send_campaign'),
    path('', views.campaigns, name='campaigns'),
    path('schedule/', views.schedule_campaign, name='schedule_campaign'),
    path('cancel/', views.cancel_scheduled_campaign, name='cancel_scheduled_campaign'),
]