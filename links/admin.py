from django.contrib import admin
from .models import Link, ReviewLinkType, ReviewLink

admin.site.register(Link)
admin.site.register(ReviewLinkType)
admin.site.register(ReviewLink)
