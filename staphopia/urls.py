from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView
from django.template.loader import add_to_builtins
from django.contrib import admin
from django.contrib.auth import views as auth_views
from registration.forms import RegistrationFormUniqueEmail
from registration.backends.default.views import RegistrationView, ActivationView
from django_email_changer.views import CreateUserEmailModificationRequest, ActivateUserEmailModification, ActivationEmailSentSuccessView

from database.views import SummaryDatatablesView
from staphopia.forms import RegistrationFormWithName
from staphopia.settings.common import *
import staphopia.signals

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'staphopia.views.index', name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^submission/', 'samples.views.submission', name='submission'),
    url(r'^top10/', 'database.views.top10', name='top10'),
    url(r'^contact/', 'staphopia.views.contact', name='contact'),
    url(r'^accounts/settings/', 'staphopia.views.account_settings', name='account_settings'),
    
    # Samples
    url(r'^samples/data/$', SummaryDatatablesView.as_view(), name='samples_data'),
    url(r'^samples/(?P<sample_tag>[^/]+)/', 'database.views.samples', name='sample_results'),
    url(r'^samples/$', 'database.views.samples', name='samples'),

    
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
            auth_views.password_reset_confirm,
            name='auth_password_reset_confirm'),
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
        {'post_reset_redirect' : '/accounts/password/reset/done/'},
        name="password_reset"),
    url('^accounts/activate/$', ActivationView.as_view(),
                               {'activation_key':'None'}, 
                               name='registration_activate'),
    # enable unique email registration feature
    url(r'^accounts/register/$',
        RegistrationView.as_view(form_class=RegistrationFormWithName),
        name='registration_register'),
    url(r'^accounts/', include('registration.backends.default.urls')),
)

for tag in AUTOLOAD_TEMPLATETAGS:
    add_to_builtins(tag)