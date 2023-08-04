from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from captcha.fields import CaptchaField

class FeedbackForm(forms.Form):
    name = forms.CharField(label='Name (optional)', required=False)
    email = forms.EmailField(label='Email (optional)', required=False)
    phone_number = forms.CharField(label='Phone Number (optional)', required=False)
    message = forms.CharField(label="Your feedback is important to us. Do you have anything else to add?", widget=forms.Textarea(attrs={'placeholder': 'Please share your feedback here'}))
    captcha = CaptchaField()

    helper = FormHelper()
    helper.form_method = 'POST'
    helper.add_input(Submit('submit', 'Send Feedback', css_class='btn-primary btn-block'))