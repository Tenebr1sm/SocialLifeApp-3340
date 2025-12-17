from django.urls import path
from . import views

urlpatterns = [
    # --- Landing & Dashboard ---
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),

    # --- Authentication ---
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # --- Registration Flow ---
    path('register/', views.register_view, name='register'),
    path('birthday/', views.birthday_view, name='birthday'),

    # --- Social Profile System ---
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    
    # --- Birthday Twins ---
    path('twins/', views.birthday_twins_view, name='birthday_twins'),

    # --- Friend System ---
    path('profile/<str:username>/friends/', views.friends_list_view, name='friends_list'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('friend-request/send/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('friend-request/accept/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('friend-request/decline/<int:request_id>/', views.decline_friend_request, name='decline_friend_request'),

    # --- Search ---
    path('search/', views.search_users_view, name='search_users'),

    # --- Messaging ---
    path('inbox/', views.inbox_view, name='inbox'),
    path('chat/<str:username>/', views.chat_view, name='chat'),

    # --- Posts ---
    path('post/delete/<int:post_id>/', views.delete_post, name='delete_post'),

    # Public Profile (Must be at the bottom)
    path('profile/<str:username>/', views.profile_view, name='profile'),
]