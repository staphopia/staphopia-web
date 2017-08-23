from django import forms
from django.forms.models import ModelForm
from django.contrib.auth.models import User

from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from crispy_forms.bootstrap import *

from registration.forms import RegistrationFormUniqueEmail
from django_email_changer.models import UserEmailModification


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


class UserEmailModificationForm(ModelForm):
    class Meta:
        model = UserEmailModification
        fields = ("new_email", )

    confirmed_email = forms.EmailField(
        required=True,
        label="Confirm Email"
    )
    password = forms.CharField(
        required=True,
        label="Your Password",
        widget=forms.PasswordInput
    )

    def clean(self):
        cleaned_data = super(UserEmailModificationForm, self).clean()
        new_email = cleaned_data.get("new_email")
        confirmed_email = cleaned_data.get("confirmed_email")
        if new_email == confirmed_email:
            if User.objects.filter(email=new_email).exists():
                raise forms.ValidationError(
                    "The email {0} is already in use, please use "
                    "another one.".format(new_email)
                )
            else:
                return cleaned_data
        else:
            raise forms.ValidationError(
                "Please provide matching emails."
            )
