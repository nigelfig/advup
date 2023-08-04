from django.shortcuts import reverse, redirect
from django.http import HttpResponse, HttpResponseRedirect
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from stores.models import Place, Messaging
from audiences.models import Audience, Subscriber, GlobalUnsubscriber
from dashboard.models import Stat
from campaigns.models import Campaign
import re
from django.shortcuts import render, redirect, get_object_or_404
from twilio.request_validator import RequestValidator
from django.contrib import messages
from django.utils import timezone as tzone
import pytz
from django_twilio.decorators import twilio_view
from django.conf import settings
from django.contrib.auth.decorators import login_required

from .tasks import text_campaign
from datetime import datetime, timedelta, timezone


@login_required()
def sms_campaign_sender(request, reviewpk):
    if request.method == "POST":
        your_audience_id = request.POST["your_audience"]
        your_audience_id = int(your_audience_id)
        place = get_object_or_404(Place, pk=reviewpk, businessperson=request.user)
        your_audience = get_object_or_404(Audience, id=your_audience_id, store=place)
        
        
        if request.POST.get('datetimepicker12', False):
            campaign = Campaign()
            campaign.audience = your_audience
            campaign_sms = request.POST['campaignsms']
            campaign_name = request.POST['campaignname']
            campaign.campaign_name = campaign_name
            campaign.campaign_sms = campaign_sms


            string_time = request.POST['datetimepicker12']
            utc_offset = int(request.POST['time_offset'])
            scheduled_time_local = datetime.strptime(string_time, '%m/%d/%Y %I:%M %p')
            print(f"The scheduled time in local time zone is {scheduled_time_local}")
            scheduled_time_utc = scheduled_time_local + timedelta(minutes=utc_offset)
            scheduled_time_utc = scheduled_time_utc.replace(tzinfo=timezone.utc)
            print(f"The scheduled time in utc time is {scheduled_time_utc}")

            campaign.create_date = scheduled_time_utc
            campaign.campaign_status='SCHEDULED' 
            campaign.was_scheduled = True
            current_time = datetime.now().replace(tzinfo=timezone.utc)
            remaining_time = scheduled_time_utc - current_time
            remaining_minutes = remaining_time.total_seconds() / 60
            print(f"The remaining time is {remaining_minutes} minutes")
            
            
            if remaining_minutes < 45:
                campaign.save()
                campaign_id = campaign.id
                celery_task = text_campaign.apply_async((reviewpk, your_audience_id, campaign_id), eta=scheduled_time_utc)
                campaign.celery_task_id = celery_task.id
                campaign.scheduled_sent_to_celery = True
            campaign.save()

            message_confirmation = "AdvantageUp has scheduled your text message campaign."
            messages.info(request, message_confirmation)

        else:
            campaign = Campaign()
            campaign.audience = your_audience
            campaign_sms = request.POST['campaignsms']
            campaign_name = request.POST['campaignname']
            campaign.campaign_name = campaign_name
            campaign.campaign_sms = campaign_sms
            campaign.create_date = tzone.now()
            campaign.campaign_status='SENDING' 
            campaign.save()

            campaign_id = campaign.id
        
            celery_task = text_campaign.delay(reviewpk, your_audience_id, campaign_id)
            campaign.celery_task_id = celery_task.id
            campaign.save()

            message_confirmation = "AdvantageUp has sent out your text message campaign."
            messages.info(request, message_confirmation)

        return redirect('campaigns', placepk=reviewpk)



    message_confirmation = "There was an issue sending through your message, if it persists contact support@advantageup.com"
    messages.info(request, message_confirmation)    
    return redirect('send_campaign', placepk=reviewpk)

@login_required()
def computer_custom_sms_response(request, reviewpk):
    if request.method == "POST":
        place = get_object_or_404(Place, pk=reviewpk, businessperson=request.user)
        messaging = get_object_or_404(Messaging, place=place)
        reviewnum = place.review_number

        # parse phone number
        userphonenumber = request.POST['userphonenumber']
        sendnum_ary = re.findall('[0-9]+', userphonenumber)
        sendnum = "".join(sendnum_ary)
        phonenum = "+1" + sendnum

        customsms = request.POST['customsms']            

        # put your own credentials here
        ACCOUNT_SID = settings.TWILIO_ACCOUNT_SID
        AUTH_TOKEN = settings.TWILIO_AUTH_TOKEN
        client = Client(ACCOUNT_SID, AUTH_TOKEN)

        client.messages.create(
            to= phonenum,
            from_=reviewnum,
            body=customsms
        )

        stat = Stat()
        stat.place = place
        stat.business_number = reviewnum 
        stat.customer_number = phonenum
        stat.feedback_on = False #review or feedback
        stat.message_category = "REQU" 
        stat.message = customsms
        stat.created_at = tzone.now()
        stat.save()
        
        message_confirmation = "AdvantageUp sent your custom text message to your customer."
        messages.info(request, message_confirmation)
        return redirect('custom_sms', placepk=reviewpk)


    message_confirmation = "There was an issue sending through your message, if it persists contact support@advantageup.com"
    messages.info(request, message_confirmation)    
    return redirect('custom_sms', placepk=reviewpk)



@login_required()
def computer_sms_response(request, reviewpk):
    if request.method == "POST":
        place = get_object_or_404(Place, pk=reviewpk, businessperson=request.user)
        messaging = get_object_or_404(Messaging, place=place)
        reviewnum = place.review_number
        reviewcopy = messaging.review_copy
        no_match_reply = messaging.no_match_reply
        # parse phone number
        message_body = request.POST['Body']
        sendnum_ary = re.findall('[0-9]+', message_body)
        sendnum = "".join(sendnum_ary)
        phonenum = "+1" + sendnum


        # put your own credentials here
        ACCOUNT_SID = settings.TWILIO_ACCOUNT_SID
        AUTH_TOKEN = settings.TWILIO_AUTH_TOKEN
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        if messaging.want_feedback == False:
            client.messages.create(
                to= phonenum,
                from_=reviewnum,
                body=reviewcopy
            )

            stat = Stat()
            stat.place = place
            stat.business_number = reviewnum 
            stat.customer_number = phonenum
            stat.feedback_on = False #review or feedback
            stat.message_category = "REQU" 
            stat.message = reviewcopy
            stat.created_at = tzone.now()
            stat.save()
            
            message_confirmation = "AdvantageUp sent a text message to customer requesting a review."
            messages.info(request, message_confirmation)
            return redirect('sendreview', placepk=reviewpk)

        if messaging.want_feedback == True: 
            feedbackcopy = messaging.feedback_copy
            client.messages.create(
                to= phonenum,
                from_=reviewnum,
                body=feedbackcopy
            )
            stat = Stat()
            stat.place = place
            stat.business_number = reviewnum 
            stat.customer_number = phonenum
            stat.feedback_on = True #review or feedback
            stat.message_category = "REQU"
            stat.message = feedbackcopy
            stat.created_at = tzone.now()
            stat.save()

            message_confirmation = "AdvantageUp sent a text message to customer requesting feedback."
            messages.info(request, message_confirmation)
            return redirect('sendreview', placepk=reviewpk)

    message_confirmation = "There was an issue sending through your message, if it persists contact support@advantageup.com"
    messages.info(request, message_confirmation)    
    return redirect('sendreview', placepk=reviewpk)

@twilio_view
def sms_response(request, reviewpk):
    if request.method == "POST":
        # put your own credentials here
        ACCOUNT_SID = settings.TWILIO_ACCOUNT_SID
        AUTH_TOKEN = settings.TWILIO_AUTH_TOKEN
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        
        place = get_object_or_404(Place, pk=reviewpk)
        umessage_body = str(request.POST['Body']).upper()
        print(umessage_body)
        if ' STOP' in umessage_body or  'STOP ' in umessage_body or umessage_body == 'STOP' or umessage_body == 'STOPALL' or 'UNSUBSCRIBE' in umessage_body or umessage_body == 'CANCEL' or umessage_body == 'END' or umessage_body == 'QUIT':
            place_num = request.POST['To']

            GlobalUnsubscriber.objects.update_or_create(
                unsubscriber_number = request.POST['From'],
                place = place
            )

            resp = MessagingResponse()
            return HttpResponse(str(resp))

        elif umessage_body == 'START' or umessage_body == 'YES' or umessage_body ==  'UNSTOP':
            GlobalUnsubscriber.objects.filter(unsubscriber_number=request.POST['From'], place=place).delete()
            resp = MessagingResponse()
            return HttpResponse(str(resp))



        place = get_object_or_404(Place, pk=reviewpk)
        messaging = get_object_or_404(Messaging, place=place)
        reviewnum = place.review_number
        reviewcopy = messaging.review_copy
        no_match_reply = messaging.no_match_reply
        # parse phone number
        message_body = request.POST['Body']
        sendnum_ary = re.findall('[0-9]+', message_body)
        sendnum = "".join(sendnum_ary)
        phonenum = "+1" + sendnum
        final_sendnum = "+" + sendnum
        lower_mb = message_body.lower()
        #feedback flow
        if (messaging.want_feedback == True and "review" not in lower_mb) or ("feedback" in lower_mb):
            feedbackcopy = messaging.feedback_copy
            #working
            if len(sendnum) == 10:
                client.messages.create(
                    to= phonenum,
                    from_=reviewnum,
                    body=feedbackcopy
                )
                stat = Stat()
                stat.place = place
                stat.business_number = reviewnum 
                stat.customer_number = phonenum
                stat.feedback_on = True #review or feedback
                stat.message_category = "REQU"
                stat.message = feedbackcopy
                stat.created_at = tzone.now()
                stat.save()

                message_confirmation = "AdvantageUp sent a text message to customer requesting feedback."
                resp = MessagingResponse()
                resp.message(message_confirmation)
                return HttpResponse(str(resp), content_type='text/xml')

            #working
            elif len(sendnum) == 11:
                client.messages.create(
                    to= final_sendnum,
                    from_=reviewnum,
                    body=feedbackcopy
                )

                stat = Stat()
                stat.place = place
                stat.business_number = reviewnum 
                stat.customer_number = final_sendnum
                stat.feedback_on = True #review or feedback
                stat.message_category = "REQU"
                stat.message = feedbackcopy
                stat.created_at = tzone.now()
                stat.save()

                message_confirmation = "AdvantageUp sent a text message to customer requesting feedback."
                resp = MessagingResponse()
                resp.message(message_confirmation)
                return HttpResponse(str(resp), content_type='text/xml')
            
            #working
            else:
                customernum = request.POST['From']
                businessnum = request.POST['To']
                customer_message = request.POST['Body']

                stat = Stat()
                stat.place = place
                stat.business_number = businessnum 
                stat.customer_number = customernum
                stat.feedback_on = True #review or feedback
                stat.message_category = "REPL"
                stat.message = customer_message
                stat.created_at = tzone.now()
                stat.save()

                resp = MessagingResponse()
                resp.message(no_match_reply)
                return HttpResponse(str(resp), content_type='text/xml')

        else:
            #working
            if len(sendnum) == 10:
                client.messages.create(
                    to= phonenum,
                    from_=reviewnum,
                    body=reviewcopy
                )

                stat = Stat()
                stat.place = place
                stat.business_number = reviewnum 
                stat.customer_number = phonenum
                stat.feedback_on = False #review or feedback
                stat.message_category = "REQU" 
                stat.message = reviewcopy
                stat.created_at = tzone.now()
                stat.save()
                
                message_confirmation = "AdvantageUp sent a text message to customer requesting a review."
                resp = MessagingResponse()
                resp.message(message_confirmation)
                return HttpResponse(str(resp), content_type='text/xml')

            #working
            elif len(sendnum) == 11:
                client.messages.create(
                    to= final_sendnum,
                    from_=reviewnum,
                    body=reviewcopy
                )

                stat = Stat()
                stat.place = place
                stat.business_number = reviewnum 
                stat.customer_number = final_sendnum
                stat.feedback_on = False #review or feedback
                stat.message_category = "REQU"
                stat.message = reviewcopy
                stat.created_at = tzone.now()
                stat.save()

                message_confirmation = "AdvantageUp sent a text message to customer requesting a review."
                resp = MessagingResponse()
                resp.message(message_confirmation)
                return HttpResponse(str(resp), content_type='text/xml')

            #working
            else:
                customernum = request.POST['From']
                businessnum = request.POST['To']
                customer_message = request.POST['Body']

                stat = Stat()
                stat.place = place
                stat.business_number = businessnum 
                stat.customer_number = customernum
                stat.feedback_on = False #review or feedback
                stat.message_category = "REPL"
                stat.message = customer_message
                stat.created_at = tzone.now()
                stat.save()

                resp = MessagingResponse()
                resp.message(no_match_reply)
                return HttpResponse(str(resp), content_type='text/xml')


