from __future__ import absolute_import, unicode_literals

from celery import shared_task

import pandas as pd
from .models import Subscriber, Audience
from stores.models import Place
from twilio.rest import Client
from django.conf import settings
import re
from django.shortcuts import render, redirect, get_object_or_404
import boto3
import io
import vonage

@shared_task
def creating_subs(file_name, your_audience_id, store_ctry, store_id, no_phone_num, no_first_name, no_last_name, phonenumi, fnamei=None, lnamei=None):
    your_audience = get_object_or_404(Audience, id=your_audience_id)
    place = get_object_or_404(Place, id=store_id)

    PHONE_TYPE_LOOKUP = settings.PHONE_TYPE_LOOKUP
    ACCOUNT_SID = settings.TWILIO_ACCOUNT_SID
    AUTH_TOKEN = settings.TWILIO_AUTH_TOKEN
    client = Client(ACCOUNT_SID, AUTH_TOKEN)

    VONAGE_API_KEY = settings.VONAGE_API_KEY
    VONAGE_SECRET_KEY = settings.VONAGE_SECRET_KEY
    vg_client = vonage.Client(key=VONAGE_API_KEY, secret=VONAGE_SECRET_KEY)

    AWS_ACCESS_KEY_ID = settings.AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY = settings.AWS_SECRET_ACCESS_KEY
    AWS_STORAGE_BUCKET_NAME = settings.AWS_STORAGE_BUCKET_NAME

    aws_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    bucket_name = AWS_STORAGE_BUCKET_NAME
    object_key = file_name
    obj = aws_client.get_object(Bucket=bucket_name, Key=object_key)


    if file_name.endswith('.csv'):
        data = obj['Body']
        csv_string = data.read().decode('utf-8')
        df = pd.read_csv(io.StringIO(csv_string))
    else:
        data = obj['Body'].read()
        df = pd.read_excel(data)

    for index, row in df.iterrows():
        # add try block to avoid error breaking whole flow
        try:
            #parse phone number
            phonenum_body = row[phonenumi]
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
                    user_fname = ""
                    user_lname = ""
                    if is_mobile or PHONE_TYPE_LOOKUP == False:
                        if not no_first_name and not no_last_name:
                            print("has first name and last name")
                            user_fname = row[fnamei]
                            user_lname = row[lnamei]
                            if pd.isnull(row[fnamei]):
                                user_fname = ""
                            if pd.isnull(row[lnamei]):
                                user_lname = ""
                            if len(user_fname) > 15:
                                user_fname = user_fname[:15]
                            if len(user_lname)> 15:
                                user_lname = user_lname[:15]
                            created = Subscriber.objects.update_or_create(
                                phone_number = phone_num,
                                audience = your_audience,
                                defaults = {
                                    "definitely_cell_number": is_mobile,
                                    "first_name": user_fname,
                                    "last_name": user_lname,
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
                            user_fname = row[fnamei]
                            if pd.isnull(row[fnamei]):
                                user_fname = ""
                            if len(user_fname) > 15:
                                user_fname = user_fname[:15]
                            created = Subscriber.objects.update_or_create(
                                phone_number = phone_num,
                                audience = your_audience,
                                defaults = {
                                    "first_name": user_fname,
                                    "last_name": "",
                                    "definitely_cell_number": is_mobile,
                                })
                            
                        elif no_first_name and not no_last_name:
                            user_lname = row[lnamei]
                            if pd.isnull(row[lnamei]):
                                user_lname = ""
                            if len(user_lname)> 15:
                                user_lname = user_lname[:15]
                            created = Subscriber.objects.update_or_create(
                                phone_number = phone_num,
                                audience = your_audience,
                                defaults = {
                                    "first_name": "",
                                    "last_name": user_lname,
                                    "definitely_cell_number": is_mobile,
                                })
        except:
            pass

                        
    your_audience.audience_status = 'UPTODATE'
    your_audience.save()              
    return None
