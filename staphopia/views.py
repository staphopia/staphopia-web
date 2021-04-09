from django.shortcuts import render
from staphopia.forms import TokenForm


def index(request):
    return render(request, 'index.html')


def server_error(request):
    return render(request, 'server_error.html')


def TokenView(request):
    from django.contrib.auth.models import User
    from rest_framework.authtoken.models import Token
    from staphopia.utils import generate_random_password
    new_user = False
    has_error = None
    honeypot = False
    token = None
    if request.POST:
        form = TokenForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                if not form.cleaned_data['first_name'] or not form.cleaned_data['last_name']:
                    has_error = f"No API token associated with {email}, please provide a first and last name to generate a token."
                elif form.cleaned_data['password1'] or form.cleaned_data['password2']:
                    has_error = True
                    honeypot = True
                if not has_error:
                    first_name = form.cleaned_data['first_name']
                    last_name = form.cleaned_data['last_name']
                    password = generate_random_password()

                    user = User.objects.create_user(email, email, password)
                    user.first_name = first_name
                    user.last_name = last_name
                    user.save()

            if not has_error:
                try:
                    token = Token.objects.get(user=user)
                except Token.DoesNotExist:
                    token = Token.objects.create(user=user)

    form = TokenForm()
    return render(request, 'token.html', {'form': form, 'has_error': has_error, 'honeypot': honeypot, 'token': token})
