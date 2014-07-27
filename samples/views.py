from django.shortcuts import render_to_response
from django.template import RequestContext

from samples.forms import SampleMetaDataForm

def submission(request):
    if request.user.is_authenticated:
        form = None
        save_results = None
        if request.method == 'POST':
            form = SampleMetaDataForm(request.user.id, request.POST)
            if form.is_valid():
                save_results = form.save(request.user.id, request.POST)
                return HttpResponseRedirect('submission/')
        else:
            form = SampleMetaDataForm(request.user.id)
        return render_to_response('submission.html', 
                                  {'form':form}, RequestContext(request))
    else:
        return HttpResponseRedirect('/')
    
def genomes(request):
    return render_to_response('genomes.html', {}, RequestContext(request))