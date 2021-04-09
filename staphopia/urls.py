from django.conf.urls import include, url
from django.views.generic import RedirectView
from django.contrib import admin
from django.views.generic.base import TemplateView

# Staphopia
from staphopia.settings.common import *

# Views
import staphopia.views
import sample.views
import api.views

# API ViewSet Routers
from api.routers import router

admin.autodiscover()

handler500 = 'staphopia.views.server_error'

urlpatterns = [
    # Django REST Framework
    url(r'^api/', include(router.urls)),

    # Admin Site
    url(r'^admin/', admin.site.urls),
    url(r'^top10/$', sample.views.top10, name='top10'),

    # generate token
    url(r'^token/$', staphopia.views.TokenView, name='token'),

    url(r'^$', staphopia.views.index, name='home'),
    url(r'^.*$', RedirectView.as_view(url='/',)),
]
