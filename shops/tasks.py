from __future__ import absolute_import, unicode_literals

from celery import shared_task

from stores.models import Place, PlaceDetail
from .models import Review
import requests
import os
import re
from django.core.mail import send_mail
from django.conf import settings

GOOGLE_PLACES_KEY = settings.GOOGLE_PLACES_KEY

@shared_task
def update_reviews():

    stores = Place.objects.all()
    Review.objects.all().delete()

    for store in stores:
        try:
            business_places_id = store.placeid
            google_places_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={business_places_id}&key={GOOGLE_PLACES_KEY}"
            r = requests.get(url=google_places_url)
            store_data = r.json()["result"]


            formatted_store_number = store_data["formatted_phone_number"]

            num_ary = re.findall('[0-9]+', formatted_store_number)
            num = "".join(num_ary)
            print(num)
            if len(num) == 10:
                unformatted_store_number = int(num)
            else:
                unformatted_store_number = None

            google_rating = store_data["rating"]
            google_reviews_total = store_data["user_ratings_total"]
            website = store_data["website"]
            hours_mon = store_data["opening_hours"]["weekday_text"][0]
            hours_tue = store_data["opening_hours"]["weekday_text"][1]
            hours_wed = store_data["opening_hours"]["weekday_text"][2]
            hours_thu = store_data["opening_hours"]["weekday_text"][3]
            hours_fri = store_data["opening_hours"]["weekday_text"][4]
            hours_sat = store_data["opening_hours"]["weekday_text"][5]
            hours_sun = store_data["opening_hours"]["weekday_text"][6]

            detail, created = PlaceDetail.objects.update_or_create(
                place = store,
                defaults = {
                    "formatted_store_number": formatted_store_number,
                    "unformatted_store_number": unformatted_store_number,
                    "google_rating": google_rating,
                    "google_reviews_total": google_reviews_total,
                    "website": website,
                    "hours_mon": hours_mon,
                    "hours_tue": hours_tue,
                    "hours_wed": hours_wed,
                    "hours_thu": hours_thu,
                    "hours_fri": hours_fri,
                    "hours_sat": hours_sat,
                    "hours_sun": hours_sun,
                })


            reviews = store_data["reviews"]

            for areview in reviews:
                if areview['rating'] >= 4:
                    review = Review()
                    review.reviewer_name = areview['author_name']
                    review.reviewer_photo_url = areview['profile_photo_url']
                    review.relative_time_description = areview['relative_time_description']
                    review.rating = areview['rating']
                    review.review_text = areview['text']
                    review.store = store
                    review.save()
        
        except:
            store_name = store.placename
            initial_subject = "Error updating place details"
            from_email = 'AdvantageUp Support <support@advantageup.com>'
            to_email = ['nigel@advantageup.com']

            subject = f"Error updating place details for {store_name}"

            if len(subject) > 80:
                subject = initial_subject

            email_message = f"There was an error updating place details for {store_name}"
            html_email_message = f"<h3>Error updating place details</h3><p>for {store_name}</p>"

            
            send_mail(subject, email_message, from_email, to_email, fail_silently=True, html_message=html_email_message)

    return None