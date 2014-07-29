from django.contrib.auth.models import Group

from staphopia.forms import RegistrationFormWithName

def user_created(sender, user, request, **kwargs):
    form = RegistrationFormWithName(request.POST)
    user.first_name = form.data['first_name']
    user.last_name = form.data['last_name']
    user.save()
    Group.objects.get(name='public').user_set.add(user)

from registration.signals import user_registered
user_registered.connect(user_created)
