from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from .forms import CustomUserCreationForm, BirthdayForm, ProfileUpdateForm
from .models import Profile, FriendRequest

def index(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        return redirect('login')

def login_view(request):
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
            return render(request, 'registration/login.html', {"error": "Invalid username or password"})
    return render(request, 'registration/login.html')

@login_required
def birthday_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = BirthdayForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            logout(request)
            messages.success(request, "Account created successfully! Please log in.")
            return redirect('login')
    else:
        form = BirthdayForm(instance=profile)
    return render(request, 'registration/birthday.html', {'form': form})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user) 
            login(request, user)
            return redirect('birthday')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def edit_profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        # Removed request.FILES here since we aren't doing images
        form = ProfileUpdateForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('home')
    else:
        form = ProfileUpdateForm(instance=profile)
    return render(request, 'profile/edit_profile.html', {'form': form})

@login_required
def home(request):
    return render(request, 'home.html')

@login_required
def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "You have successfully logged out.")
    return redirect('login')

# --- FRIEND & SOCIAL VIEWS ---

@login_required
def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    
    friend_status = 'none'
    if request.user == profile_user:
        friend_status = 'self'
    else:
        # Check if already friends
        if request.user.profile.friends.filter(user=profile_user).exists():
            friend_status = 'friends'
        # Check if request sent
        elif FriendRequest.objects.filter(from_user=request.user, to_user=profile_user).exists():
            friend_status = 'request_sent'
        # Check if request received
        elif FriendRequest.objects.filter(from_user=profile_user, to_user=request.user).exists():
            friend_status = 'request_received'

    return render(request, 'profile/profile.html', {
        'profile_user': profile_user, 
        'friend_status': friend_status
    })

@login_required
def birthday_twins_view(request):
    my_profile = Profile.objects.get(user=request.user)
    if not my_profile.birthday:
        messages.warning(request, "Please set your birthday first!")
        return redirect('edit_profile')

    twins = Profile.objects.filter(
        birthday__month=my_profile.birthday.month,
        birthday__day=my_profile.birthday.day
    ).exclude(user=request.user)

    return render(request, 'birthday_twins.html', {'twins': twins})

@login_required
def send_friend_request(request, user_id):
    to_user = get_object_or_404(User, id=user_id)
    if request.user != to_user:
        FriendRequest.objects.get_or_create(from_user=request.user, to_user=to_user)
        messages.success(request, f"Friend request sent to {to_user.username}!")
    return redirect('profile', username=to_user.username)

@login_required
def accept_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id)
    if friend_request.to_user == request.user:
        # Add to friends list (both ways)
        request.user.profile.friends.add(friend_request.from_user.profile)
        friend_request.from_user.profile.friends.add(request.user.profile)
        # Delete request
        friend_request.delete()
        messages.success(request, f"You are now friends with {friend_request.from_user.username}!")
    return redirect('notifications')

@login_required
def decline_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id)
    if friend_request.to_user == request.user:
        friend_request.delete()
        messages.info(request, "Friend request declined.")
    return redirect('notifications')

@login_required
def friends_list_view(request, username):
    viewed_user = get_object_or_404(User, username=username)
    friends = viewed_user.profile.friends.all()
    return render(request, 'friends_list.html', {
        'friends': friends,
        'viewed_user': viewed_user
    })

@login_required
def notifications_view(request):
    received_requests = FriendRequest.objects.filter(to_user=request.user)
    return render(request, 'notifications.html', {'received_requests': received_requests})
