# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# Create your views here.

from django.shortcuts import render, redirect
from forms import SignUpForm, LoginForm
from models import UserModel, SessionToken
from django.contrib.auth.hashers import make_password, check_password

import sendgrid

from sendgrid.helpers.mail import *


# Create your views here.
your_clientId="31bd2c0d7d5a46d"
your_clientSecret="bd8022508c9d2924f77a230a120e3c8f6d919344"
sendgrid_key="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"
api_key="b6cb8952189e4e608c72c82668c129b3"

def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            if (len(form.cleaned_data['username'])<5):
                return render(request, 'invalid.html')
            username = form.cleaned_data['username']
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            # saving data to DB
            user = UserModel(name=name, password=make_password(password), email=email, username=username)
            user.save()
            sg = sendgrid.SendGridAPIClient(apikey=(sendgrid_key))
            from_email = Email("muskaanlaroia@gmail.com")
            to_email = Email(form.cleaned_data['email'])
            subject = "Welcome to Swacch Bharat Abhiyaan"
            content = Content("text/plain", "You maay post the pictures of your surroundings and let us categorise them for u to help keep your country clean")
            mail = Mail(from_email, subject, to_email, content)
            response = sg.client.mail.send.post(request_body=mail.get())
            print(response.status_code)
            print(response.body)
            print(response.headers)
            return render(request, 'success.html')
            # return redirect('login/')
    else:
        form = SignUpForm()

    return render(request, 'index.html', {'form': form})


def login_view(request):
    response_data = {}
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = UserModel.objects.filter(username=username).first()

            if user:
                if check_password(password, user.password):
                    token = SessionToken(user=user)
                    token.create_token()
                    token.save()
                    response = redirect('feed/')
                    response.set_cookie(key='session_token', value=token.session_token)
                    return response
                else:
                    response_data['message'] = 'Incorrect Password! Please try again!'

    elif request.method == 'GET':
        form = LoginForm()

    response_data['form'] = form
    return render(request, 'login.html', response_data)



