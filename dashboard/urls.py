from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('data/', views.get_data, name='data'),
    path('<int:placepk>/', views.dashboard_multi, name='dashboard-multi'),
    path('data/<int:placeid>/', views.get_data_multi, name='data-multi'),
]