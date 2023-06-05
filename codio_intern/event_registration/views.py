from django.shortcuts import render
from django.http import HttpResponse


def home(request):
    return render(request, 'event_registration/home.html')

def about(request):
    return render(request,'event_registration/about.html')



# Create your views here.
