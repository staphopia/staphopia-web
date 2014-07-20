from django.conf.urls import patterns, include, url
from django.template.loader import add_to_builtins
from django.contrib import admin
from staphopia.settings.common import *
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'staphopia.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', 'staphopia.views.index', name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r"^account/", include('account.urls')),
    url(r"^account/", 'staphopia.views.login'),
    url(r'^contact/thankyou/', 'staphopia.views.thankyou'),
    url(r'^contact/', 'staphopia.views.contact', name='contact'),
)

for tag in AUTOLOAD_TEMPLATETAGS:
    add_to_builtins(tag)