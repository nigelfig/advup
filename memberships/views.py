from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
# Create your views here.
from .models import Membership, UserMembership, Subscription
import stripe
from django.contrib.auth import get_user_model
User = get_user_model()

@login_required(login_url="/signup")
def get_user_membership(request):
    user_membership_qs = UserMembership.objects.filter(user=request.user)
    if user_membership_qs.exists():
        return user_membership_qs.first()
    return None

def get_monthly_membership(request):
    selected_membership_qs = Membership.objects.filter(
            membership_type='PROM'
    ) 
    if selected_membership_qs.exists():
        return selected_membership_qs.first()
    return None

def get_annual_membership(request):
    selected_membership_qs = Membership.objects.filter(
            membership_type='PROA'
    ) 
    if selected_membership_qs.exists():
        return selected_membership_qs.first()
    return None

def PaymentView(request):
    user_membership = get_user_membership(request)
    monthly_membership = get_monthly_membership(request)
    annual_membership = get_annual_membership(request)
    stripe_publish_key = settings.STRIPE_PUBLISHABLE_KEY


    if request.method == "POST":
        try:

            token = request.POST['stripeToken']
            quantity = int(request.POST['quant'])
            plan = request.POST['plan']
            stripe.Customer.modify( user_membership.stripe_customer_id, source = token)

            selected_membership_qs = Membership.objects.filter(
                membership_type=plan
            ) 
            selected_membership = selected_membership_qs.first()

            subscription = stripe.Subscription.create(
                customer=user_membership.stripe_customer_id,
                items=[
                    {
                        "plan": selected_membership.stripe_plan_id,
                        'quantity': quantity,
                    },
                ],
            )

            user_membership.membership = selected_membership
            user_membership.locations = quantity
            user_membership.save()

            return redirect(reverse('memberships:update-transactions',
                                    kwargs={
                                        'subscription_id': subscription.id,
                                    }))

        except:
            messages.info(request, "Payment did not go through")

    annual_monthly_price = int(annual_membership.price / 12)
    savings  =  monthly_membership.price*12 - annual_membership.price

    context = {
        'stripe_publish_key': stripe_publish_key,
        'monthly_membership': monthly_membership,
        'annual_membership': annual_membership,
        'savings': savings,
        'annual_monthly_price': annual_monthly_price
    }

    return render(request, "memberships/membership_payment.html", context)

def updateTransactions(request, subscription_id):
    user_membership = get_user_membership(request)

    sub, created = Subscription.objects.get_or_create(user_membership=user_membership)
    sub.stripe_subscription_id = subscription_id
    sub.active = True
    sub.save()
  
    messages.info(request, "Successfully created membership")
    return redirect(reverse('create'))
