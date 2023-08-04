from dashboard.models import Stat
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from stores.models import Place, Messaging
from links.models import ReviewLinkType, ReviewLink
from memberships.models import UserMembership
from django.contrib import messages
from django.conf import settings
import requests

@login_required()
def check_paid(request):
    user_type = UserMembership.objects.filter(user=request.user)
    # print(user_type)
    user_type = user_type.first()
    # print("filtered")
    # print(user_type)
    return user_type

@login_required()
def check_base(request):
    businessowner=request.user
    places = Place.objects.filter(businessperson=businessowner)
    # print(places)
    if places.first().basic_advup == True:
        if places.count() > 1:
            my_base = 'accounts/base_basic_multi.html'
        else:
            my_base = 'accounts/base_basic.html'
    elif places.count() > 1:
        my_base = 'accounts/base_multi.html'
    else:
        my_base = 'accounts/base.html'
    return my_base

@login_required()
def update_review(request, placepk):
    if request.method == "POST":
        store = get_object_or_404(Place, pk=placepk, businessperson=request.user)
        messaging = get_object_or_404(Messaging, place=store)
        messaging.review_copy = request.POST['reviewsms']
        messaging.no_match_reply = request.POST['randomsms']
        messaging.feedback_copy = request.POST['feedreqsms']
        if request.POST.get('feedbox'):
            messaging.want_feedback = True
        else:
            messaging.want_feedback = False
        messaging.save()
        messages.info(request, "Successfully updated messaging")
        return redirect('updatereview', placepk=placepk)
    else:
        user_type = check_paid(request)
        if user_type.membership.membership_type == "FREE":
            return redirect('memberships:payment')
        else:
            store = get_object_or_404(Place, pk=placepk, businessperson=request.user)

            google_review_type = get_object_or_404(ReviewLinkType, review_link_type='GOOG')
            feedback_review_type = get_object_or_404(ReviewLinkType, review_link_type='FEED')
            google_review_link = get_object_or_404(ReviewLink, store=store, review_link_type=google_review_type)
            feedback_link = get_object_or_404(ReviewLink, store=store, review_link_type=feedback_review_type)
              
            my_base = check_base(request)

            return render(request, 'sendreview/updatereview.html', {
                    "store": store,
                    "my_base": my_base,
                    "google_review_link": google_review_link,
                    "feedback_link": feedback_link,
                })

@login_required()
def custom_sms(request, placepk):
    if request.method == "POST":
        return HttpResponseRedirect(reverse('dashboard'))
    else:
        user_type = check_paid(request)
        if user_type.membership.membership_type == "FREE":
            return redirect('memberships:payment')
        else:
            store = get_object_or_404(Place, pk=placepk, businessperson=request.user)
            my_base = check_base(request)

            return render(request, 'sendreview/sendcustom.html', {
                    "store": store,
                    "my_base": my_base,
                })


@login_required()
def send_review(request, placepk):
    if request.method == "POST":
        return HttpResponseRedirect(reverse('dashboard'))
    else:
        user_type = check_paid(request)
        if user_type.membership.membership_type == "FREE":
            return redirect('memberships:payment')
        else:
            store = get_object_or_404(Place, pk=placepk, businessperson=request.user)
            stats = Stat.objects.filter(place=store).order_by('-created_at')[:30]
            my_base = check_base(request)

            cur_review_link_click = 0
            cur_feedback_link_click = 0

            google_review_type = get_object_or_404(ReviewLinkType, review_link_type='GOOG')
            feedback_review_type = get_object_or_404(ReviewLinkType, review_link_type='FEED')
            google_review_link = get_object_or_404(ReviewLink, store=store, review_link_type=google_review_type)
            feedback_link = get_object_or_404(ReviewLink, store=store, review_link_type=feedback_review_type)   

            if google_review_link.link_id:

                try:
                    url = "https://api.rebrandly.com/v1/links/" + google_review_link.link_id + "?apikey=" + settings.REBRANDLY_API_KEY

                    response = requests.request("GET", url)

                    link_data = response.json()
                    cur_review_link_click = link_data["clicks"]

                except:
                    pass


            if feedback_link.link_id:

                try:
                    url = "https://api.rebrandly.com/v1/links/" + feedback_link.link_id + "?apikey=" + settings.REBRANDLY_API_KEY

                    response = requests.request("GET", url)

                    link_data = response.json()
                    cur_feedback_link_click = link_data["clicks"]

                except:
                    pass
            
            return render(request, 'sendreview/sendreview.html', {
                "store": store,
                "my_base": my_base,
                "stats": stats,
                "review_clicks": cur_review_link_click,
                "feedback_clicks": cur_feedback_link_click,
                })


 
