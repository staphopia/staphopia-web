from django.conf.urls import patterns, url
from django.views.generic import RedirectView

from staphopia.settings.common import *

urlpatterns = patterns(
    '',
    url(r'^$', 'staphopia.views.index', name='home'),
    url(r'^top10/', 'sample.views.top10', name='top10'),
    url(r'^contact/', 'staphopia.views.contact', name='contact'),

    # Samples
    url(r'^samples/data/$', 'sample.views.sample_summary',
        name='samples_data'),
    url(r'^samples/(?P<sample_tag>[^/]+)/$', 'sample.views.sample',
        name='sample_results'),
    url(r'^samples/$', 'sample.views.sample', name='samples'),
    url(r'^.*$',
        RedirectView.as_view(url='/', permanent=False),
        name='index'),
)
