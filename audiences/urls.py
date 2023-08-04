from django.urls import path
from . import views

urlpatterns = [
    path('', views.audiences, name='audiences'),
    path('delete/', views.delete_audience, name='delete_audience'),
    path('create/', views.create_audience, name='create_audience'),
    path('<int:audiencepk>/subs/', views.subs, name='subs'),
    path('unsubscribers/', views.unsubscribers, name='unsubscribers'),
    path('unsubscribe/', views.unsubscribe_customer, name='unsubscribe_customer'),
    path('resubscribe/', views.resubscribe, name='resubscribe'),
    path('remove/', views.remove_subscriber, name='remove_subscriber'),
    path('upload/', views.upload_subscribers, name='upload'),
    path('add/', views.add_subscriber, name='add_subscriber'),

]