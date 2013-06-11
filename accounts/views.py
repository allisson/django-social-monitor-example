# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import Http404
from django.core import signing
from django.conf import settings
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User

from twython import Twython

from accounts.models import SocialAccount
from accounts.forms import (
    RegisterConfirmEmailForm, 
    RegisterForm, 
    ForgotPasswordForm, 
    ForgotPasswordConfirmForm, 
    LoginForm,
)


def register_confirm_email(request):
    if request.method == 'POST':
        form = RegisterConfirmEmailForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, u'Verifique o link que foi enviado para o seu e-mail.')
            return redirect('accounts_register_confirm_email')
    else:
        form = RegisterConfirmEmailForm()
    return render(request, 'accounts/register_confirm_email.html', {'form': form})


def register(request, token):
    # check token
    try:
        token_object = signing.loads(token, max_age=settings.REGISTER_MAX_AGE)
        email = token_object['email']
        register = token_object['register']
    except:
        messages.error(request, u'Link de ativação inválido.')
        return redirect('accounts_register_confirm_email')

    # check for registered user
    if User.objects.filter(email=email):
        messages.error(request, u'E-mail já cadastrado.')
        return redirect('accounts_register_confirm_email')

    # process form
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # get new user
            new_user = form.save(email=email)

            # login new user
            auth_login(request, new_user)

            # make message
            messages.success(request, u'Conta criada com sucesso.')

            # redirect to index
            return redirect('staticpages_index')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login(request):
    # get next parameter
    next = request.REQUEST.get('next', settings.LOGIN_REDIRECT_URL)

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect(next)
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form, 'next': next})


def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,
                u'Verifique o link que foi enviado para o seu e-mail.'
            )
            return redirect('accounts_forgot_password')
    else:
        form = ForgotPasswordForm()
    return render(request, 'accounts/forgot_password.html', {'form': form})


def forgot_password_confirm(request, token):
    # check token
    try:
        token_object = signing.loads(token, max_age=settings.FORGOT_PASSWORD_MAX_AGE)
        email = token_object['email']
        forgot_password = token_object['forgot-password']
    except:
        messages.error(request, u'Link inválido.')
        return redirect('accounts_forgot_password')

    # check for registered user
    try:
        user = User.objects.get(email=email)
    except:
        messages.error(request, u'E-mail não cadastrado.')
        return redirect('accounts_forgot_password')

    # process form
    if request.method == 'POST':
        form = ForgotPasswordConfirmForm(request.POST, user=user)
        if form.is_valid():
            form.save()
            messages.success(request, u'Senha alterada com sucesso.')
            return redirect('accounts_login')
    else:
        form = ForgotPasswordConfirmForm(user=user)
    return render(request, 'accounts/forgot_password_confirm.html', {'form': form})


@login_required
def social_account_list(request):
    account_list = request.user.social_accounts.all()
    return render(request, 'accounts/social_account_list.html', 
        {'account_list': account_list}
    )


@login_required
def social_account_delete(request, pk):
    account = get_object_or_404(SocialAccount, user=request.user, pk=pk)
    if request.method == 'POST':
        account.delete()
        messages.success(request, u'Conta excluída com sucesso.')
        return redirect('accounts_social_account_list') 
    return render(request, 'accounts/social_account_delete.html', 
        {'account': account}
    )


@login_required
def connect_twitter(request):
    t = Twython(settings.TWITTER_APP_KEY, settings.TWITTER_APP_SECRET)
    auth_props = t.get_authentication_tokens(callback_url=settings.TWITTER_CALLBACK_URL)
    request.session['oauth_token'] = auth_props['oauth_token']
    request.session['oauth_token_secret'] = auth_props['oauth_token_secret']
    return redirect(auth_props['auth_url'])


@login_required
def connect_twitter_callback(request):
    oauth_token_secret = request.session.get('oauth_token_secret', False)
    if not oauth_token_secret:
        return redirect('accounts_connect_twitter')

    oauth_token = request.GET.get('oauth_token', False)
    oauth_verifier = request.GET.get('oauth_verifier', False)
    if not oauth_token or not oauth_verifier:
        return redirect('accounts_connect_twitter')

    t = Twython(settings.TWITTER_APP_KEY, settings.TWITTER_APP_SECRET, 
        oauth_token, oauth_token_secret)
    auth_tokens = t.get_authorized_tokens(oauth_verifier)

    social_account = SocialAccount.objects.get_or_create(
        user=request.user,
        site='twitter',
        access_token=auth_tokens['oauth_token'],
        access_token_secret=auth_tokens['oauth_token_secret'],
        account_user_id=auth_tokens['user_id'],
        account_screen_name=auth_tokens['screen_name']
    )
    messages.success(request, u'Conta do twitter adicionada com sucesso.')
    return redirect('accounts_social_account_list')
