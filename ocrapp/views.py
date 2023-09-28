from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, EmailMessage, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from ESRGAN import test
# Create your views here.
from django.urls import reverse

import csv
from django.http import HttpResponse

from django.contrib.auth import views

from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text

from .forms import SubscribersForm, ContactForm, ImageUForm, ImageGANForm
from .owner import OwnerUpdateView
from .tokens import generate_token

from OCRdJANGO_BETA_PROJECT import settings

#from ESRGAN import test

from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.contrib.auth.tokens import default_token_generator

#from django.http import StreamHttpResponse
#from WSGIREF.UTIL import FileWrapper
#import mimtypes

def home(request):
    if request.method == "POST":
        imgform = ImageUForm(request.POST, request.FILES or None)
        form = SubscribersForm(request.POST)

        if imgform.is_valid():
            img_obj = imgform.instance
            imgform.save()

            return render(request, 'home.html', {'form': imgform, 'img_obj': img_obj})
        elif form.is_valid():
            form.save()
            messages.success(request, 'You are subscribed!')
            return redirect('/')
        else:
            messages.success(request, 'Email address already exists!')
            return redirect('/')

    else:
        imgform = ImageUForm()

    return render(request, 'home.html', {'form': imgform})


def signup(request):
    if request.method == "POST":

        imgform = ImageUForm(request.POST, request.FILES or None)

        if imgform.is_valid():
            img_obj = imgform.instance
            imgform.save()

            return render(request, 'authentication/index_signup.html', {'form': imgform, 'img_obj': img_obj})

        # username = request.POST.get('username')
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['password1']
        pass2 = request.POST['password2']

        if User.objects.filter(username=username):
            messages.error(request, "Username already exist! Please try again with different username.")
            return redirect('signin')

        if User.objects.filter(email=email).exists():
            messages.error(request, "EmailID already registered!!")
            return redirect('signin')

        if len(username) > 20:
            messages.error(request, "Username must be under 20  characters!!")
            return redirect('signup')

        if pass1 != pass2:
            messages.error(request, "Passwords didn't matched!!")
            return redirect('signup')

        if not username.isalnum():
            messages.error(request, "Username must be Alpha-Numeric!!")
            return redirect('signup')

        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.is_active = False
        myuser.save()
        if myuser:
            messages.success(request,
                             "Your Account has been created successfully!! "
                             "Please check your email to confirm your email address in order to activate your account.")

        # Welcome Email

        subject = "Welcome to AevolveAI!!"
        message = "Hello " + myuser.first_name + "!! \n" + "Welcome to AevolveAI!! \nThank you for visiting our " \
                                                           "website\n. " \
                                                           "We have sent you a confirmation email, " \
                                                           "please confirm your email address. \n\nThanking " \
                                                           "You\nAevolveAI "
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)

        # Email Address Confirmation Email

        current_site = get_current_site(request)
        email_subject = "Confirm your Email @ AevolveAI - ocularai Login!!"
        message2 = render_to_string('email_confirmation.html', {

            'name': myuser.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser)
        })
        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email],
        )
        email.fail_silently = True
        email.send()

        return redirect('signin')

    else:

        imgform = ImageUForm()

    return render(request, 'authentication/index_signup.html', {'form': imgform})


def signin(request):
    if request.method == 'POST':

        imgform = ImageUForm(request.POST, request.FILES or None)

        if imgform.is_valid():
            img_obj = imgform.instance
            imgform.save()

            return render(request, 'authentication/index_signin.html', {'form': imgform, 'img_obj': img_obj})

        email = request.POST['email']
        pass1 = request.POST['password']
        username = ''
        valids = ''
        try:
            username = User.objects.get(email=email).username
            valids = User.objects.get(email=email).is_active
        except User.DoesNotExist:
            messages.error(request, "Bad credentials!!")
            return redirect('signin')
        user = authenticate(request, username=username, password=pass1)

        if user is not None and user.is_active:
            login(request, user)
            fname = user.first_name

            # return render(request, "ocr_page.html", {"name": fname})
            return HttpResponseRedirect(reverse('welcome'))
        elif user is not None and str(valids) == 'False':

            messages.error(request, "Your account is in inactive state, please activate your account!!")
            return redirect('signin')
        elif user is None and str(valids) == 'False':

            messages.error(request, "Your account is in inactive state, please activate your account!!")
            return redirect('signin')
        else:
            messages.error(request, "Bad credentials!!")
            return redirect('signin')

    else:
        imgform = ImageUForm()

    return render(request, 'authentication/index_signin.html', {'form': imgform})


def signout(request):
    logout(request)
    messages.success(request, "Logged Out Successfully!!")
    return redirect('signin')


@login_required
def special(request):
    return HttpResponse("You are logged in !")


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)

    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None

    context = {'uidb64': uidb64, 'token': token}

    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        login(request, myuser)

        # return redirect('home')
        messages.success(request, "Your account is activated!!")
        return render(request, 'authentication/index_signin.html', context)
    else:
        messages.success(request, "Activation failed, please try again!")
        return render(request, 'authentication/index_signup.html')


def contact_record(request):
    if request.method == "POST" and request.POST.get('name') is None:

        form = SubscribersForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'You are subscribed!')
            return redirect('/')
        else:
            messages.success(request, 'Email address already exists!')
            return redirect('/')

    elif request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        subject = request.POST['subject']
        message = request.POST['message']
        form = ContactForm(request.POST)

        if form.is_valid():
            form.save()

            # Send email

            send_mail(
                subject,  # Subject
                message,  # Message
                email,  # From Email
                [settings.EMAIL_HOST_USER],  # To Email
                fail_silently=True
            )

            return render(request, 'home.html', {'name': name})
        else:
            return redirect('/')

    else:
        form1 = SubscribersForm()
        form2 = ContactForm

        context = {'form': form1, 'form1': form2}

        return render(request, 'home.html', context)


def base(request):
    return redirect('/')


def free_upload(request):
    if request.method == 'POST':

        imgform = ImageUForm(request.POST, request.FILES or None)

        if imgform.is_valid():
            img_obj = imgform.instance
            imgform.save()

            return render(request, 'ocr_page.html', {'form': imgform, 'img_obj': img_obj})
        else:
            return HttpResponse("not valid")

    else:
        form = ImageUForm()

    return render(request, 'ocr_page.html', {'form': form})


def user_upload(request, pk=None):
    if request.method == 'POST':
        user = get_object_or_404(User, id=pk, user=request.user)
        if User.objects.is_active and user:
            imgform = ImageUForm(request.POST, request.FILES or None)

        if imgform.is_valid():
            img_obj = imgform.instance
            imgform.save()

            return render(request, 'ocr_page.html', {'form': imgform, 'img_obj': img_obj})

        else:
            return HttpResponse("not valid")

    else:
        imgform = ImageUForm()

    return render(request, 'ocr_page.html', {'form': imgform})


def welcome(request):
    return render(request, 'ocr_page.html')


def forgot_password(request):
    if request.method == 'POST':
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            current_site = get_current_site(request)
            if associated_users.exists():
                for user in associated_users:

                    subject = "Password Reset Requested"
                    email_template_name = "authentication/password_reset_email.txt"
                    c = {
                        "email": user.email,
                        "domain": current_site.domain,
                        "site_name": "AevolveAI",
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "token": default_token_generator.make_token(user),

                    }
                    '''
                    message2 = render_to_string('email_confirmation.html', {

                        'email': user.email,
                        'domain': current_site.domain,
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'token': generate_token.make_token(user)
                    })'''
                    email_message = render_to_string(email_template_name, c)
                    try:
                        send_mail(subject, email_message, settings.EMAIL_HOST_USER, [user.email], fail_silently=True)
                    except BadHeaderError:

                        return HttpResponse('Invalid header found.')

                    messages.success(request, 'A message with reset password instructions has been sent to your inbox.')

                    return redirect("signin")
            messages.error(request, 'An invalid email has been entered.')
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="authentication/password_reset.html",
                  context={"password_reset_form": password_reset_form})


def reset_password(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    context = {'uidb64': uidb64, 'token': token}

    if user is not None and request.method == 'POST':
        # Password reset
        password = request.POST['password']
        User.objects.filter(username=str(user)).update(password=password)
        # return redirect('home')
        messages.success(request, 'Your password has been reset!!')
        return render(request, 'authentication/signin.html', context)
    else:
        return render(request, 'authentication/password_reset_confirm.html')


def update_password(request):
    if request.method == 'POST':
        # Password reset
        password = request.POST['password']
        user = request.POST['username']
        # User.objects.filter(username = user).update(password=password)
        # return redirect('home')
        u = User.objects.get(username=user)
        u.set_password(password)
        u.save()
        messages.success(request, 'Your password has been reset!!')
        return render(request, 'authentication/index_signin.html', {'user': user})
    else:
        messages.error(request, 'Password reset failed, please retry')
        return render(request, 'authentication/index_signin.html')


def user_reset_password_refresh(request):
    return render(request, 'user_reset_password.html')


class UpdateUserPassword(OwnerUpdateView):
    template_name = 'user_reset_password.html'

    def get(self, request, pk=None):

        # return render(request, self.template_name)
        return HttpResponseRedirect(reverse('user_reset_password_refresh'))

    def post(self, request, pk=None):

        password1 = request.POST['password1']
        password2 = request.POST['password2']
        user = request.POST['username']

        if password1 != password2:
            messages.error(request, "Password did not match, try again!!")
            return render(request, self.template_name)

        u = User.objects.get(username=user)

        if str(u.username) == str(self.request.user):
            u.set_password(password1)
            u.save()
            messages.success(request, 'Your password has been reset, please re-login!!')
            # return render(request, 'ocr_page.html')
            return HttpResponseRedirect(reverse('signin_1'))

        else:
            messages.error(request, "Invalid user, please provide correct username!!")
            return render(request, self.template_name)


def signin_1(request):
    return render(request, 'ocr_page.html')


def ocr_homepage(request):
    return render(request, 'ocr_homepage.html')


# def srgan_homepage(request):
#    return render(request, 'ESRGAN_homepage.html')


def esrgan_master1(request, pk=None):
    #test.call_srgan()
    if request.method == 'POST':
        # return render(request, 'ESRGAN_homepage.html')
        print("1firts")
        user = get_object_or_404(User, id=pk, user=request.user)
        if User.objects.is_active and user:
            imgform = Image_gan(request.POST, request.FILES or None)
        print("2firts")

        if imgform.is_valid():
            img_obj = imgform.instance
            imgform.save()

            # return render(request, 'ESRGAN_homepage.html', {'form': imgform, 'img_obj': img_obj})
            return HttpResponse("success")
        print("3firts")
    print("4firts")
    # return render(request, 'ESRGAN_homepage.html')
    # return HttpResponse("Here's the text of the web page.")
    return render(request, 'ESRGAN_homepage.html')

def get_username():
    username = None
    if request.user.get_username():
        username = request.user.username

def writeafile(username):
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="filename.txt"'

    response.write(username)

    return response

def esrgan_master(request):
    if request.method == 'POST':

        username = None
        if request.user.get_username():
            username = request.user.username
            file1 = open('myfile.txt', 'w')
            file1.write(username)
            #file1 = open('myfile.txt', 'r')
            #print("filedetails: ", file1.read())
            file1.close()


        imgform = ImageGANForm(request.POST, request.FILES or None)

        if imgform.is_valid():
            #if request.user.get_username():
                #username = request.user.username
                #writeafile(username)
                #print('user1:', username)
            img_obj = imgform.instance
            imgform.save()
            #print("DONE!!!")
            username = None
            if request.user.get_username():
                username = request.user.username
            print("Image Name : ",img_obj.image)
            from PIL import Image
            imgpath = imgform
            #img = Image.open(imgpath)
            print("Imagename :", imgform['image'].value())
            test.call_srgan(username,imgform['image'].value())

            print("DONE!!!")
            return render(request, 'ESRGAN_homepage_final.html', {'form': imgform, 'img_obj': img_obj})
            # return HttpResponse("valid")
        else:
            return HttpResponse("not valid")

    else:
        form = ImageUForm()

    return render(request, 'ESRGAN_homepage.html', {'form': form})
    # return HttpResponse("get method")


def uploadimage(request):
    if request.method == 'POST' and request.FILES['avatar']:
        img = request.FILES['avatar']
        fs = FileSystemStorage()

        #To copy image to the base folder
        #filename = fs.save(img.name, img)

        #To save in a specified folder
        filename = fs.save('C://Users//Asus//Downloads//DjangoProject_AevolveAI_Beta//ESRGAN//LR//'+img.name, img)
        uploaded_file_url = fs.url(filename)                 #To get the file`s url
        return render(request, 'myapp/upload.html', {'uploaded_file_url': uploaded_file_url})
    else:
        return render(request, 'myapp/upload.html')


# Import mimetypes module
import mimetypes
# import os module
import os
# Import HttpResponse module
from django.http.response import HttpResponse
# Import render module
from django.shortcuts import render

# Define function to download pdf file using template
def download_file(request):
    if request.user.get_username():
        username = request.user.username


        # Define Django project base directory
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = 'C:/Users/Asus/Downloads/DjangoProject_AevolveAI_Beta/ESRGAN/results/'+username+'/'
        files = os.listdir(path)
        paths = [os.path.join(path, basename) for basename in files]


        # Define the full file path
        filepath = max(paths, key=os.path.getmtime)
        # Open the file for reading content
        path = open(filepath, 'rb')
        # Set the mime type
        mime_type, _ = mimetypes.guess_type(filepath)
        # Set the return value of the HttpResponse
        response = HttpResponse(path, content_type=mime_type)
        # Set the HTTP header for sending to browser
        response['Content-Disposition'] = "attachment; filepath=%s" % filepath
        # Return the response value
        return response
    else:
        # Load the template
        return render(request, 'ESRGAN_homepage_final.html')

'''

def signup(request):
    if request.method == 'POST':
       forms = SignUpForm(request.POST)
       if forms.is_valid():
       
           forms.save()
           username = forms.cleaned_data.get('username')
           raw_password = forms.cleaned_data.get('password1')
           user = authenticate(username=username, password=raw_password)
           login(request, user)
           return redirect('home')
        else:
            forms = SignUpForm()
        return render(request, 'authentication/index_signup.html', {'form': forms})




def register(request):
    registered = False
    if request.method == 'POST':

        imgform = ImageUForm(request.POST, request.FILES or None)
        form = Register(request.POST)
        signup = Signup()

        if imgform.is_valid():
            img_obj = imgform.instance
            imgform.save()

            return render(request, 'home.html', {'form': imgform, 'img_obj': img_obj})

        name = request.POST['name']
        email = request.POST['email']
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if username in signup.username:
            messages.error(request, "Username already exists")
            return HttpResponse('Username already exists')

        if len(username) > 10:
            messages.error(request, "Username must be under 10 characters")
            return HttpResponse('Username must be under 10 characters')

        if password1 != password2:
            messages.error(request, "Password did not match")
            return HttpResponse('Password did not match')

        if not username.isalnum():
            messages.error(request, "username must be alpha-numeric")
            return HttpResponse('username must be alpha-numeric')

        elif form.is_valid():

            registered = True
            #signup.is_valid = True
            form_obj = form.instance
            form.save()

            messages.success(request,
                             "Your account has been successfully created. We have sent you a confirmation email, "
                             "please verify your email inorder to activate your account")

            # Welcome email

            subject = "Welcome to ocular.ai OCR based application"
            message = "Hello " + name + "!! \n" + "Welcome to ocular.ai OCR based application!! \n Thank you " \
                                                  "for visiting our website \n We have sent you a " \
                                                  "confirmation email, please confirm your email address in " \
                                                  "order to activate your account. \n\n Thanking You\n Ocular " \
                                                  "Team "
            from_email = settings.EMAIL_HOST_USER
            to_list = [email]
            send_mail(subject, message, from_email, to_list, fail_silently=True)

            # Email Address confirmation

            current_site = get_current_site(request)
            email_subject = "Confirm your email -- Ocularai.co.in"
            message2 = render_to_string('email_confirmation.html', {
                'name': name,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(1)),
                # 'uid': "MTg",
                'token': generate_token.make_token(form)})
            email = EmailMessage(
                email_subject,
                message2,
                settings.EMAIL_HOST_USER,
                [email], )
            email.fail_silently = True
            email.send()

            return redirect("home")

        else:
            print(form.errors)

    else:
        imgform = ImageUForm()

    return render(request, 'authentication/index_signup.html', {'form': imgform, 'registered': registered})

'''

'''
def signin(request):
    if request.method == 'POST':

        imgform = ImageUForm(request.POST, request.FILES or None)

        if imgform.is_valid():
            img_obj = imgform.instance
            imgform.save()

            return render(request, 'authentication/index_signin.html', {'form': imgform, 'img_obj': img_obj})

        username = request.POST['username']
        pass1 = request.POST['pass1']

        user = authenticate(username=username, password=pass1)

        if user is not None:
            login(request, user)
            fname = user.first_name
            return render(request, "authentication/index.html", {'fname': fname})
        else:
            messages.error(request, "Please enter correct credentials")
            return redirect('home')

    else:
        imgform = ImageUForm()

    return render(request, 'authentication/index_signin.html', {'form': imgform})

'''
