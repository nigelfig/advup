from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Place, Messaging
from links.models import ReviewLinkType, ReviewLink
from memberships.models import UserMembership
from django.utils import timezone
import requests 
from django.http import HttpResponseRedirect
from django.urls import reverse
import json
from django.conf import settings

from sendreview.views import check_paid, check_base

@login_required
def your_stores(request):
    user_type = check_paid(request)
    if user_type.membership.membership_type == "FREE":
        return redirect('memberships:payment')
    else:
        places = Place.objects.filter(businessperson=request.user)
        my_base = check_base(request)

        if places.first().basic_advup:
            return render(request, 'stores/your_stores_basic.html', {
                        "places": places,
                        "my_base": my_base,
                        })
        
        return render(request, 'stores/your_stores.html', {
                    "places": places,
                    "my_base": my_base,
                    })

# need to check if protected against unpaid clients
@login_required()
def create(request):
    key = settings.GOOGLE_PLACES_KEY
    if request.method == "POST":
        if request.POST['user_place_id']:
            placename = request.POST.get("user_place_name", None)
            place = Place()
            user_placeid = request.POST.get("user_place_id", None)
            place.placeid = user_placeid
            place.placename = placename
            place.title = placename
            place.address = request.POST.get("user_address", None)
            place.store_number = request.POST.get("store_number", None)
            place.create_date = timezone.now()

            # api-endpoint 
            URL = "https://maps.googleapis.com/maps/api/geocode/json"

            # location given here 
            location = user_placeid
            

            # defining a params dict for the parameters to be sent to the API 
            PARAMS = {'place_id':location, 'key': key} 

            # sending get request and saving the response as response object 
            r = requests.get(url = URL, params = PARAMS) 

            # extracting data in json format 
            data = r.json() 


            # extracting latitude, longitude and formatted address 
            # of the first matching location 
            latitude = data['results'][0]['geometry']['location']['lat'] 
            longitude = data['results'][0]['geometry']['location']['lng']
            print(f"latitude is {latitude} and longitude is {longitude}")             
            
            place.latitude = latitude
            place.longitude = longitude

            comps = data['results'][0]['address_components']
        

            for val in comps:
                if 'country' in val['types']:
                    place.country = val['short_name']
                    break
            place.main_review_type = get_object_or_404(ReviewLinkType, review_link_type='GOOG')

            place.save()
            place.businessperson.add(request.user)

            google_link = ReviewLink()

            review_url_long = "https://search.google.com/local/writereview?placeid=" + user_placeid
            review_url_name =  "Google Review Link " + placename
            place_slug = place.slug

            linkRequest = {
                "destination": review_url_long, 
                "domain": { "fullName": "adva.co" }, 
                "title": review_url_name,
                "slashtag": place_slug,
            }


            requestHeaders = {
            "Content-type": "application/json",
            "apikey": settings.REBRANDLY_API_KEY,
            }

            r = requests.post("https://api.rebrandly.com/v1/links", 
                data = json.dumps(linkRequest),
                headers=requestHeaders)

            print(r.status_code)

            if (r.status_code == requests.codes.ok):
                link_data = r.json()
                google_link.short_url = link_data["shortUrl"]
                google_link.link_id = link_data["id"]
                google_link.long_url = review_url_long
                google_link.review_link_type = get_object_or_404(ReviewLinkType, review_link_type='GOOG')
                google_link.store = place
                google_link.save()  

            place_feedback_slug = place_slug + "-feedback"

            feedback_link = ReviewLink()

            feedback_url_long = f"https://app.advantageup.com/shops/{place_slug}/recommend/"
            feedback_url_name =  "Feedback Link " + placename

            linkRequest = {
                "destination": feedback_url_long, 
                "domain": { "fullName": "adva.co" }, 
                "title": feedback_url_name,
                "slashtag": place_feedback_slug,
            }


            requestHeaders = {
            "Content-type": "application/json",
            "apikey": settings.REBRANDLY_API_KEY,
            }

            r = requests.post("https://api.rebrandly.com/v1/links", 
                data = json.dumps(linkRequest),
                headers=requestHeaders)

            print(r.status_code)

            if (r.status_code == requests.codes.ok):
                link_data = r.json()
                feedback_link.short_url = link_data["shortUrl"]
                feedback_link.link_id = link_data["id"]
                feedback_link.long_url = feedback_url_long
                feedback_link.review_link_type = get_object_or_404(ReviewLinkType, review_link_type='FEED')
                feedback_link.store = place
                feedback_link.save()  

            messaging = Messaging()
            messaging.place = place
            messaging.review_copy = f"Thanks for doing business with {place.placename}. Would you mind leaving us a review on Google: {google_link.short_url}"
            messaging.feedback_copy = f"Thanks for doing business with {place.placename}. Would you mind leaving us a review on Google: {feedback_link.short_url}"
            messaging.no_match_reply = f"This is an automated messaging system. We'd love to speak to you and get your feedback, please give us call at {place.store_number}."
            messaging.save()
            

            reviewpk = place.id
        return HttpResponseRedirect(reverse('findphonenums:findnum', kwargs={'reviewpk': reviewpk}))
    else:
        purchased_stores = get_object_or_404(UserMembership, user=request.user).locations
        added_stores = Place.objects.filter(businessperson=request.user).count()
        stores_to_add = purchased_stores - added_stores
        key_url = "https://maps.googleapis.com/maps/api/js?key=" + key + "&libraries=places&callback=initMap"
        if stores_to_add > 0:
            return render(request, 'stores/create.html', {"maps_key_url": key_url})
        else:
            ## need to change redirect link
            return HttpResponseRedirect(reverse('sendreview'))
