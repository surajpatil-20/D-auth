from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth.decorators import login_required

# For email verification
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.core.mail import send_mail
from .models import CustomUserCreationForm
from .tokens import token_generator


# Create your views here.

# def login_view(request):
#     if request.method == 'POST':
#         form = AuthenticationForm(request,data = request.POST)
#         if form.is_valid():
#             user = form.get_user()
#             login(request, user)
#             return redirect("home")
#     else:
#         form = AuthenticationForm()
#     return render(request, 'login.html',{'form':form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        username_or_email = request.POST.get("username")
        password = request.POST.get("password")
        try:
            if '@' in username_or_email :
                user_obj = User.objects.filter(email=username_or_email).first()
                username = user_obj.username if user_obj else username_or_email
            else:
                username= username_or_email
        except User.DoesNotExist:
            username = username_or_email

        user = authenticate(username=username,password=password)
        if user:
            login(request,user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request,'login.html', {'form':form})




def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate account till it is confirmed
            user.save()

            # generate token
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token  = token_generator.make_token(user)

            #build activation link
            current_site = get_current_site(request)
            verification_link = f"http://{current_site.domain}/activate/{uid}/{token}/"

            # send email
            send_mail(
                subject="Activate your accout",
                message=f"Hi {user.username}, \n\n Please click the link below to verify your account:\n{verification_link}\n\nThank you!",
                from_email="surajabpatil2002@gmail.com",
                recipient_list=[user.email],
            )
            messages.success(request, "Account created successfully! Please check your email to verify your account.")

            return redirect("login")
    else :
        form = CustomUserCreationForm()
    return render(request, "signup.html", {"form":form})

# Activation view
def activate_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Your account has been activated! You can log in now.")
        return redirect("login")
    else:
        messages.error(request, "Activation link is invalid or has expired.")
        return redirect("signup")
    
    

@login_required(login_url='login')
def home_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request,'home.html',{'user': request.user})


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')
    else:
        return redirect('home')

