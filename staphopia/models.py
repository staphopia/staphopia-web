from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField(max_length=100)
    subject = forms.CharField(max_length=200)
    message = forms.CharField(widget=forms.Textarea(), max_length=1000)
