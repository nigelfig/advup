from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from stores.models import Place, Messaging
from memberships.models import UserMembership
from audiences.models import Audience
from django.contrib import messages
from sendreview.views import check_paid, check_base
from .models import Campaign
from links.models import Link
from django.conf import settings
import requests 
import json
from advantageup.celery import app
from django.views.decorators.http import require_POST

@login_required
@require_POST
def cancel_scheduled_campaign(request, placepk):
    campaign_id = int(request.POST["campaign_id"])
    campaign = get_object_or_404(Campaign, id=campaign_id, campaign_status='SCHEDULED')

    task_id = campaign.celery_task_id
    if task_id:
        app.control.revoke(task_id)

    campaign.delete()

    message_confirmation = "Campaign has been canceled and deleted"
    messages.info(request, message_confirmation)

    return redirect('campaigns', placepk=placepk)

# consider fixing messages_setup.html for style tag showing up in the body
@login_required()
def campaigns(request, placepk):
    if request.method == "POST":
        pass
    else:
        user_type = check_paid(request)
        if user_type.membership.membership_type == "FREE":
            return redirect('memberships:payment')
        else:
            store = get_object_or_404(Place, id=placepk, businessperson=request.user)
            update_day = store.create_date.day
            audiences = Audience.objects.filter(store=store).order_by('-create_date')
            campaigns = Campaign.objects.filter(audience__in=audiences).order_by('-create_date')
            link_metrics = []
            for campaign in campaigns:
                if campaign.campaign_link:
                    try:
                        link_id = get_object_or_404(Link, short_url=campaign.campaign_link).link_id
                        print(link_id)
                        url = "https://api.rebrandly.com/v1/links/" + link_id + "?apikey=" + settings.REBRANDLY_API_KEY

                        response = requests.request("GET", url)

                        link_data = response.json()
                        link_clicks = link_data["clicks"]
                        link_metrics.append(link_clicks)
                    except:
                        link_metrics.append("Not Trackable")
                else:
                    link_metrics.append("")


            campaign_data = zip(campaigns, link_metrics)
            my_base = check_base(request)
            return render(request, 'campaigns/campaigns.html', {
                "store": store,
                "update_day": update_day,
                "campaigns": campaign_data,
                "my_base": my_base,
                })

@login_required()
def send_campaign(request, placepk=False):
    if request.method == "POST":
        return HttpResponseRedirect(reverse('dashboard'))
    else:
        user_type = check_paid(request)
        if user_type.membership.membership_type == "FREE":
            return redirect('memberships:payment')
        else:
            store = get_object_or_404(Place, id=placepk, businessperson=request.user)
            update_day = store.create_date.day
            audiences = Audience.objects.filter(store=store)
            my_base = check_base(request)
            return render(request, 'campaigns/sendcampaign.html', {
                "store": store,
                "update_day": update_day,
                "audiences": audiences,
                "my_base": my_base,
                })

@login_required()
def schedule_campaign(request, placepk=False):
    if request.method == "POST":
        return HttpResponseRedirect(reverse('dashboard'))
    else:
        user_type = check_paid(request)
        if user_type.membership.membership_type == "FREE":
            return redirect('memberships:payment')
        else:
            store = get_object_or_404(Place, id=placepk, businessperson=request.user)
            update_day = store.create_date.day
            audiences = Audience.objects.filter(store=store)
            my_base = check_base(request)
            return render(request, 'campaigns/schedule_campaign.html', {
                "store": store,
                "update_day": update_day,
                "audiences": audiences,
                "my_base": my_base,
                })
