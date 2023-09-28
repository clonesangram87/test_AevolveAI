"""OCRdJANGO_BETA_PROJECT URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.template.defaulttags import url
from django.urls import path, include
from . import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
                  path('', views.home, name="home"),
                  path('base', views.base, name='base'),
                  path('signup', views.signup, name='signup'),
                  path('signin', views.signin, name='signin'),
                  path('signout', views.signout, name='signout'),
                  path('contact', views.contact_record, name='contact'),
                  path('freeload', views.free_upload, name='freeload'),
                  path('userload', views.user_upload, name='userload'),
                  path('testpage', views.free_upload, name='testpage'),
                  # path('signup_test', views.register, name='signup_test'),
                  path('activate/<uidb64>/<token>/', views.activate, name='activate'),
                  path('welcome', views.welcome, name='welcome'),
                  path('forgot_password', views.forgot_password, name='forgot_password'),
                  path('reset_password/<uidb64>/<token>/', views.reset_password, name='reset_password'),
                  path('update_password', views.update_password, name='update_password'),
                  path('user_reset_password', views.UpdateUserPassword.as_view(), name='user_reset_password'),
                  path('signin_1', views.signin_1, name='signin_1'),
                  path('user_reset_password_refresh', views.user_reset_password_refresh,
                       name='user_reset_password_refresh'),
                  path('ocr_homepage', views.ocr_homepage, name='ocr_homepage'),
                  # path('image_resolution', views.srgan_homepage, name='image_resolution'),
                  path('upload_res_image', views.esrgan_master, name='upload_res_image'),
                  path('downloadfile', views.download_file, name='downloadfile'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.MEDIA_GAN_URL, document_root=settings.MEDIA_GAN_ROOT)
