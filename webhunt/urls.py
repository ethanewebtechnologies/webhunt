"""webhunt URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from crackan import views
from django.conf import settings
from django.views.static import serve 

urlpatterns = [
    path('media/<path:path>', serve,{'document_root': settings.MEDIA_ROOT}), 
    path('static/<path:path>', serve,{'document_root': settings.STATIC_ROOT}), 
    path('admin/', admin.site.urls),
    path('account/', include('django.contrib.auth.urls')),
    path('account/signup/', views.signup, name='signup'),
    path('', views.index, name='home'),
    path('hunt', views.hunt, name='hunt'),
    path('ajax/hunt', views.ajax_hunt, name='ajax_hunt'),
    path('upload_contact', views.upload_contact, name='upload_contact'),
    path('hunt_and_send', views.hunt_and_send, name='hunt_and_send'),
    path('upload', views.simple_upload, name='simple_upload'),
    path('demo/download/<path:path>', views.download, name='demo_download'),
    #path('uploads/', include('crackan.urls')),
] 
