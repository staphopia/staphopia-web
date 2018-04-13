from django.core.mail import EmailMessage, send_mail
from django.urls import reverse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.contrib.auth import get_backends
from django.views.generic import FormView
from django.views.generic.edit import ProcessFormView, FormMixin
from django.views.generic.base import TemplateResponseMixin

# from registration.backends import get_backend
# from django_email_changer import settings
# from django_email_changer.models import UserEmailModification

from staphopia.forms import (
    ContactForm,
    RegistrationFormWithName,
    # UserEmailModificationForm
)


def index(request):
    return render(request, 'index.html')


def account_settings(request):
    return render(request, 'settings/settings.html')

    def get(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        supplement_form_class = self.get_supplement_form_class()
        supplement_form = self.get_supplement_form(supplement_form_class)
        context = self.get_context_data(
                form=form, supplement_form=supplement_form)
        return self.render(context)


def contact(request):
    email_sent = False
    if request.POST:
        form = ContactForm(request.POST)
        if form.is_valid():
            labrat = "Staphopia's Friendly Robot <usa300@staphopia.com>"
            sender = '{0} <{1}>'.format(form.cleaned_data['name'],
                                        form.cleaned_data['email'])
            subject = '[Staphopia Contact] - ' + form.cleaned_data['subject']
            message = ("This is an automated reply from Staphopia, we'll try "
                       "to answer you as quickly as possible.\n\n--------\n\n")
            message += form.cleaned_data['message']
            recipients = ['admin@staphopia.com', 'robert.petit@emory.edu',
                          sender]
            email = EmailMessage(subject, message, labrat, recipients)
            try:
                email.send(fail_silently=False)
                email_sent = True
            except Exception:
                email_sent = False

    form = ContactForm()
    return render(request, 'contact.html', {'form': form, 'email': email_sent})


class RegistrationView(FormMixin, TemplateResponseMixin, ProcessFormView):
    """A complex view for registration
    GET:
        Display an RegistrationForm which has ``username``, ``email1`` and ``email2``
        for registration.
        ``email1`` and ``email2`` should be equal to prepend typo.
        ``form`` and ``supplement_form`` is in context to display these form.
    POST:
        Register the user with passed ``username`` and ``email1``
    """
    template_name = r'registration/registration_form.html'

    def __init__(self, *args, **kwargs):
        self.backend = get_backends()[0]
        super(RegistrationView, self).__init__(*args, **kwargs)

    def get_success_url(self):
        """get registration complete url via backend"""
        return self.backend.get_registration_complete_url(self.new_user)

    def get_disallowed_url(self):
        """get registration closed url via backend"""
        return self.backend.get_registration_closed_url()

    def get_form_class(self):
        """get registration form class via backend"""
        # return self.backend.get_registration_form_class()
        return RegistrationFormWithName

    def get_supplement_form_class(self):
        """get registration supplement form class via backend"""
        return self.backend.get_supplement_form_class()

    def get_supplement_form(self, supplement_form_class):
        """get registration supplement form instance"""
        if not supplement_form_class:
            return None
        return supplement_form_class(**self.get_form_kwargs())

    def form_valid(self, form, supplement_form=None):
        """register user with ``username`` and ``email1``
        this method is called when form validation has successed.
        """
        username = form.cleaned_data['username']
        email = form.cleaned_data['email1']
        if supplement_form:
            supplement = supplement_form.save(commit=False)
        else:
            supplement = None
        self.new_user = self.backend.register(username, email,
                                              self.request,
                                              supplement=supplement)
        self.new_user.first_name = form.cleaned_data['first_name']
        self.new_user.last_name = form.cleaned_data['last_name']
        self.new_user.save()
        profile = self.new_user.registration_profile
        # save the profile on the session so that the RegistrationCompleteView
        # can refer the profile instance.
        # this instance is automatically removed when the user accessed
        # RegistrationCompleteView
        self.request.session['registration_profile_pk'] = profile.pk
        return super(RegistrationView, self).form_valid(form)

    def form_invalid(self, form, supplement_form=None):
        context = self.get_context_data(
            form=form,
            supplement_form=supplement_form
        )
        return render(self.request, self.template_name, context)

    def get(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        supplement_form_class = self.get_supplement_form_class()
        supplement_form = self.get_supplement_form(supplement_form_class)
        context = self.get_context_data(
                form=form, supplement_form=supplement_form)
        return render(self.request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        supplement_form_class = self.get_supplement_form_class()
        supplement_form = self.get_supplement_form(supplement_form_class)
        if form.is_valid() and (
            not supplement_form or supplement_form.is_valid()
        ):
            return self.form_valid(form, supplement_form)
        else:
            return self.form_invalid(form, supplement_form)

    def dispatch(self, request, *args, **kwargs):
        if not self.backend.registration_allowed():
            # registraion has closed
            return redirect(self.get_disallowed_url())
        return super(RegistrationView, self).dispatch(request, *args, **kwargs)


'''
class CreateUserEmailModificationRequest(FormView):
    form_class = UserEmailModificationForm
    http_method_names = ["get", "post", ]
    template_name = "django_email_changer/change_email_form.html"

    def get_success_url(self, **kwargs):
        return reverse(settings.EMAIL_CHANGE_SUCCESS_URL)

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            if not request.user.check_password(
                form.cleaned_data.get("password")
            ):
                form.errors["password"] = [u'Incorrect password.']
                return self.form_invalid(form)
            new_email = form.cleaned_data.get("new_email")
            uem = UserEmailModification.objects.create(
                user=request.user, new_email=new_email
            )
            email_body = render_to_string(
                settings.EMAIL_CHANGE_NOTIFICATION_EMAIL_TEMPLATE,
                {"email_modification": uem, "request": request, }
            )
            thread = Thread(target=send_mail,
                            args=[settings.EMAIL_CHANGE_NOTIFICATION_SUBJECT,
                                  email_body,
                                  settings.EMAIL_CHANGE_NOTIFICATION_FROM,
                                  (uem.new_email, )],
                            kwargs={"fail_silently": True})
            thread.setDaemon(True)
            thread.start()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
'''
