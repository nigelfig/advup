# Create your tasks here
from __future__ import absolute_import, unicode_literals

from celery import shared_task

from stores.models import Place
from audiences.models import Audience, Subscriber, GlobalUnsubscriber
from campaigns.models import Campaign
from twilio.rest import Client
from django.shortcuts import get_object_or_404
import re
from django.conf import settings
from datetime import datetime, timedelta, timezone

@shared_task
def text_campaign(reviewpk, your_audience_id, campaign_id):
    # eventually updated to validate user owns audience

    your_audience = get_object_or_404(Audience, id=your_audience_id)
    campaign = get_object_or_404(Campaign, id=campaign_id)
    place = get_object_or_404(Place, pk=reviewpk)
    dont_contacts = GlobalUnsubscriber.objects.filter(place=place).values('unsubscriber_number')
    subscribers = Subscriber.objects.filter(audience=your_audience).exclude(phone_number__in=dont_contacts)
    campaign_sms = campaign.campaign_sms
    

    reviewnum = place.review_number

    ACCOUNT_SID = settings.TWILIO_ACCOUNT_SID
    AUTH_TOKEN = settings.TWILIO_AUTH_TOKEN
    client = Client(ACCOUNT_SID, AUTH_TOKEN)

    your_campaign_links = re.findall('adva\.co/[a-zA-Z0-9_\.-]+', campaign_sms)

    if your_campaign_links:
        campaign_link = your_campaign_links[0]
        campaign.campaign_link = campaign_link
    
    campaign.audience_size = len(subscribers)

    failed_sms = 0
    successful_sms = 0
    
    for subscriber in subscribers:
        try:
            remaining_sms = place.monthly_sms
            if remaining_sms > 0:
                subscriber_num = subscriber.phone_number
                new_sms = campaign_sms.replace("*|FNAME|*", subscriber.first_name)
                new_sms = new_sms.replace("*|LNAME|*", subscriber.last_name)
                client.messages.create(
                    to= subscriber_num,
                    from_=reviewnum,
                    body=new_sms
                )
                successful_sms += 1
                place.monthly_sms -= 1
                place.save()
        except:
            failed_sms += 1
    
    campaign.successful_sends = successful_sms
    campaign.failed_sends = failed_sms
    campaign.campaign_status = 'SENT'

    campaign.save()

    return None


@shared_task
def scheduled_thirty():

    startdate = datetime.today().replace(tzinfo=timezone.utc)
    enddate = startdate + timedelta(minutes=45)
    campaigns = Campaign.objects.filter(was_scheduled=True, scheduled_sent_to_celery=False, create_date__range=[startdate, enddate])

    for campaign in campaigns:
        reviewpk = campaign.audience.store.id
        your_audience_id = campaign.audience.id
        campaign_id = campaign.id
        scheduled_time_utc = campaign.create_date.replace(tzinfo=timezone.utc)
        print(reviewpk, your_audience_id, campaign_id)
        celery_task = text_campaign.apply_async((reviewpk, your_audience_id, campaign_id), eta=scheduled_time_utc)
        campaign.celery_task_id = celery_task.id
        campaign.scheduled_sent_to_celery = True
        campaign.save()


    return None