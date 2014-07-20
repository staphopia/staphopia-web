from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from staphopia.models import ContactForm
from django.template import RequestContext, Context
from django import forms
from django.core.mail import send_mail, BadHeaderError

def index(request):
    return render_to_response('index.html', {}, RequestContext(request))
    
def top10(request):
    return render_to_response('top10.html', {}, RequestContext(request))
    
def genomes(request):
    return render_to_response('genomes.html', {}, RequestContext(request))
    
def login(request):
    return render_to_response('account/login.html')
    
def contact(request):
    subject = request.POST.get('subject', '')
    message = request.POST.get('message', '')
    from_email = request.POST.get('email', '')

    if subject and message and from_email:
        try:
            send_mail(subject, message, from_email, ['change@this.com'])
        except BadHeaderError:
            return HttpResponse('Invalid header found.')
        return HttpResponseRedirect('/contact/thankyou/')
    else:
        return render_to_response('contact.html', {'form': ContactForm()}, 
                                  RequestContext(request))

def thankyou(request):
    return render_to_response('thankyou.html')