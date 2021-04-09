from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from crispy_forms.bootstrap import *


class TokenForm(forms.Form):
    first_name = forms.CharField(max_length=50, label='First Name', required=False)
    last_name = forms.CharField(max_length=50, label='Last Name', required=False)
    email = forms.EmailField(max_length=100, required=True)
    password1 = forms.CharField(required=False, widget=forms.HiddenInput(),)
    password2 = forms.CharField(required=False, widget=forms.HiddenInput(),)

    helper = FormHelper()
    helper.form_method = 'POST'
    helper.form_id = 'token-form'
    helper.form_class = ''
    helper.form_action = ''
    helper.add_input(Submit('submit', 'Submit'))
