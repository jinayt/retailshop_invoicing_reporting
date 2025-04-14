from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import auth
from django.contrib.auth.models import User
from account.models import Profile
from django.contrib.auth.decorators import login_required

def home(request):
    context = {'page':'Home'}
    return render(request, "index.html", context)


def about(request):
    context = {'page':'About'}
    return render(request,"about.html",context)
  
def contact(request):
    context = {'page':'contact'}
    return render(request,"contact.html",context)

@login_required(login_url = '/login/')
def admin_dashboard(request):
    return render(request,'admindashboard.html',{'page':'Dashboard'})

@login_required(login_url = '/login/')
def customer_dashboard(request):
    return render(request,'customerdashboard.html',{'page':'Dashboard'})

