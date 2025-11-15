from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages #required for showing message
from django.contrib.auth.forms import UserCreationForm

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
            return redirect('home')
        else:
            return render(
                request,
                'registration/login.html',
                {"error": "Invalid username or password"}
            )

    return render(request, 'registration/login.html')

def register_view(request):
    #Handles user registration
    # If the user is already logged in, redirect them to the home page
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        # Process the submitted form data
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the new user to the database
            login(request, user) # Log the user in immediately
            messages.success(request, "Registration successful. You can now log in.")
            return redirect('login') # Redirect to the home page
        else:
            # Form was invalid, pass it back to the template
            # The form object will now contain error messages
            pass 
    else:
        # If it's a GET request, create a blank form
        form = UserCreationForm()

    # Render the registration template
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