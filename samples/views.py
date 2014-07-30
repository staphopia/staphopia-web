from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db import transaction

from samples.forms import SampleMetaDataForm

@transaction.commit_on_success
def submission(request):
    if request.user.is_authenticated:
        form = None
        save_results = None
        if request.method == 'POST':
            form = SampleMetaDataForm(request.user.id, request.POST, request.FILES)
            if form.is_valid():
                sample = form.create_new_sample(
                    request.user.id,
                    True if 'is_public' in request.POST else False,
                    True if 'is_paired' in request.POST else False
                )
                save_results = form.save_metadata(request.user, sample.pk, request.POST)
                save_upload = form.save_upload(sample.pk, request.FILES)
                return HttpResponseRedirect('/')
        else:
            form = SampleMetaDataForm(request.user.id)
        return render_to_response('submission.html', 
                                  {'form':form}, RequestContext(request))
    else:
        return HttpResponseRedirect('/')
    
