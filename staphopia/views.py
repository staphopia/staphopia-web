from django.core.mail import EmailMessage
from django.shortcuts import render_to_response
from django.template import RequestContext
from staphopia.models import ContactForm

def index(request):
    return render_to_response('index.html', {}, RequestContext(request))
    
def login(request):
    return render_to_response('account/login.html')
    
def contact(request):
    if request.POST:
        form = ContactForm(request.POST)
        if form.is_valid():
            labrat = "Staphopia's Friendly Robot <usa300@staphopia.com>"
            sender = '{0} <{1}>'.format(form.cleaned_data['name'], 
                                        form.cleaned_data['email'])
            subject = '[Staphopia Contact] - ' + form.cleaned_data['subject']
            message = ("This is an autmated reply from Staphopia, we'll try to "
                       "answer you as quickly as possible.\n\n----------\n\n")
            message += form.cleaned_data['message']
            recipients = ['admin@staphopia.com', sender]
            email = EmailMessage(subject, message, labrat, recipients)
            email.send(fail_silently=False)

            return render_to_response(
                'contact/success.html',
                {},
                context_instance=RequestContext(request))
    else:
        form = ContactForm()

    return render_to_response('contact.html', {'form': form},
                              context_instance=RequestContext(request))
