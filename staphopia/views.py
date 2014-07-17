from django.shortcuts import render_to_response
from django.template import RequestContext

def index(request):
    return render_to_response('index.html')
    
def login(request):
    return render_to_response('account/login.html')