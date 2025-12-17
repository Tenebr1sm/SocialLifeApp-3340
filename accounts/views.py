from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from datetime import date
from .forms import CustomUserCreationForm, BirthdayForm, ProfileUpdateForm, PostForm, MessageForm
from .models import Profile, FriendRequest, Post, Message

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
        form = ProfileUpdateForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile', username=request.user.username)
    else:
        form = ProfileUpdateForm(instance=profile)
    return render(request, 'profile/edit_profile.html', {'form': form})

@login_required
def home(request):
    # --- 1. POST HANDLING ---
    if request.method == 'POST':
        post_form = PostForm(request.POST)
        if post_form.is_valid():
            new_post = post_form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            messages.success(request, "Posted to bulletin board!")
            return redirect('home')
    else:
        post_form = PostForm()

    # --- 2. GET SOCIAL FEED ---
    friends = request.user.profile.friends.all()
    friend_user_ids = [f.user.id for f in friends]
    friend_user_ids.append(request.user.id) # Include myself
    posts = Post.objects.filter(author__id__in=friend_user_ids).order_by('-created_at')

    # --- 3. BIRTHDAYS HANDLING ---
    
    # Get user's preferred notification duration (defaults to 30 if not set or 0)
    notification_days = request.user.profile.birthday_notification_days or 30
    
    upcoming_birthdays = []
    all_friends_birthdays = [] # NEW: To store all friends with birthdays
    today = date.today()
    
    for friend in friends:
        if friend.birthday:
            
            # Add to the list of ALL friends with birthdays (for the second box)
            all_friends_birthdays.append(friend) 
            
            # Logic to calculate the next birthday
            try:
                birthday_this_year = friend.birthday.replace(year=today.year)
            except ValueError:
                # Handle leap day gracefully if current year is not a leap year
                birthday_this_year = friend.birthday.replace(year=today.year, month=3, day=1)

            if birthday_this_year < today:
                try:
                    next_birthday = friend.birthday.replace(year=today.year + 1)
                except ValueError:
                    next_birthday = friend.birthday.replace(year=today.year + 1, month=3, day=1)
            else:
                next_birthday = birthday_this_year
            
            days_until = (next_birthday - today).days
            
            # Use the user's preferred notification duration
            if 0 <= days_until <= notification_days:
                upcoming_birthdays.append({
                    'profile': friend,
                    'days_until': days_until,
                    'date': next_birthday
                })
    
    upcoming_birthdays.sort(key=lambda x: x['days_until'])

    return render(request, 'home.html', {
        'upcoming_birthdays': upcoming_birthdays,
        'all_friends_birthdays': all_friends_birthdays, # NEW CONTEXT VARIABLE
        'notification_days': notification_days, # NEW CONTEXT VARIABLE
        'posts': posts,
        'post_form': post_form
    })

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user == post.author:
        post.delete()
        messages.success(request, "Post deleted successfully.")
    else:
        messages.error(request, "You cannot delete someone else's post.")
    return redirect('home')

@login_required
def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "You have successfully logged out.")
    return redirect('login')

@login_required
def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    
    friend_status = 'none'
    is_friend = False

    if request.user == profile_user:
        friend_status = 'self'
        is_friend = True 
    else:
        if request.user.profile.friends.filter(user=profile_user).exists():
            friend_status = 'friends'
            is_friend = True
        elif FriendRequest.objects.filter(from_user=request.user, to_user=profile_user).exists():
            friend_status = 'request_sent'
        elif FriendRequest.objects.filter(from_user=profile_user, to_user=request.user).exists():
            friend_status = 'request_received'

    can_view_details = (request.user == profile_user) or (not profile_user.profile.is_private) or is_friend

    return render(request, 'profile/profile.html', {
        'profile_user': profile_user, 
        'friend_status': friend_status,
        'can_view_details': can_view_details
    })

@login_required
def birthday_twins_view(request):
    my_profile = Profile.objects.get(user=request.user)
    if not my_profile.birthday:
        messages.warning(request, "Please set your birthday first!")
        return redirect('edit_profile')

    twins = Profile.objects.filter(
        birthday__month=my_profile.birthday.month,
        birthday__day=my_profile.birthday.day,
        is_private=False 
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
        request.user.profile.friends.add(friend_request.from_user.profile)
        friend_request.from_user.profile.friends.add(request.user.profile)
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

@login_required
def search_users_view(request):
    query = request.GET.get('q')
    results = []
    
    if query:
        results = User.objects.filter(
            Q(username__icontains=query) | 
            Q(profile__nickname__icontains=query)
        ).distinct().exclude(id=request.user.id)
    
    return render(request, 'search_results.html', {'results': results, 'query': query})

@login_required
def inbox_view(request):
    messages_qs = Message.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).order_by('-timestamp')
    
    conversations = []
    seen_users = set()
    
    for msg in messages_qs:
        other_user = msg.receiver if msg.sender == request.user else msg.sender
        if other_user not in seen_users:
            conversations.append({
                'user': other_user,
                'last_message': msg
            })
            seen_users.add(other_user)
            
    return render(request, 'messages/inbox.html', {'conversations': conversations})

@login_required
def chat_view(request, username):
    other_user = get_object_or_404(User, username=username)
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.sender = request.user
            msg.receiver = other_user
            msg.save()
            return redirect('chat', username=username)
    else:
        form = MessageForm()
    
    messages_qs = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=other_user)) |
        (Q(sender=other_user) & Q(receiver=request.user))
    ).order_by('timestamp')
    
    Message.objects.filter(sender=other_user, receiver=request.user, is_read=False).update(is_read=True)

    return render(request, 'messages/chat.html', {
        'other_user': other_user,
        'messages': messages_qs,
        'form': form
    })