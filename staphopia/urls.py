from django.conf.urls import patterns, include, url
from django.template.loader import add_to_builtins
from django.contrib import admin
from staphopia.settings.common import *
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'staphopia.views.index', name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^top10/', 'database.views.top10', name='top10'),
    url(r'^genomes/', 'database.views.genomes', name='genomes'),
    url(r'^contact/', 'staphopia.views.contact', name='contact'),
)

for tag in AUTOLOAD_TEMPLATETAGS:
    add_to_builtins(tag)