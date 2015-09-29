from django.core.mail import EmailMessage
from django.shortcuts import render_to_response
from django.template import RequestContext

from staphopia.forms import ContactForm


def index(request):
    return render_to_response('index.html', {}, RequestContext(request))


def account_settings(request):
    return render_to_response('accounts/settings.html', {},
                              RequestContext(request))


def contact(request):
    email_sent = False
    if request.POST:
        form = ContactForm(request.POST)
        if form.is_valid():
            labrat = "Staphopia's Friendly Robot <usa300@staphopia.com>"
            sender = '{0} <{1}>'.format(form.cleaned_data['name'],
                                        form.cleaned_data['email'])
            subject = '[Staphopia Contact] - ' + form.cleaned_data['subject']
            message = ("This is an automated reply from Staphopia, we'll try "
                       "to answer you as quickly as possible.\n\n--------\n\n")
            message += form.cleaned_data['message']
            recipients = ['admin@staphopia.com', 'robert.petit@emory.edu',
                          sender]
            email = EmailMessage(subject, message, labrat, recipients)
            try:
                email.send(fail_silently=False)
                email_sent = True
            except Exception:
                email_sent = False

    form = ContactForm()

    return render_to_response(
        'contact.html',
        {'form': form, 'email': email_sent},
        context_instance=RequestContext(request)
    )
