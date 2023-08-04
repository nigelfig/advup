from django.shortcuts import render, get_object_or_404, reverse, redirect
from twilio.rest import Client
from django.conf import settings
from stores.models import Place
from django.http import HttpResponseRedirect
import requests
from django.contrib.auth.decorators import login_required

@login_required()
def selectnumber(request, reviewpk):
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    client = Client(account_sid, auth_token)
    
    place = get_object_or_404(Place, pk=reviewpk)
    if request.method == "POST":
        if place.has_number == False and request.user in place.businessperson.all():

            
            
            if settings.PHONE_PURCHASING_ON == True:
                bought_number = client.incoming_phone_numbers \
                            .create(phone_number=request.POST['phonenum'])
                num_sid = bought_number.sid
            place.has_number = True
            place.review_number = request.POST['phonenum']
            place.save()
            reviewnum_id = str(place.id)
            sms_url =  settings.MAIN_URL + "/smsapp/" + reviewnum_id + "/"

            if settings.PHONE_PURCHASING_ON == True:
                post_str = "https://api.twilio.com/2010-04-01/Accounts/" + account_sid + "/IncomingPhoneNumbers/" + num_sid + ".json"
                response = requests.post(post_str, auth=(account_sid, auth_token), data={'SmsUrl':sms_url} )
            
            return redirect('dashboard')
        else:
            return redirect('dashboard')

    if place.has_number == False and request.user in place.businessperson.all():
        longitude = place.longitude
        latitude = place.latitude
        country = place.country
        lat_long = str(latitude) + "," + str(longitude)



        numbers = client.available_phone_numbers(country) \
                        .local \
                        .list(near_lat_long=lat_long, distance="25", voice_enabled=True, sms_enabled=True, mms_enabled=True, fax_enabled=True)
        
        context = {
            'numbers': numbers,
            'place': place,
    
        }

        return render(request, "findphonenum/select_number.html", context)
    else:
        return redirect('dashboard')