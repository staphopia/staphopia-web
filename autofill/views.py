from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from autofill.forms import AutoFillForm

def index(request):
    if request.user.is_authenticated:
        form = None
        if request.method == 'POST':
            form = AutoFillForm(request.user.id, request.POST)
            if form.is_valid():
                form.save(request.user.id, request.POST)
                return HttpResponseRedirect('/settings/autofill/')
        else:
            form = AutoFillForm(request.user.id)
        return render_to_response('settings/autofill.html',
                                  {'form': form}, RequestContext(request))
    else:
        return HttpResponseRedirect('/')
