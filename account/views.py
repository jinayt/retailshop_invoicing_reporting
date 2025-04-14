from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib import auth
from django.contrib.auth.models import User
from account.models import Profile
from django.contrib.auth.decorators import login_required
from .decorator import unauthenticated_user

# Create your views here.

@unauthenticated_user
def user_login(request):
    context = {'page':'login'}
    if request.method == "POST":
        user = auth.authenticate(username = request.POST['username'], password = request.POST['password'])
        if user is not None:
            auth.login(request,user)
            if user.groups.filter(name="Customer").exists():
                return redirect('customerdashboard')
            else:
                return redirect('admindashboard')
        else:
            return render(request,'login.html',{'error':"Invalid login credentials."})
    else:
        return render(request,'login.html',context)
    

def signup(request):
    context = {'page':'signup'}
    if request.method == "POST":
        if request.POST['password'] == request.POST['cn_password']:
            try:
                user = User.objects.get(username=request.POST['username'])
                return render(request,"signup.html",{'error':"Username has already been Taken"})
            except User.DoesNotExist:
                mobile = request.POST.get('mobile')
                first_name = request.POST.get('firstname')
                last_name = request.POST.get('lastname')
                email = request.POST.get('email')
                user = User.objects.create_user(username = request.POST['username'],password = request.POST['password'],email = email, first_name = first_name , last_name=last_name)
                Profile.objects.create(mobile_no = mobile, user = user)
                auth.login(request,user)
                return redirect('customerdashboard')
    else:
        return render(request,'signup.html',context)    

@login_required(login_url = '/login/')
def showdata(request):
    datas = Profile.objects.filter(user = request.user)
    return render(request,"register.html",{'data':datas})


def logout(request):
    auth.logout(request)
    context = {'page':'Home'}
    return redirect('/')