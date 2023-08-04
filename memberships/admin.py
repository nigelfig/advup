from django.contrib import admin

# Register your models here.
from .models import Membership, UserMembership, Subscription

class MembershipAdmin(admin.ModelAdmin):
    list_display= ('slug', 'membership_type', 'price', 'stripe_plan_id', 'plan_type')
    list_filter = ('membership_type',)

class UserMembershipAdmin(admin.ModelAdmin):
    list_display= ('user', 'stripe_customer_id', 'membership', 'locations')
    list_filter = ('membership',)

class SubscriptionAdmin(admin.ModelAdmin):
    list_display= ('user_membership', 'stripe_subscription_id', 'active')

admin.site.register(Membership, MembershipAdmin)
admin.site.register(UserMembership, UserMembershipAdmin)
admin.site.register(Subscription, SubscriptionAdmin)