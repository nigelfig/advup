from django.core.management.base import BaseCommand, CommandError

from stores.models import Place
from companies.models import Profile
from datetime import datetime

class Command(BaseCommand):
    def updating_monthly_limit():
        now = datetime.now()
        cday = now.strftime("%d")
        profiles = Profile.objects.all()

        for profile in profiles:
            regday = profile.create_date.strftime("%d")
            if cday == "29" or cday == "30" or cday == "31":
                pass
            elif cday == "28":
                if cday == regday or regday == "29" or regday == "30" or regday == "31":
                    businessperson = profile.businessperson
                    places = Place.objects.filter(businessperson=businessperson)
                    for place in places:
                        sms_limit = place.monthly_sms_limit
                        upload_limit = place.monthly_sub_uploads_limit
                        place.monthly_sms = sms_limit
                        place.monthly_sub_uploads = upload_limit
                        place.save()
            elif cday == regday:
                businessperson = profile.businessperson
                places = Place.objects.filter(businessperson=businessperson)
                for place in places:
                    sms_limit = place.monthly_sms_limit
                    upload_limit = place.monthly_sub_uploads_limit
                    place.monthly_sms = sms_limit
                    place.monthly_sub_uploads = upload_limit
                    place.save()

        return
