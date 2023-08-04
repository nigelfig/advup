from django.shortcuts import render, redirect, get_object_or_404,reverse
from sendreview.views import check_paid, check_base
from .models import Stat
from stores.models import Place
from links.models import ReviewLink, ReviewLinkType
from campaigns.models import Campaign
from links.models import Link
from memberships.models import UserMembership
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from datetime import datetime
import calendar
import requests
import json
from itertools import chain
import operator
from django.conf import settings

# Create your views here.
@login_required()
def dashboard(request):
    user_type = check_paid(request)
    places = Place.objects.filter(businessperson=request.user)
    basic_plan = False
    if places.first() != None:
        basic_plan = places.first().basic_advup
        
    if user_type.membership.membership_type == "FREE":
        return redirect('memberships:payment')
    
    elif basic_plan == True:
        if places.count() == 1:
            storeid = places.first().id
            return redirect('sendreview', storeid)
        else:
            return redirect('your-stores')
    else:
 
        current_day = datetime.today()
        month_filter = current_day.strftime("%Y-%m")

        this_month = datetime.now().month

        # print(month_filter)
        campaigns = []
        link_metrics = []
        stats = Stat.objects.filter(place__in=places).order_by('-created_at')
        cur_review_link_clicks = 0
        cur_feedback_link_clicks = 0
        today = datetime.today()
        current_yearnum = today.year
        rev_monthnum = today.month
        cur_review_link_clicks = 0
        for place in places:
            place_campaigns = Campaign.objects.filter( audience__store=place, create_date__month=this_month )
            from itertools import chain
            campaigns = list(chain(campaigns, place_campaigns))
            cur_review_link_click = 0
            cur_feedback_link_click = 0

            google_review_type = get_object_or_404(ReviewLinkType, review_link_type='GOOG')
            feedback_review_type = get_object_or_404(ReviewLinkType, review_link_type='FEED')
            google_review_link = get_object_or_404(ReviewLink, store=place, review_link_type=google_review_type)
            feedback_link = get_object_or_404(ReviewLink, store=place, review_link_type=feedback_review_type)   

            if google_review_link.link_id:

                try:
                    url = "https://api.rebrandly.com/v1/links/" + google_review_link.link_id + "?apikey=" + settings.REBRANDLY_API_KEY

                    response = requests.request("GET", url)

                    link_data = response.json()
                    cur_review_link_click = link_data["clicks"]

                except:
                    pass

                cur_review_link_clicks += cur_review_link_click

            if feedback_link.link_id:

                try:
                    url = "https://api.rebrandly.com/v1/links/" + feedback_link.link_id + "?apikey=" + settings.REBRANDLY_API_KEY

                    response = requests.request("GET", url)

                    link_data = response.json()
                    cur_feedback_link_click = link_data["clicks"]

                except:
                    pass

                cur_feedback_link_clicks += cur_feedback_link_click

            links = Link.objects.filter( store=place, create_date__month=this_month )
            print(links)

            for link in links:
                try:
                    link_id = link.link_id

                    url = "https://api.rebrandly.com/v1/links/" + link_id + "?apikey=" + settings.REBRANDLY_API_KEY

                    response = requests.request("GET", url)

                    link_data = response.json()
                    link_clicks = link_data["clicks"]
                    link_metrics.append(link_clicks)

                    
                except:
                    link_metrics.append(0)




        monthly_campaign_clicks = sum(link_metrics)

        
        store = ""
        if places.count() == 1:
            store = get_object_or_404(Place, businessperson=request.user)

        clientpk=request.user.id
        complete_stores = Place.objects.filter(businessperson=clientpk, has_number=True)
        complete_stores_num = complete_stores.count()
        incomplete_stores = Place.objects.filter(businessperson=clientpk, has_number=False)
        incomplete_stores_num = incomplete_stores.count()
        purchased_stores = get_object_or_404(UserMembership, user=request.user).locations
        remaining_stores_num = purchased_stores - (complete_stores_num + incomplete_stores_num)
        print(f"there are {remaining_stores_num} remaining stores")
        remaining = purchased_stores > (complete_stores_num + incomplete_stores_num)
        print(f"remaining stores exist {remaining}")
        if remaining:
            my_base = 'accounts/base_multi.html'
        else:
            my_base = check_base(request)

        monthly_campaigns = len(campaigns)

        return render(request, 'dashboard/dashboard.html', {
                    "places": places,
                    "monthly_campaigns": monthly_campaigns,
                    "monthly_campaign_clicks": monthly_campaign_clicks,
                    "stats": stats,
                    "review_clicks": cur_review_link_clicks,
                    "feedback_clicks": cur_feedback_link_clicks,
                    "my_base": my_base,
                    "store": store,
                    "complete_stores": complete_stores,
                    "complete_stores_num": complete_stores_num,
                    "incomplete_stores": incomplete_stores,
                    "incomplete_stores_num": incomplete_stores_num,
                    "remaining_stores_num": remaining_stores_num,
                    "remaining": remaining,
                    "basic_plan": basic_plan,
                    })

            


@login_required()
def get_data(request, *args, **kwargs):
    places = Place.objects.filter(businessperson=request.user)
    today = datetime.today()
    monthnum = today.month
    current_monthnum = today.month
    current_yearnum = today.year
    current_month = calendar.month_name[monthnum]
    month_name_list = [current_month]

    sms_requests = []
    sms_interactions = []
    campaign_smss = []

    sms_request = 0
    sms_interaction = 0
    campaign_sms = 0

    #get stats for current month
    for place in places:
        sms_request += Stat.objects.filter(place=place, message_category = "REQU", created_at__month=monthnum, created_at__year=current_yearnum).count() 
        sms_interaction += Stat.objects.filter(place=place, message_category = "REPL", created_at__month=monthnum, created_at__year=current_yearnum).count() + Stat.objects.filter(place=place, message_category = "RATE", created_at__month=monthnum, created_at__year=current_yearnum).count()

        campaigns = Campaign.objects.filter( audience__store=place, create_date__month=monthnum, create_date__year=current_yearnum )
        campaign_sms += sum(campaign.successful_sends for campaign in campaigns if campaign.successful_sends)

    sms_requests.insert(0, sms_request)
    sms_interactions.insert(0, sms_interaction)
    campaign_smss.insert(0, campaign_sms)

    # get stats for 5 previous months
    for x in range(5):
        myyear = 0
        if monthnum <= 12 and monthnum >= 2:
            monthnum -= 1
        else:
            monthnum = 12
        if monthnum > current_monthnum:
            myyear = current_yearnum - 1
        else:
            myyear = current_yearnum
        month = calendar.month_name[monthnum]
        month_name_list.insert(0, month)
        sms_request = 0
        sms_interaction = 0
        campaign_sms = 0
        for place in places:
            sms_request += Stat.objects.filter(place=place, message_category = "REQU", created_at__month=monthnum, created_at__year=myyear).count()
            sms_interaction += Stat.objects.filter(place=place, message_category = "REPL", created_at__month=monthnum, created_at__year=myyear).count() + Stat.objects.filter(place=place, message_category = "RATE", created_at__month=monthnum, created_at__year=myyear).count()
            sms_request += Stat.objects.filter(place=place, message_category = "REQU", created_at__month=monthnum, created_at__year=myyear).count()

            campaigns = Campaign.objects.filter( audience__store=place, create_date__month=monthnum, create_date__year=myyear )
            campaign_sms += sum(campaign.successful_sends for campaign in campaigns if campaign.successful_sends)

        sms_requests.insert(0, sms_request)
        sms_interactions.insert(0, sms_interaction)
        campaign_smss.insert(0, campaign_sms)

    data = {
        "months": month_name_list,
        "requests": sms_requests,
        "interactions": sms_interactions,
        "campaign_smss": campaign_smss,
    }
    return JsonResponse(data) # http response


@login_required()
def dashboard_multi(request, placepk):
    user_type = check_paid(request)
    if user_type.membership.membership_type == "FREE":
        return redirect('memberships:payment')
    else:
        campaigns = []
        link_metrics = []
        stores = Place.objects.filter(businessperson=request.user)
        place = get_object_or_404(Place, pk=placepk, businessperson=request.user)
        # print(places)


        current_day = datetime.today()
        month_filter = current_day.strftime("%Y-%m")
        # print(month_filter)

        stats = Stat.objects.filter(place=place).order_by('-created_at')
        cur_review_link_clicks = 0
        today = datetime.today()
        current_yearnum = today.year
        rev_monthnum = today.month

        cur_review_link_clicks = 0
        cur_feedback_link_clicks = 0

        google_review_type = get_object_or_404(ReviewLinkType, review_link_type='GOOG')
        feedback_review_type = get_object_or_404(ReviewLinkType, review_link_type='FEED')
        google_review_link = get_object_or_404(ReviewLink, store=place, review_link_type=google_review_type)
        feedback_link = get_object_or_404(ReviewLink, store=place, review_link_type=feedback_review_type)    

        if google_review_link.link_id:
            try:
                url = "https://api.rebrandly.com/v1/links/" + google_review_link.link_id + "?apikey=" + settings.REBRANDLY_API_KEY

                response = requests.request("GET", url)

                link_data = response.json()
                cur_review_link_clicks = link_data["clicks"]
            except:
                pass


        if feedback_link.link_id:
            try:
                url = "https://api.rebrandly.com/v1/links/" + feedback_link.link_id + "?apikey=" + settings.REBRANDLY_API_KEY

                response = requests.request("GET", url)

                link_data = response.json()
                cur_feedback_link_clicks = link_data["clicks"]
            except:
                pass

        this_month = datetime.now().month
        links = Link.objects.filter( store=place, create_date__month=this_month )
        print(links)

        for link in links:
            try:
                link_id = link.link_id

                url = "https://api.rebrandly.com/v1/links/" + link_id + "?apikey=" + settings.REBRANDLY_API_KEY

                response = requests.request("GET", url)

                link_data = response.json()
                link_clicks = link_data["clicks"]
                link_metrics.append(link_clicks)

                
            except:
                link_metrics.append(0)




        monthly_campaign_clicks = sum(link_metrics)


         
        my_base = check_base(request)
        campaigns = Campaign.objects.filter( audience__store=place, create_date__month=this_month )
        monthly_campaigns = len(campaigns)

        basic_plan = place.basic_advup

        return render(request, 'dashboard/dashboard_multi.html', {
                    "store": place,
                    "monthly_campaigns": monthly_campaigns,
                    "monthly_campaign_clicks": monthly_campaign_clicks,
                    "stores": stores,
                    "stats": stats,
                    "review_clicks": cur_review_link_clicks,
                    "feedback_clicks": cur_feedback_link_clicks,
                    "my_base": my_base,
                    "basic_plan": basic_plan,
                    })

@login_required()
def get_data_multi(request, placeid, *args, **kwargs):
    place = get_object_or_404(Place, pk=placeid, businessperson=request.user)
    today = datetime.today()
    monthnum = today.month
    current_monthnum = today.month
    current_yearnum = today.year
    current_month = calendar.month_name[monthnum]
    month_name_list = [current_month]



    sms_requests = []
    sms_interactions = []
    campaign_smss = []
    review_link_clicks = []
    sms_request = 0
    sms_interaction = 0
    campaign_sms = 0
    review_link_click  = 0
    #get stats for current month
    

    sms_interaction += Stat.objects.filter(place=place, message_category = "REPL", created_at__month=monthnum, created_at__year=current_yearnum).count() + Stat.objects.filter(place=place, message_category = "RATE", created_at__month=monthnum, created_at__year=current_yearnum).count()
    sms_request += Stat.objects.filter(place=place, message_category = "REQU", created_at__month=monthnum, created_at__year=current_yearnum).count()
    

    sms_requests.insert(0, sms_request)
    sms_interactions.insert(0, sms_interaction)

    campaigns = Campaign.objects.filter( audience__store=place, create_date__month=monthnum, create_date__year=current_yearnum )
    campaign_sms += sum(campaign.successful_sends for campaign in campaigns if campaign.successful_sends)
    campaign_smss.insert(0, campaign_sms)
    # print(places)
    # get stats for latest 6 months
    complete_review_clicks = []
    # for place in places:
    rev_monthnum = today.month

    # get stats for 5 previous months
    for x in range(5):
        myyear = 0
        if monthnum <= 12 and monthnum >= 2:
            monthnum -= 1
        else:
            monthnum = 12
        if monthnum > current_monthnum:
            myyear = current_yearnum - 1
        else:
            myyear = current_yearnum
        month = calendar.month_name[monthnum]
        month_name_list.insert(0, month)
        sms_request = 0
        sms_interaction = 0
        campaign_sms = 0
        
        sms_interaction += Stat.objects.filter(place=place, message_category = "REPL", created_at__month=monthnum, created_at__year=myyear).count() + Stat.objects.filter(place=place, message_category = "RATE", created_at__month=monthnum, created_at__year=myyear).count()
        sms_request += Stat.objects.filter(place=place, message_category = "REQU", created_at__month=monthnum, created_at__year=myyear).count()


        sms_requests.insert(0, sms_request)
        sms_interactions.insert(0, sms_interaction)

        campaigns = Campaign.objects.filter( audience__store=place, create_date__month=monthnum, create_date__year=myyear )
        campaign_sms += sum(campaign.successful_sends for campaign in campaigns if campaign.successful_sends)
        campaign_smss.insert(0, campaign_sms)
    # print(merged_review_clicks)

    data = {
        "months": month_name_list,
        "requests": sms_requests,
        "interactions": sms_interactions,
        "campaign_smss": campaign_smss,
    }
    return JsonResponse(data) # http response