from django.shortcuts import render, get_object_or_404, redirect
from stores.models import Place, PlaceDetail
from links.models import ReviewLink, ReviewLinkType
from .models import Review
from django.http import HttpResponseRedirect
from .forms import FeedbackForm
from django.urls import reverse

# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


# Create your views here.

def recommend_shop(request, slug):
    if request.method == "POST":
        return HttpResponseRedirect(reverse('dashboard'))
    else:
        print("before store ")
        store = get_object_or_404(Place, slug=slug)
        main_review_type = store.main_review_type
        print("after store ")
        print(main_review_type)
        review_link = get_object_or_404(ReviewLink, store=store, review_link_type=main_review_type)
        complete_review_link = "https://" + review_link.short_url

        return render(request, 'shops/recommend_shop.html', {
                    "store": store,
                    "review_link": complete_review_link,
                    "slug": slug
                })

def shop_feedback(request, slug):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = FeedbackForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            customer_name = form.cleaned_data['name']
            customer_email = form.cleaned_data['email']
            customer_phone_number = form.cleaned_data['phone_number']
            message = form.cleaned_data['message']
            initial_subject = "Feedback from Customer - AdvantageUp"
            from_email = 'AdvantageUp Support <support@advantageup.com>'

            store = get_object_or_404(Place, slug=slug)
            to_email = list(person.email for person in store.businessperson.all())

            store_name = store.placename

            subject = f"Feedback from Customer for {store_name}"

            if len(subject) > 80:
                subject = initial_subject


            email_message = f"AdvantageUp Customer Feedback A customer {customer_name} {customer_email} {customer_phone_number} who clicked thumbs down was directed to feedback page and left the following comments {message}"

            html_email_message = f"<h3>AdvantageUp Customer Feedback</h3><h4>A customer {customer_name} {customer_email} {customer_phone_number} who clicked thumbs down was directed to feedback page and left the following comments</h4><p>{message}</p>"

            message = Mail(
                from_email=from_email,
                to_emails=to_email,
                subject=subject,
                html_content=html_email_message)
            try:
                sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
                response = sg.send(message)
                print(response.status_code)
                print(response.body)
                print(response.headers)

            except:
                pass
            

            return redirect('feedback_thanks', slug=slug)

    # if a GET (or any other method) we'll create a blank form
    else:
        form = FeedbackForm()
    
    store = get_object_or_404(Place, slug=slug)

    return render(request, 'shops/feedback.html',{
                    'form': form,
                    "store": store,
                }) 

def feedback_thanks(request, slug):
    if request.method == "POST":
        pass
    else:
        store = get_object_or_404(Place, slug=slug)

        return render(request, 'shops/feedback_thanks.html', {
                    "store": store,
                })

def shop(request, slug):
    if request.method == "POST":
        pass
    else:
        store = get_object_or_404(Place, slug=slug)
        store_detail = get_object_or_404(PlaceDetail, place=store)

        reviews = Review.objects.filter(store=store)

        return render(request, 'shops/shop.html', {
                    "store": store,
                    "detail": store_detail,
                    "slug": slug,
                    "reviews": reviews
                })


