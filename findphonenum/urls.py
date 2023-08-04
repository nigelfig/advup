from django.urls import path
from .views import selectnumber

app_name = 'findphonenums'

urlpatterns = [
    path('<int:reviewpk>/find/', selectnumber, name="findnum"),
]
