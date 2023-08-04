from django.urls import path
from .views import PaymentView, updateTransactions

app_name = 'memberships'

urlpatterns = [
    path('payment/', PaymentView, name="payment"),
    path('update-transactions/<subscription_id>', updateTransactions, name="update-transactions"),
]
