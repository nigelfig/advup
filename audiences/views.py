from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Audience, Subscriber, GlobalUnsubscriber
from stores.models import Place
from django.utils import timezone
from sendreview.views import check_paid, check_base
from django.contrib import messages
import pandas as pd
import re
from twilio.rest import Client
from django.conf import settings
from memberships.models import UserMembership
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.core.files.storage import default_storage

import boto3
import io
from .tasks import creating_subs

from django.core.paginator import Paginator, EmptyPage

import vonage

@login_required
def add_subscriber(request, placepk):
    if request.method == "POST":
        no_first_name = not request.POST["first_name"]
        print("Does not have first name")
        print(no_first_name)

        no_last_name = not request.POST["last_name"]
        print("Does not have last name")
        print(no_last_name)

        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        phonenum_body = request.POST["phone_num_body"]

        store_ctry = request.POST['store_ctry']
        your_audience_id = request.POST["your_audience"]

        place = get_object_or_404(Place, pk=placepk, businessperson=request.user)
        your_audience = get_object_or_404(Audience, pk=your_audience_id, store=place)
        PHONE_TYPE_LOOKUP = settings.PHONE_TYPE_LOOKUP
        ACCOUNT_SID = settings.TWILIO_ACCOUNT_SID
        AUTH_TOKEN = settings.TWILIO_AUTH_TOKEN
        client = Client(ACCOUNT_SID, AUTH_TOKEN)

        VONAGE_API_KEY = settings.VONAGE_API_KEY
        VONAGE_SECRET_KEY = settings.VONAGE_SECRET_KEY
        vg_client = vonage.Client(key=VONAGE_API_KEY, secret=VONAGE_SECRET_KEY)
        
        #parse phone number
        if isinstance(phonenum_body, int):
            phonenum_body = str(phonenum_body)

        sendnum_ary = re.findall('[0-9]+', phonenum_body)
        sendnum = "".join(sendnum_ary)
        phonenum = "+1" + sendnum
        final_sendnum = "+" + sendnum
        phone_num = None
        print(sendnum_ary)
        if len(sendnum) == 10 or len(sendnum) == 11:
            print("number is 10 or 11 digits")
            if len(sendnum) == 10:
                phone_num = phonenum
            else:
                phone_num = final_sendnum
            
            remaining_subs = place.monthly_sub_uploads
            if remaining_subs > 0:
                is_mobile = False

                place.monthly_sub_uploads -= 1
                place.save()

                if store_ctry == 'US' and PHONE_TYPE_LOOKUP == True:
                    phone_numb_lookup = client.lookups.phone_numbers(phone_num).fetch(type=['carrier'])
                    if phone_numb_lookup.carrier['type'] == "mobile":
                        is_mobile = True
                if store_ctry == 'CA' and PHONE_TYPE_LOOKUP == True:
                    vg_insight_json = vg_client.get_standard_number_insight(number=phone_num)
                    vg_phone_type = vg_insight_json['current_carrier']['network_type']
                    if vg_phone_type == "mobile":
                        is_mobile = True

                if is_mobile or PHONE_TYPE_LOOKUP == False:
                    if not no_first_name and not no_last_name:
                        print("has first name and last name")

                        if len(first_name) > 15:
                            first_name = first_name[:15]
                        if len(last_name)> 15:
                            last_name = last_name[:15]
                        created = Subscriber.objects.update_or_create(
                            phone_number = phone_num,
                            audience = your_audience,
                            defaults = {
                                "definitely_cell_number": is_mobile,
                                "first_name": first_name,
                                "last_name": last_name,
                            })
                    elif no_first_name and no_last_name:
                        created = Subscriber.objects.update_or_create(
                            phone_number = phone_num,
                            audience = your_audience,
                            defaults = {
                                "first_name": "",
                                "last_name": "",
                                "definitely_cell_number": is_mobile,
                            })            
                    elif not no_first_name and no_last_name:
                        if len(first_name) > 15:
                            first_name = first_name[:15]
                        created = Subscriber.objects.update_or_create(
                            phone_number = phone_num,
                            audience = your_audience,
                            defaults = {
                                "definitely_cell_number": is_mobile,
                                "first_name": first_name,
                                "last_name": "",
                            })
                        
                    elif no_first_name and not no_last_name:
                        if len(last_name)> 15:
                            last_name = last_name[:15]
                        created = Subscriber.objects.update_or_create(
                            phone_number = phone_num,
                            audience = your_audience,
                            defaults = {
                                "definitely_cell_number": is_mobile,
                                "first_name": "",
                                "last_name": last_name,
                            })
                    
                    messages.info(request, "Successfully added subscriber to your audience")
                    return redirect('add_subscriber', placepk=placepk)
            else:
                messages.error(request, "You have reached your monthly subscriber upload limit. Subscriber was not added to your audience.")
                return redirect('add_subscriber', placepk=placepk)
        # except:
        #     pass


        messages.error(request, "Error occured, subscriber was not added to your audience. Please try again")
        return redirect('add_subscriber', placepk=placepk)
    else:
        user_type = check_paid(request)
        if user_type.membership.membership_type == "FREE":
            return redirect('memberships:payment')
        else:
            audiences = Audience.objects.filter(store=placepk)
            store = get_object_or_404(Place, id=placepk, businessperson=request.user)
            update_day = store.create_date.day
            my_base = check_base(request)

            return render(request, 'audiences/add_subscriber.html', {
                "store": store,
                "update_day": update_day,
                "audiences": audiences,
                "my_base": my_base,
                })


@login_required
def create_audience(request, placepk):
    if request.method == "POST":
        audience = Audience()
        audience.audience_name = request.POST["audience_name"]
        audience.create_date = timezone.now()
        store = get_object_or_404(Place, pk=placepk, businessperson=request.user, has_number=True)
        audience.store = store
        audience.save()
        messages.info(request, "Successfully created a new audience")
        return redirect('create_audience', placepk=placepk)

    else:
        user_type = check_paid(request)
        if user_type.membership.membership_type == "FREE":
            return redirect('memberships:payment')
        else:
            store = get_object_or_404(Place, id=placepk, businessperson=request.user)
            my_base = check_base(request)
            return render(request, 'audiences/create_audience.html', {
                "store": store,
                "my_base": my_base,
                })


@login_required()
def audiences(request, placepk):
    if request.method == "POST":
        pass
    else:
        user_type = check_paid(request)
        if user_type.membership.membership_type == "FREE":
            return redirect('memberships:payment')
        else:
            audiences = Audience.objects.filter(store=placepk).order_by('-create_date')
            store = get_object_or_404(Place, id=placepk, businessperson=request.user)
            my_base = check_base(request)
            return render(request, 'audiences/audiences.html', {
                "store": store,
                "audiences": audiences,
                "my_base": my_base,
                })


@login_required()
def subs(request, placepk, audiencepk):
    if request.method == "POST":
        pass
    else:
        user_type = check_paid(request)
        if user_type.membership.membership_type == "FREE":
            return redirect('memberships:payment')
        else:
            subscribers = Subscriber.objects.filter(audience=audiencepk).order_by('-create_date')
            audience = get_object_or_404(Audience, id=audiencepk)
            store = get_object_or_404(Place, id=placepk, businessperson=request.user)
            p = Paginator(subscribers , 100)

            print('NUMBER OF PAGES')
            print(p.num_pages)

            page_num = request.GET.get('page', 1)
            try:
                page = p.page(page_num)
            except EmptyPage:
                page = p.page(1)
            my_base = check_base(request)
            return render(request, 'audiences/subs.html', {
                "store": store,
                "subscribers": page,
                "audience": audience,
                "my_base": my_base,
                })

@login_required()
def unsubscribers(request, placepk):
    if request.method == "POST":
        pass
    else:
        user_type = check_paid(request)
        if user_type.membership.membership_type == "FREE":
            return redirect('memberships:payment')
        else:
            store = get_object_or_404(Place, id=placepk, businessperson=request.user)
            unsubscribers = GlobalUnsubscriber.objects.filter(place=store).order_by('-unsubscribed_on')
            my_base = check_base(request)
            return render(request, 'audiences/unsubscribers.html', {
                "store": store,
                "unsubscribers": unsubscribers,
                "my_base": my_base,
                })

@login_required
def unsubscribe_customer(request, placepk):
    if request.method == "POST":
        phonenum_body = request.POST["phone_num_body"]
        #parse phone number
        if isinstance(phonenum_body, int):
            phonenum_body = str(phonenum_body)

        sendnum_ary = re.findall('[0-9]+', phonenum_body)
        sendnum = "".join(sendnum_ary)
        phone_num = "+1" + sendnum

        if len(sendnum) != 10:
            messages.error(request, 'There was an error in unsubscribing customer cell number, please try again.')
            return redirect('unsubscribe_customer', placepk=placepk)
        
        store = get_object_or_404(Place, id=placepk, businessperson=request.user, has_number=True)

        unsubscriber, created = GlobalUnsubscriber.objects.get_or_create(
            unsubscriber_number=phone_num,
            place=store,
            defaults={'staff_unsubscribed': True},
        )
        if not created:
            messages.info(request, "Customer cell number was already unsubscribed")
            return redirect('unsubscribe_customer', placepk=placepk)
        
        messages.info(request, "Successfully unsubscribed customer cell number")
        return redirect('unsubscribe_customer', placepk=placepk)

    else:
        user_type = check_paid(request)
        if user_type.membership.membership_type == "FREE":
            return redirect('memberships:payment')
        else:
            store = get_object_or_404(Place, id=placepk, businessperson=request.user, has_number=True)
            my_base = check_base(request)
            return render(request, 'audiences/unsubscribe_customer.html', {
                "store": store,
                "my_base": my_base,
                })

@login_required
@require_POST
def delete_audience(request, placepk):
    audience_id = request.POST["audience_id"]
    Audience.objects.filter(id=audience_id).delete()

    return redirect('audiences', placepk=placepk)

@login_required
def remove_subscriber(request, placepk):
    if request.method == "POST":
        audience_id = request.POST["audience_id"]
        sub_id = request.POST["sub_id"]
        Subscriber.objects.filter(id=sub_id).delete()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
@require_POST
def resubscribe(request, placepk):
    resub_id = request.POST["resub_id"]
    GlobalUnsubscriber.objects.filter(id=resub_id).delete()
    return redirect('unsubscribers', placepk=placepk)

@login_required
def upload_subscribers(request, placepk):
    template = "audiences/upload.html"
    if request.method == "POST":
        # your_file = request.FILES['file']
        uploaded_file = request.FILES['file']
        file_name = default_storage.save(uploaded_file.name, uploaded_file)
        print("the file name")
        print(file_name)
        file_url = default_storage.url(file_name)
        print("the file url")
        print(file_url)
        your_audience_id = request.POST["your_audience"]
        your_audience_id = int(your_audience_id)
        store_ctry = request.POST["store_ctry"]
        store_id = placepk
        no_phone_num = not request.POST["phonenum"]
        no_first_name = not request.POST["fname"]
        no_last_name = not request.POST["lname"]
        your_audience = get_object_or_404(Audience, id=your_audience_id)
        place = get_object_or_404(Place, businessperson=request.user, id=store_id)
        audiences = Audience.objects.filter(store=place)

        if no_phone_num:
            messages.error(request, 'You must select a Column Letter for the cell number field in the Excel file.')
            return redirect('upload', placepk=placepk)

        if not no_phone_num:
            phonenumi = int(request.POST["phonenum"])
        if not no_first_name:
            fnamei = int(request.POST["fname"])
        if not no_last_name:
            lnamei = int(request.POST["lname"])

        if not no_first_name and not no_last_name:
            if fnamei == phonenumi or lnamei == phonenumi or fnamei == lnamei:
                messages.error(request, 'You cannot use the same Column Letter for two fields, for example First Name and Last Name cannot be assigned the same Column Letter.')
                return redirect('upload', placepk=placepk)
        elif not no_first_name and no_last_name:
            if fnamei == phonenumi:
                messages.error(request, 'You cannot use the same Column Letter for two fields, for example First Name and Last Name cannot be assigned the same Column Letter.')
                return redirect('upload', placepk=placepk)

        elif no_first_name and not no_last_name:
            if lnamei == phonenumi:
                messages.error(request, 'You cannot use the same Column Letter for two fields, for example First Name and Last Name cannot be assigned the same Column Letter.')
                return redirect('upload', placepk=placepk)


        
        if file_name.endswith('.csv') or file_name.endswith('.xlsx') or file_name.endswith('.xls'):
            # code to update status of audience to processing
            your_audience.audience_status = 'PROCESSING'
            your_audience.save()
            if not no_first_name and not no_last_name:
                creating_subs.delay(file_name, your_audience_id, store_ctry, store_id, no_phone_num, no_first_name, no_last_name, phonenumi, fnamei=fnamei, lnamei=lnamei)
            elif not no_first_name and no_last_name:
                creating_subs.delay(file_name, your_audience_id, store_ctry, store_id, no_phone_num, no_first_name, no_last_name, phonenumi, fnamei=fnamei)
            elif no_first_name and not no_last_name:
                creating_subs.delay(file_name, your_audience_id, store_ctry, store_id, no_phone_num, no_first_name, no_last_name, phonenumi, lnamei=lnamei)
            elif no_first_name and no_last_name:
                creating_subs.delay(file_name, your_audience_id, store_ctry, store_id, no_phone_num, no_first_name, no_last_name, phonenumi)
            messages.warning(request, "Your subscribers are being added to your audience, wait until status changes to 'up to date', before sending a campaign.")
            return redirect('audiences', placepk=placepk)      
        else:
            messages.error(request, 'This is not a Excel file, please try another file. Formats accepted are .xlsx , .xls, and .csv')
        return redirect('upload', placepk=placepk)

    user_type = check_paid(request)
    if user_type.membership.membership_type == "FREE":
        return redirect('memberships:payment')
    else:

        store = get_object_or_404(Place, id=placepk, businessperson=request.user)
        update_day = store.create_date.day
        audiences = Audience.objects.filter(store=store)
        my_base = check_base(request)
        
        prompt = {
            'order': 'Order of the CSV should be first_name, last_name, email, phone_number',
            "update_day": update_day,
            "audiences": audiences,
            'store':store,
            "my_base": my_base,
        }

    
        return render(request, template, prompt)
