from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include
from django.conf.urls import url

admin.site.site_header = 'AdvantageUp Admin Panel'
admin.site.site_title = 'AdvantageUp Admin'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('memberships/', include('memberships.urls', namespace='memberships')),
    path('phonenumbers/', include('findphonenum.urls', namespace='findphonenums')),
    path('stores/', include('stores.urls')),
    path('shops/', include('shops.urls')),
    path('smsapp/', include('smsapp.urls')),
    path('<int:placepk>/messaging/', include('sendreview.urls')),
    path('', include('accounts.urls')),
    path('accounts/', include('accounts.passwords.urls')),
    path('profile/', include('companies.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('support/', include('support.urls')),
    path('<int:placepk>/audiences/', include('audiences.urls')),
    path('<int:placepk>/campaigns/', include('campaigns.urls')),
    path('<int:placepk>/links/', include('links.urls')),
    url(r'^tz_detect/', include('tz_detect.urls')),
    path('captcha/', include('captcha.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
