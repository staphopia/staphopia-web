from django.conf.urls import include, url
from django.views.generic import RedirectView
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.core.urlresolvers import reverse_lazy

from rest_framework.authtoken import views as token_views

# Thrid Party Apps
from django_email_changer.views import (
    ActivateUserEmailModification,
    ActivationEmailSentSuccessView,
    CreateUserEmailModificationRequest,
)

# Registrations

# Staphopia
from staphopia.forms import RegistrationFormWithName
from staphopia.settings.common import *

# Views
import staphopia.views
import sample.views
import api.views

# API ViewSet Routers
from api.routers import router

admin.autodiscover()

urlpatterns = [
    # Django REST Framework
    url(r'^api/', include(router.urls)),
    url(r'^settings/api-token/', api.views.api_token, name='api-token'),

    # Grappelli & Admin Site
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^top10/', sample.views.top10, name='top10'),
    url(r'^contact/', staphopia.views.contact, name='contact'),
    url(r'^settings/account/', staphopia.views.account_settings,
        name='account_settings'),

    # Samples
    url(r'^samples/data/$', sample.views.sample_summary,
        name='samples_data'),
    url(r'^samples/(?P<sample_tag>[^/]+)/$', sample.views.sample,
        name='sample_results'),
    url(r'^samples/$', sample.views.sample, name='samples'),

    # Autofill Genome Submission fields
    url(r'^settings/autofill/', include('autofill.urls'), name='autofill'),

    # django-email-changer
    url(r'settings/email/change/activate/(?P<code>[^/]+)/',
        ActivateUserEmailModification.as_view(),
        name="django_change_email_activate_new_email"),
    url(r'^settings/email/change/sent/$',
        ActivationEmailSentSuccessView.as_view(),
        name="django_change_email_sent_activation_email"),
    url(r'^settings/email/$',
        CreateUserEmailModificationRequest.as_view(),
        name="django_email_changer_change_view"),

    # django-registration
    # url(r'^accounts/$', RedirectView.as_view(url='/',)),
    url(r'^accounts/register/$', staphopia.views.RegistrationView.as_view(),
        name='registration_register'),
    url('^accounts/', include('registration.urls')),

    # Fix for password reset
    url(r'^accounts/password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        auth_views.password_reset_confirm, name='auth_password_reset_confirm'),
    url(r'^password/reset/complete/$',
        auth_views.password_reset_complete,
        name='password_reset_complete'),
    url(r'^password/change/done/$',
        auth_views.password_change_done,
        name='password_change_done'),
    url(r'^accounts/password/reset/confirm/$',
        RedirectView.as_view(url='/',)),
    url(r'^accounts/password/reset/$', auth_views.password_reset,
        {'post_reset_redirect': '/accounts/password/reset/done/'},
        name="password_reset"),
    #url('^accounts/activate/$', ActivationView.as_view(),
    #    {'activation_key': 'None'}, name='registration_activate'),
    url(r'^settings/admin/$',
        auth_views.password_change,
        {'post_change_redirect': reverse_lazy('auth_password_change_done')},
        name='auth_password_change'),

    # enable unique email registration feature
    #url(r'^accounts/', include(registration.backends.default.urls)),

    url(r'^$', staphopia.views.index, name='home'),
]
