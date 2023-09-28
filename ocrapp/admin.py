from django.contrib import admin

# Register your models here.

from .  models import  Subscribers, Contacts, Image, Signin, Signup

admin.site.register(Subscribers)

admin.site.register(Contacts)

admin.site.register(Image)

admin.site.register(Signin)

admin.site.register(Signup)

