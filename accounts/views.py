from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages 
from .forms import CustomUserCreationForm, BirthdayForm
from .models import Profile

def index(request):
    #redirect to login if not logged in, otherwise show home
    if request.user.is_authenticated:
        return redirect('home')
    else:
        return redirect('login')


def login_view(request):
    #simple login page that checks username + password
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            profile, created = Profile.objects.get_or_create(user=user)

            if not profile.birthday:
                return redirect('birthday')

            return redirect('home')
        else:
            return render(
                request,
                'registration/login.html',
                {"error": "Invalid username or password"}
            )

    return render(request, 'registration/login.html')

@login_required
def birthday_view(request):
    """Step 2 of registration: collect birthday."""
     # Get the user's profile
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = BirthdayForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            logout(request)
            messages.success(request, "Account created successfully. Please log in.")
            return redirect('login')
    else:
        form = BirthdayForm(instance=profile)

    return render(request, 'registration/birthday.html', {'form': form})

def register_view(request):
    #Handles user registration
    # If the user is already logged in, redirect them to the home page
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user) 
            
            # --- CHANGED LOGIC ---
            # 1. Log the user in immediately so they can access the birthday page
            login(request, user)
            
            # 2. Redirect to the Birthday page (Step 2)
            return redirect('birthday')
        else:
            pass 
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})


@login_required
def home(request):
    #Home page for logged-in users.
    return render(request, 'home.html')

@login_required
def logout_view(request):
    #Logs out the current user and immediately redirects to the login page.
    logout(request)
    messages.info(request, "You have successfully logged out")

    return redirect('login') # This sends the user directly to the 'login' URL