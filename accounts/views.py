from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def index(request):
    """Redirect to login if not logged in, otherwise show home."""
    if request.user.is_authenticated:
        return redirect('home')
    else:
        return redirect('login')


@login_required
def home(request):
    """Home page for logged-in users."""
    return render(request, 'home.html')