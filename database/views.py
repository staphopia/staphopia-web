from django.shortcuts import render_to_response
from django.template import RequestContext

def top10(request):
    return render_to_response('top10.html', {}, RequestContext(request))
    
def genomes(request):
    return render_to_response('genomes.html', {}, RequestContext(request))
