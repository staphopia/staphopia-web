from django.shortcuts import render_to_response
from django.template import RequestContext


def api_token(request):
    return render_to_response('settings/api-token.html', {},
                              RequestContext(request))
