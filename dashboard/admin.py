from django.contrib import admin

# Register your models here.
from .models import Stat

# class StatAdmin(admin.ModelAdmin):
#     readonly_fields = ('created_at',)

# admin.site.register(Stat, StatAdmin)

# admin.site.register(Stat)

class StatAdmin(admin.ModelAdmin):
    list_display= ('place', 'business_number', 'customer_number', 'message', 'message_category', 'feedback_on', 'created_at', 'feedback_rating')
    list_filter = ('business_number', 'message_category', 'feedback_on')

    search_fields = ['place__placename', 'business_number']

admin.site.register(Stat, StatAdmin)