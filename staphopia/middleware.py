from django.http import HttpResponseRedirect
from django.conf import settings
from django.core.urlresolvers import reverse
from re import compile

def get_login_url():
    return settings.LOGIN_URL
 
def get_exempts():
    exempts = []
    if hasattr(settings, 'LOGIN_EXEMPT_URLS'):
        exempts += [compile(expr) for expr in settings.LOGIN_EXEMPT_URLS]
    return exempts
 
 
class LoginRequiredMiddleware(object):
    """
    Middleware that requires a user to be authenticated to view any page other
    than reverse(LOGIN_URL). Exemptions to this requirement can optionally
    be specified in settings via a list of regular expressions in
    LOGIN_EXEMPT_URLS (which you can copy from your urls.py).
 
    Requires authentication middleware and template context processors to be
    loaded. You'll get an error if they aren't.
    
    https://gist.github.com/TomasTomecek/5056424
    """
    def process_request(self, request):
        assert hasattr(request, 'user'), "The Login Required middleware\
            requires authentication middleware to be installed. Edit your\
            MIDDLEWARE_CLASSES setting to insert\
            'django.contrib.auth.middlware.AuthenticationMiddleware'. If that\
            doesn't work, ensure your TEMPLATE_CONTEXT_PROCESSORS setting includes\
            'django.core.context_processors.auth'."
        if not request.user.is_authenticated():
            path = request.path.lstrip('/')
            if not any(m.match(path) for m in get_exempts()):
                return HttpResponseRedirect(get_login_url() + "?next=" + request.path)