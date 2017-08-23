from django.shortcuts import render


def api_token(request):
    return render(request, 'settings/api-token.html')
