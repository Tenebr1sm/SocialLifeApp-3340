from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),   # root → redirect logic
    path('home/', views.home, name='home'),
]
