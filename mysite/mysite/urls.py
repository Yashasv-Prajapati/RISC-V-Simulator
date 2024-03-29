"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import include, path

from polls.views import index, load_next, load_prev, load_reset, load_run
from phase3.views import index, load_next3, load_prev3, load_reset3, load_run3

urlpatterns = [
    path("phase3/", include("phase3.urls")),
    path("polls/", include("polls.urls")),
    path("admin/", admin.site.urls),
    path('load_prev3/',load_prev3, name='load_prev3'),
    path('load_next3/',load_next3, name='load_next3'),
    path('load_run3/',load_run3, name='load_run3'),
    path('load_reset3/',load_reset3, name='load_reset3'),
    path('load_prev/',load_prev, name='load_prev'),
    path('load_next/',load_next, name='load_next'),
    path('load_run/',load_run, name='load_run'),
    path('load_reset/',load_reset, name='load_reset'),
]