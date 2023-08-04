from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

# Create your models here.
class Link(models.Model):
    link_id = models.TextField()
    long_url = models.TextField()
    short_url = models.CharField(max_length=60)
    create_date = models.DateTimeField(auto_now_add=True)
    store = models.ForeignKey('stores.Place', on_delete=models.CASCADE)

    def __str__(self):
        return self.short_url

class ReviewLinkType(models.Model):
    FEED = 'FEED'
    GOOG = 'GOOG'
    FB = 'FB'
    YELP = 'YELP'
    REVIEW_LINK_TYPES = (
        (FEED, 'Feeback'),
        (GOOG, 'Google'),
        (FB, 'Facebook'),
        (YELP, 'Yelp'),
    )
    review_link_type = models.CharField(
        choices=REVIEW_LINK_TYPES,
        max_length=30,
        unique=True,
    )


    def __str__(self):
        return self.review_link_type

class ReviewLink(models.Model):
    link_id = models.TextField()
    long_url = models.TextField()
    short_url = models.CharField(max_length=60)
    store = models.ForeignKey('stores.Place', on_delete=models.CASCADE)
    review_link_type = models.ForeignKey(ReviewLinkType, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['store', 'review_link_type']

    def __str__(self):
        return self.short_url