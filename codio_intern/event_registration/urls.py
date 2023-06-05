from django.urls import path,include
from . import views

urlpatterns = [
    path('', views.home, name='codio-home'),
    path('about/', views.about, name='codio-about'), 
]
