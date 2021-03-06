from .models import Message
from django.contrib.auth.models import User
from rest_framework import viewsets, permissions
from .serializers import MessageSerializer, UserSerializer
from django.views.generic import View, UpdateView
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import SignupForm, CreateNewMessageForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core.mail import EmailMessage


class MessageView(viewsets.ModelViewSet):
	queryset = Message.objects.all()
	serializer_class = MessageSerializer
    # guests can read messages
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

class UserView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # guests cannot read user data
    permission_classes = (permissions.IsAuthenticated,)

def wall(request):
	messages_list = Message.objects.order_by('-pub_date')
	context = {'messages_list': messages_list}
	return render(request, 'wall.html', context)


def new_msg(request):
    if request.method == 'POST' and request.user.is_authenticated:
        form = CreateNewMessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.author = request.user
            msg.save()
            return redirect('wall')
    elif request.method == 'GET' and request.user.is_authenticated:
            form = CreateNewMessageForm()
    else:
        return HttpResponse('Your not signed in')
    return render(request, 'new_msg.html', {'form': form})


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Activate your account.'
            message = render_to_string('acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                        mail_subject, message, to=[to_email]
            )
            email.send()
            return HttpResponse('Please confirm your email address to complete the registration')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('wall')
        # return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!')
