from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()
from .utils import unique_slug_generator
from django.db.models.signals import pre_save
from links.models import ReviewLinkType

# Create your models here.
class Place(models.Model):
    placeid = models.CharField(max_length=255)
    placename = models.CharField(max_length=255)
    basic_advup = models.BooleanField(default=False)
    slug = models.SlugField(blank=True)
    address = models.TextField()
    country = models.CharField(max_length=2)
    review_number = models.CharField(default="no number", max_length=20)
    store_number = models.CharField(default="no number listed", max_length=30)
    latitude = models.FloatField()
    longitude = models.FloatField()
    create_date = models.DateTimeField()
    businessperson = models.ManyToManyField(User)
    has_number = models.BooleanField(default=False)
    monthly_sms = models.IntegerField(default=2000)
    monthly_sub_uploads = models.IntegerField(default=2000)
    total_links_remaining = models.IntegerField(default=100)
    monthly_sms_limit = models.IntegerField(default=2000)
    monthly_sub_uploads_limit = models.IntegerField(default=2000)
    total_links_limit = models.IntegerField(default=100)
    main_review_type = models.ForeignKey(ReviewLinkType, blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.placename
    
class Messaging(models.Model):
    place = models.OneToOneField(Place, on_delete=models.CASCADE)
    review_copy = models.TextField(max_length=160)
    no_match_reply = models.TextField(max_length=160, default="")
    want_feedback = models.BooleanField(default=False)
    feedback_copy = models.TextField(max_length=160, default="")
    
    def __str__(self):
        return self.place.placename


def pre_save_post_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)

pre_save.connect(pre_save_post_receiver, sender=Place)

class PlaceDetail(models.Model):
    place = models.OneToOneField(Place, on_delete=models.CASCADE)
    place_map = models.ImageField(null=True, blank=True)
    formatted_store_number = models.CharField(max_length=20, blank=True, null=True)
    unformatted_store_number = models.BigIntegerField(blank=True, null=True)
    google_rating = models.FloatField()
    google_reviews_total = models.IntegerField()
    store_category = models.CharField(max_length=250, blank=True, null=True,)
    website = models.CharField(max_length=500)
    hours_mon = models.CharField(max_length=250)
    hours_tue = models.CharField(max_length=250)
    hours_wed = models.CharField(max_length=250)
    hours_thu = models.CharField(max_length=250)
    hours_fri = models.CharField(max_length=250)
    hours_sat = models.CharField(max_length=250)
    hours_sun = models.CharField(max_length=250)

    def __str__(self):
        return self.website