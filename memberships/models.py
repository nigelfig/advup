from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from datetime import datetime
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY



class Membership(models.Model):
    FREE = 'FREE'
    PROMON = 'PROM'
    PROANU = 'PROA'
    MEMBERSHIP_CHOICES = (
        (FREE, 'Free'),
        (PROMON, 'Professional Monthly'),
        (PROANU, 'Professional Annual'),
    )
    slug = models.SlugField()
    membership_type = models.CharField(
        choices=MEMBERSHIP_CHOICES,
        default=FREE,
        max_length=30)
    price = models.IntegerField(default=50)
    stripe_plan_id = models.CharField(max_length=40)
    plan_type = models.CharField(max_length=40, default="monthly")

    def __str__(self):
        return self.membership_type

class UserMembership(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=40)
    membership = models.ForeignKey(Membership, on_delete=models.SET_NULL, null=True)
    locations = models.IntegerField(default=1)

    def __str__(self):
        return self.user.email

def post_save_usermembership_create(sender, instance, created, *args, **kwargs):
    user_membership, created = UserMembership.objects.get_or_create(user=instance)

    if user_membership.stripe_customer_id is None or user_membership.stripe_customer_id == '':
        if instance.is_staff:
            user_membership.stripe_customer_id = 'staff'
            user_membership.save()
        elif instance.shop_team_member:
            user_membership.stripe_customer_id = 'shop-team-member'
            user_membership.save()
        else:
            new_customer_id = stripe.Customer.create(email=instance.email)
            free_membership = Membership.objects.get(membership_type='FREE')
            user_membership.stripe_customer_id = new_customer_id['id']
            user_membership.membership = free_membership
            user_membership.save()

post_save.connect(post_save_usermembership_create, sender=settings.AUTH_USER_MODEL)


class Subscription(models.Model):
    user_membership = models.ForeignKey(UserMembership, on_delete=models.CASCADE)
    stripe_subscription_id = models.CharField(max_length=40)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.user_membership.user.email

    @property
    def get_created_date(self):
        subscription = stripe.Subscription.retrieve(self.stripe_subscription_id)
        return datetime.fromtimestamp(subscription.created)

    @property
    def get_next_billing_date(self):
        subscription = stripe.Subscription.retrieve(self.stripe_subscription_id)
        return datetime.fromtimestamp(subscription.current_period_end)