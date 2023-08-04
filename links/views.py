from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from stores.models import Place
from .models import Link
from memberships.models import UserMembership
from sendreview.views import check_paid, check_base
from django.conf import settings
import requests 
import json
from django.contrib import messages

# Create your views here.
@login_required()
def delete_link(request, placepk):
    if request.method == "POST":
        if request.POST['link_id'] and request.POST["actual_link_id"]:
            store = get_object_or_404(Place, id=placepk, businessperson=request.user)
            links_remaining = store.total_links_remaining 
            if links_remaining > 0:

                store.total_links_remaining += 1
                store.save()

                actual_link_id = request.POST["actual_link_id"]
                
                get_object_or_404(Link, id=actual_link_id, store=store).delete()

                link_id = request.POST['link_id']
                url = 'https://api.rebrandly.com/v1/links/' + link_id

                requestHeaders = {
                "Content-type": "application/json",
                "apikey": settings.REBRANDLY_API_KEY,
                }

                r = requests.delete(url,
                    headers=requestHeaders)

                messages.info(request, "Successfully deleted link")

        return redirect('links', placepk=placepk)

@login_required()
def create_link(request, placepk):
    if request.method == "POST":
        if request.POST['my_long_url'] and request.POST['short_name']:
            
            store = get_object_or_404(Place, id=placepk, businessperson=request.user)
            links_remaining = store.total_links_remaining 
            if links_remaining > 0:

                #create shortened url
                my_long_url = request.POST['my_long_url']
                short_name = request.POST['short_name']
                short_name = short_name.replace(" ", "")
                short_name = short_name.replace("/", "")
                short_name = short_name.replace("\\", "")

                linkRequest = {
                "destination": my_long_url
                , "domain": { "fullName": "adva.co" }
                , "slashtag": short_name
                , "title": my_long_url
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
                    link = Link()
                    link.link_id = link_data["id"]
                    link.short_url = link_data["shortUrl"]
                    link.long_url = link_data["destination"]
                    link.store = store
                    link.save()
                    print("Long URL was %s, short URL is %s" % (link_data["destination"], link_data["shortUrl"]))
                    store.total_links_remaining -= 1
                    store.save()

                    messages.info(request, "Successfully created new short link")
                    return redirect('links', placepk=placepk)
                else:
                    messages.error(request, 'Error in creating short link, ex. short name may be taken')
                    return redirect('create-link', placepk=placepk)
            else:
                messages.error(request, 'Error in creating short link, you may have used up all your short links, consider deleting some')
                return redirect('create-link', placepk=placepk)
        
            return redirect('create-link', placepk=placepk)
    else:
        user_type = check_paid(request)
        if user_type.membership.membership_type == "FREE":
            return redirect('memberships:payment')
        else:
            store = get_object_or_404(Place, id=placepk, businessperson=request.user)
            my_base = check_base(request)
            return render(request, 'links/createlink.html', {
                    "store": store,
                    "my_base": my_base,
                })

@login_required()
def links(request, placepk):
    if request.method == "POST":
        pass
    else:
        user_type = check_paid(request)
        if user_type.membership.membership_type == "FREE":
            return redirect('memberships:payment')
        else:
            store = get_object_or_404(Place, id=placepk, businessperson=request.user)
            links = Link.objects.filter(store=store).order_by('-create_date')

            link_metrics = []
            for link in links:
                try:
                    link_id = link.link_id
                    print(link_id)
                    url = "https://api.rebrandly.com/v1/links/" + link_id + "?apikey=" + settings.REBRANDLY_API_KEY

                    response = requests.request("GET", url)

                    link_data = response.json()
                    link_clicks = link_data["clicks"]
                    link_metrics.append(link_clicks)
                except:
                    link_metrics.append("Not Trackable")



            link_data = zip(links, link_metrics)

            my_base = check_base(request)
            return render(request, 'links/links.html', {
                "store": store,
                "links": link_data,
                "my_base": my_base,
                })
