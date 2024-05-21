from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

@login_required(login_url="/auth/login/")
def home(request):
    return render(request, 'home.html')

@login_required(login_url="/auth/login/")
def logout(request):
    return render(request, 'logout.html')

@login_required(login_url="/auth/login/")
def logout_view(request):
    logout(request)
    url_login = reverse('login')
    return redirect(url_login)