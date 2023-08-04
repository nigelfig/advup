from django.contrib import admin

from .models import Profile
# Register your models here.

class ProfileAdmin(admin.ModelAdmin):
    list_display= ('businessperson', 'first_name', 'last_name', 'company_name', 'phone_number', 'create_date')
    list_filter = ('businessperson__email', 'company_name',)

    search_fields = ['businessperson__email', 'first_name', 'last_name', 'company_name']

admin.site.register(Profile, ProfileAdmin)