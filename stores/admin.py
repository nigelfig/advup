from django.contrib import admin

# Register your models here.
from .models import Place, Messaging, PlaceDetail

class PlaceAdmin(admin.ModelAdmin):
    list_display= ('placename', 'address', 'country', 'review_number', 'store_number', 'create_date', 'has_number')


    search_fields = ['placename', 'businessperson__email']

admin.site.register(Place, PlaceAdmin)

admin.site.register( Messaging )

admin.site.register( PlaceDetail )