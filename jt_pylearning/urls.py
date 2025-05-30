"""
URL configuration for jt_pylearning project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path, include

#for image upload
from django.conf.urls.static import static
from django.conf import settings

from home.views import * 
from account.views import *
from order.views import *



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home , name='home'),
    path('', include('home.urls')),
    path('', include('order.urls')),
    path('about/', about , name="about"),
    path('contact/',contact,name="contact"),
    path('login/',user_login,name="login"),
    path('signup/',signup,name="signup"),
    path('show/',showdata,name="showdata"),
    path('logout/',logout,name='logout'),
    
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
