from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from crispy_forms.bootstrap import *

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
