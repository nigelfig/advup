from django.shortcuts import render, redirect, get_object_or_404,reverse
from sendreview.views import check_paid, check_base
from .models import Profile
from stores.models import Place
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone

# Create your views here.
@login_required()
def profile(request):
    if request.method == "POST":
        profile = get_object_or_404(Profile, businessperson=request.user)
        profile.first_name = request.POST['firstname']
        profile.last_name = request.POST['lastname']
        profile.company_name = request.POST['companyname']
        profile.phone_number = request.POST['phonenum']
        profile.create_date = timezone.now()
        profile.save()
        messages.info(request, "Successfully updated profile")
        return HttpResponseRedirect(reverse('profile'))
    else:
        user_type = check_paid(request)
        if user_type.membership.membership_type == "Free":
            return redirect('memberships:payment')
        else:
            profile = Profile.objects.get(businessperson=request.user)
            places = Place.objects.filter(businessperson=request.user)
            store = ""
            if places.count() == 1:
                store = get_object_or_404(Place, businessperson=request.user)
            my_base = check_base(request)
            return render(request, 'companies/profile.html', {
                "profile": profile,
                "my_base": my_base,
                "store": store,
                })