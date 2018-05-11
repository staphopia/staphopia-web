from django.shortcuts import render, redirect


def api_token(request):
    if request.user.is_authenticated:
        return render(request, 'settings/api-token.html')
    return redirect(request, 'accounts/login/')
