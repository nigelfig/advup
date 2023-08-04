from django.shortcuts import render, get_object_or_404
from companies.models import Profile
from stores.models import Place
from sendreview.views import check_paid, check_base

# Create your views here.
def support(request):
    user_type = check_paid(request)
    if user_type.membership.membership_type == "FREE":
        return redirect('memberships:payment')
    else:
        my_base = check_base(request)
        profile = Profile.objects.get(businessperson=request.user)
        places = Place.objects.filter(businessperson=request.user)
        store = ""
        if places.count() == 1:
            store = get_object_or_404(Place, businessperson=request.user)

        return render(request, 'support/support.html', {
            "profile": profile,
            "my_base": my_base,
            "store": store,
        })