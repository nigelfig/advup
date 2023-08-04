from django.db import models
from stores.models import Place

# Create your models here.
class Review(models.Model):
    reviewer_name = models.CharField(max_length=100)
    reviewer_photo_url = models.CharField(max_length=500)
    relative_time_description = models.CharField(max_length=100)
    rating = models.IntegerField()
    review_text = models.TextField()
    store = models.ForeignKey(Place, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
