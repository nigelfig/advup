from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import auth
from memberships.models import UserMembership
from django.contrib.auth.decorators import login_required
from companies.models import Profile
from django.utils import timezone

import base64
from django.conf import settings
import gspread
from oauth2client import service_account
import json
from django.core.mail import send_mail

# Create your views here.
@login_required
def homepage(request):
    return redirect('dashboard')

def register(request):
    if request.method == "POST":
        # User has info and wants an account now!
        
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.get(email=request.POST['email'])
                return render(request, 'accounts/register.html', {'error': 'Email has already been taken'})
            except User.DoesNotExist:
                user = User.objects.create_user(request.POST['email'], password=request.POST['password1'])
                first_name = request.POST['firstname']
                last_name = request.POST['lastname']
                company_name = request.POST['companyname']
                phone_number = request.POST['phonenum']
                customer_email = request.POST['email']

                auth.login(request, user)
                company = Profile()
                company.businessperson = request.user
                company.first_name = first_name
                company.last_name = last_name
                company.company_name = company_name
                company.phone_number = phone_number
                company.create_date = timezone.now()
                company.save()

                if settings.NEW_REG_EMAIL_AND_SHEET == True:
                    byte_gdata = settings.ENCODED_GOOGLE_JSON.encode('utf-8')
                    newgdata = base64.b64decode(byte_gdata).decode('utf-8')
                    gdata = json.loads(newgdata)

                    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
                    credentials = service_account.ServiceAccountCredentials.from_json_keyfile_dict(gdata, scope)

                    gc = gspread.authorize(credentials)
                    wks = gc.open('AdvantageUp Registrations').sheet1
                    wks.append_row([first_name, last_name, company_name, phone_number, customer_email])

                    subject = "New AdvantageUp Registration"
                    from_email = "nigel@advantageup.com"
                    to_email = ["nigel@advantageup.com"]

                    email_message = f"New AdvantageUp Registration First Name: {first_name} Last Name: {last_name} Company: {company_name} Phone Number: {phone_number} Email: {customer_email}"

                    html_email_message = f"<h2>New AdvantageUp Registration</h2>First Name: {first_name}<br/>Last Name: {last_name}<br/>Company: {company_name}<br/> Phone Number: {phone_number}<br/>Email: {customer_email}"

                    send_mail(subject, email_message, from_email, to_email, fail_silently=True, html_message=html_email_message)


                return redirect('memberships:payment')
        else:
            return render(request, 'accounts/register.html', {'error': 'Passwords must match'})
    # User wants to enter info
    return render(request, 'accounts/register.html')

def login(request):
    if request.method == "POST":
        user = authenticate(email=request.POST["email"], password=request.POST["password"])
        if user is not None:
            # Our backend authenticated the credentials
            auth_login(request, user)
            return redirect('dashboard')
        else:
            # Backend did not authenticate the credentials
            return render(request, 'accounts/login.html', {"error": "Incorrect email and or password"})

    else:
        return render(request, 'accounts/login.html')

def logout(request):
    auth.logout(request)
    return redirect('login')


