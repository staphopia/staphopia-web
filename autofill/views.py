from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext


from autofill.forms import AutoFillForm
 
@login_required
def index(request):
    if request.user.is_authenticated:
        form = None
        save_results = None
        if request.method == 'POST':
            form = AutoFillForm(request.user.id, request.POST)
            if form.is_valid():
                save_results = form.save(request.user.id, request.POST)
                return HttpResponseRedirect('/accounts/autofill/')
        else:
            form = AutoFillForm(request.user.id)
        return render_to_response('accounts/autofill.html', 
                                  {'form':form}, RequestContext(request))
    else:
        return HttpResponseRedirect('/')
