from django import forms
from django.contrib.auth.models import User

from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from crispy_forms.bootstrap import *
from registration.forms import RegistrationFormUniqueEmail


class RegistrationFormWithName(RegistrationFormUniqueEmail):
    first_name = forms.CharField(max_length=50, label='First Name')
    last_name = forms.CharField(max_length=50, label='Last Name')


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField(max_length=100)
    subject = forms.CharField(max_length=200)
    message = forms.CharField(widget=forms.Textarea(), max_length=1000)

    helper = FormHelper()
    helper.form_method = 'POST'
    helper.form_id = 'contact-form'
    helper.form_class = ''
    helper.form_action = ''
    helper.add_input(Submit('submit', 'Contact'))


class UserEmailForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('email',)
