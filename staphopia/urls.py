from django.conf.urls import include, url
from django.views.generic import RedirectView
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.core.urlresolvers import reverse_lazy

# Thrid Party Apps
from django_email_changer.views import (
    ActivateUserEmailModification,
    ActivationEmailSentSuccessView,
    CreateUserEmailModificationRequest,
)
from organizations.backends import invitation_backend

# Staphopia
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
    url(r'^top10/$', sample.views.top10, name='top10'),
    url(r'^contact/$', staphopia.views.contact, name='contact'),
    url(r'^settings/account/', staphopia.views.account_settings,
        name='account_settings'),

    # Samples
    url(r'^sample/data/$', sample.views.sample_summary,
        name='samples_data'),
    url(r'^sample/(?P<sample_id>[0-9]+)/?$', sample.views.sample,
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
    url(r'^accounts/register/$', staphopia.views.RegistrationView.as_view(),
        name='registration_register'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout',
        {'next_page': '/'}),
    url('^accounts/', include('registration.urls')),

    # django-organizations
    url(r'^groups/', include('organizations.urls')),
    url(r'^invitations/', include(invitation_backend().get_urls())),

    # Charts
    # url(r'^chart-data/sequencing-centers/$',
    #    sample.charts.top_sequencing_centers,
    #    name='chart_centers'),

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
    url(r'^settings/admin/$',
        auth_views.password_change,
        {'post_change_redirect': reverse_lazy('auth_password_change_done')},
        name='auth_password_change'),
    url(r'^$', staphopia.views.index, name='home'),
    url(r'^.*$', RedirectView.as_view(url='/',)),
]
