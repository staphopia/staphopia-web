from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView
from django.contrib import admin
from django.contrib.auth import views as auth_views

# from rest_framework import routers
from registration.backends.default.views import (
    ActivationView,
    RegistrationView
)
from django_email_changer.views import (
    ActivateUserEmailModification,
    ActivationEmailSentSuccessView,
    CreateUserEmailModificationRequest,
)

# from api.views import (
#     sample_list,
#     VariantViewSet,
# )
from samples.views import SummaryDatatablesView
from staphopia.forms import RegistrationFormWithName
from staphopia.settings.common import *

admin.autodiscover()


# Routers provide an easy way of automatically determining the URL conf.
# router = routers.DefaultRouter()
# router.register(r'variant', VariantViewSet)
# router.register(r'sample(?P<sample_tag>[^/]+)/', sample_list)

urlpatterns = patterns(
    '',
    # Django REST Framework
    # url(r'^api/', include(router.urls)),
    # url(r'^api-auth/', include('rest_framework.urls',
    #     namespace='rest_framework')),

    # Grappelli & Admin Site
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', 'staphopia.views.index', name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^submission/', 'samples.views.submission', name='submission'),
    url(r'^top10/', 'samples.views.top10', name='top10'),
    url(r'^contact/', 'staphopia.views.contact', name='contact'),
    url(r'^accounts/settings/', 'staphopia.views.account_settings',
        name='account_settings'),

    # Samples
    url(r'^samples/data/$', SummaryDatatablesView.as_view(),
        name='samples_data'),
    url(r'^samples/(?P<sample_tag>[^/]+)/', 'samples.views.samples',
        name='sample_results'),
    url(r'^samples/$', 'samples.views.samples', name='samples'),

    # django-email-changer
    url(r'accounts/email/change/activate/(?P<code>[^/]+)/',
        ActivateUserEmailModification.as_view(),
        name="django_change_email_activate_new_email"),
    url(r'^accounts/email/change/sent/$',
        ActivationEmailSentSuccessView.as_view(),
        name="django_change_email_sent_activation_email"),
    url(r'^accounts/email/change/$',
        CreateUserEmailModificationRequest.as_view(),
        name="django_email_changer_change_view"),

    # Autofill Genome Submission fields
    url(r'^accounts/autofill/', include('autofill.urls'), name='autofill'),

    # django-registration
    url(r'^accounts/$', RedirectView.as_view(url='/',)),
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
    url(r'^accounts/password/reset/$',
        'django.contrib.auth.views.password_reset',
        {'post_reset_redirect': '/accounts/password/reset/done/'},
        name="password_reset"),
    url('^accounts/activate/$', ActivationView.as_view(),
        {'activation_key': 'None'}, name='registration_activate'),

    # enable unique email registration feature
    url(r'^accounts/register/$',
        RegistrationView.as_view(form_class=RegistrationFormWithName),
        name='registration_register'),
    url(r'^accounts/', include('registration.backends.default.urls')),
)
