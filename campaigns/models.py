from django.db import models
from audiences.models import Audience

# # Create your models here.
class Campaign(models.Model):
    SENDING = 'SENDING'
    SCHEDULED = 'SCHEDULED'
    SENT = 'SENT'
    CANCELED = 'CANCELED'
    INCOMPLETED = 'INCOMPLETED'

    CAMPAIGN_STATUS_CHOICES = [
        (SENDING, 'Sending'),
        (SCHEDULED, 'Scheduled'),
        (SENT, 'Sent'),
        (CANCELED, 'Canceled'),
        (INCOMPLETED, 'Incompleted'),
    ]
    campaign_status = models.CharField(
        max_length=11,
        choices=CAMPAIGN_STATUS_CHOICES,
        null=True,
        blank=True
    )
    campaign_name = models.CharField(max_length=50)
    campaign_sms = models.TextField(max_length=160)
    campaign_link = models.CharField(max_length=100, blank=True, default='')
    create_date = models.DateTimeField()
    audience = models.ForeignKey(Audience, on_delete=models.CASCADE, null=True, blank=True)
    audience_size = models.IntegerField(null=True, blank=True)
    successful_sends = models.IntegerField(null=True, blank=True)
    failed_sends = models.IntegerField(null=True, blank=True)
    was_scheduled = models.BooleanField(default=False)
    scheduled_sent_to_celery = models.BooleanField(default=False)
    celery_task_id = models.CharField(max_length=255, unique=True, null=True, blank=True)

    def __str__(self):
        return self.campaign_name
