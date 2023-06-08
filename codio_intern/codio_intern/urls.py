"""
URL configuration for codio_intern project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from users import views as user_views

urlpatterns = [
    path('admin/', admin.site.urls),


    path('register/',user_views.register, name='register'),
    path('profile/',user_views.profile, name='profile'),
    path('login/',user_views.loginPage, name='login'),
    path('logout/',user_views.logoutUser, name='logout'),


    path('password-reset/',  auth_views.PasswordResetView.as_view(template_name='users/password_reset.html'), name='password_reset'),
    path('password-reset/done/',auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>',auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'),name='password_reset_confirm'),
    path('password-reset-complete/',auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),name='password_reset_complete'),
    
    path('activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/',user_views.activate,name='activate'),
    #path('', include('event_registration.urls')),

    path('', user_views.home, name='codio-home'),
    path('about/', user_views.about, name='codio-about'), 

    path('room/<str:pk>/',user_views.room, name="room"),
     path('profile/<str:pk>/', user_views.userProfile, name="user-profile"),


    path('create-room/', user_views.createRoom, name="create-room"),
    path('update-room/<str:pk>/', user_views.updateRoom, name="update-room"),
    path('delete-room/<str:pk>/', user_views.deleteRoom, name="delete-room"),
    path('delete-message/<str:pk>/', user_views.deleteMessage, name="delete-message"),

    path('topics/', user_views.topicsPage, name="topics"),
    path('activity/', user_views.activityPage, name="activity"),

    path('api/update-room-follow/', user_views.update_room_follow, name='update_room_follow'),
    path('download-users/<str:pk>/', user_views.download_users, name='download_users'),
]
