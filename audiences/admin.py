from django.contrib import admin
from .models import Audience, Subscriber, GlobalUnsubscriber, StoreDefaultAudience

from import_export.admin import ImportExportModelAdmin


class SubscriberAdmin(ImportExportModelAdmin):
    list_display= ('phone_number', 'definitely_cell_number', 'first_name', 'last_name', 'audience')

class GlobalUnsubscriberAdmin(admin.ModelAdmin):
    list_display= ('unsubscriber_number', 'place')

class AudienceAdmin(admin.ModelAdmin):
    list_display= ('audience_name', 'store','subs_count')
    def subs_count(self, instance):
        return instance.get_subscribers()

admin.site.register(Audience, AudienceAdmin)
admin.site.register(Subscriber, SubscriberAdmin)
admin.site.register(GlobalUnsubscriber, GlobalUnsubscriberAdmin)
admin.site.register(StoreDefaultAudience)