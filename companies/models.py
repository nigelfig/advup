from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

# Create your models here.
class Profile(models.Model):
    businessperson = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    phone_number= models.CharField(max_length=20)
    create_date = models.DateTimeField()
    def __str__(self):
        return self.company_name