from django.conf.urls import patterns, include, url
from django.template.loader import add_to_builtins
from django.contrib import admin
from registration.forms import RegistrationFormUniqueEmail
from registration.backends.default.views import RegistrationView

from staphopia.settings.common import *

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'staphopia.views.index', name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^top10/', 'database.views.top10', name='top10'),
    url(r'^genomes/', 'database.views.genomes', name='genomes'),
    url(r'^contact/', 'staphopia.views.contact', name='contact'),
    
    # enable unique email registration feature
    url(r'^accounts/register/$',
        RegistrationView.as_view(form_class=RegistrationFormUniqueEmail),
        name='registration_register'),
    url(r'^accounts/', include('registration.backends.default.urls'))
)

for tag in AUTOLOAD_TEMPLATETAGS:
    add_to_builtins(tag)