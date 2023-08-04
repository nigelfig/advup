from django.contrib import admin

from .models import Review

class ReviewAdmin(admin.ModelAdmin):
    list_display= ('reviewer_name', 'relative_time_description', 'rating', 'store', 'updated_at')

admin.site.register(Review, ReviewAdmin)