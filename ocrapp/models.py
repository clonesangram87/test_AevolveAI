from django.contrib.auth.models import User
from django.db import models
from django.core.exceptions import ValidationError


# Create your models here.
from django.db.models.signals import post_save
from django.dispatch import receiver


class Subscribers(models.Model):
    # email = models.EmailField(null=True)
    email = models.EmailField(null=True, unique=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class Contacts(models.Model):
    name = models.CharField(max_length=200, null=True)

    email = models.EmailField(null=True)

    subject = models.CharField(max_length=200)

    message = models.CharField(max_length=400)

    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Image(models.Model):
    title = models.CharField(max_length=100, blank=False)
    image = models.ImageField(upload_to='ocrimages/', blank=False, null=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Image_gan(models.Model):
    title = models.CharField(max_length=100, blank=False)
    file1 = open('myfile.txt', 'r')
    # print("filedetails: ", file1.read())
    #print(self.request.user.id)
    usrname=file1.read()
    image = models.ImageField(upload_to='ESRGAN/LR/'+usrname+'/', blank=False, null=False)

    def __str__(self):
        return self.title


class Signin(models.Model):

    username = models.OneToOneField(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


class Signup(models.Model):
    name = models.CharField(max_length=100,null=False)
    email = models.EmailField(max_length=100,null=False, unique=True)
    username = models.CharField(max_length=100)
    password1 = models.CharField(max_length=100)
    password2 = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)
    is_valid = models.BooleanField(default=False,auto_created=True)

    def __str__(self):
        return self.username
