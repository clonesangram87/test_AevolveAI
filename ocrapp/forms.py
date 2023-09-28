from django import forms
from django.contrib.auth.models import User

from .models import Subscribers, Contacts, Image, Signin, Signup, Image_gan

from django.contrib.auth.forms import UserCreationForm, UserChangeForm


class SubscribersForm(forms.ModelForm):
    class Meta:
        model = Subscribers
        fields = ['email', ]

    def clean_email(self):
        data = self.cleaned_data['email']
        if User.objects.filter(email=data).count() > 0:
            raise forms.ValidationError("Email ID already exists")

        return data


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contacts
        fields = ['name', 'email', 'subject', 'message', ]


class ImageUForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['title', 'image', ]

class ImageGANForm(forms.ModelForm):
    class Meta:
        model = Image_gan
        fields = ['title', 'image', ]


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password')

'''

class Register(forms.ModelForm):

    class Meta:
        model = Signup
        fields = ["name", "email", "username", "password1", "password2", ]

'''
