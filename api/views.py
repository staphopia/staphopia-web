from django.shortcuts import render, redirect


def api_token(request):
    if request.user.is_authenticated:
        return render(request, 'settings/api-token.html')
<<<<<<< HEAD
    return redirect(request, 'accounts/login/')
=======
    return redirect('/accounts/login/')
>>>>>>> 9f859aeb4fa94c876d736e9596574c0d656c4d95
