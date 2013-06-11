# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import EmailMessage
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.core import signing
from django.contrib.auth import authenticate

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Hidden
from crispy_forms.bootstrap import FormActions


class RegisterConfirmEmailForm(forms.Form):

    email = forms.EmailField(
        label=u'E-mail',
        required=True,
        help_text=u'Informe seu e-mail para criação da conta.'
    )

    def __init__(self, *args, **kwargs):
        # load super class 
        super(RegisterConfirmEmailForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'signup-confirm-form'
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'
        self.helper.form_action = '.'

        self.helper.add_input(Submit('submit', 'Enviar'))

    def clean_email(self):
        email = self.cleaned_data.get('email', None)
        if User.objects.filter(email=email):
            raise forms.ValidationError(u'E-mail já cadastrado.')
        return email

    def save(self):
        # get email
        email = self.cleaned_data.get('email')

        # get site
        site = Site.objects.get_current()

        # create signed
        signed_value = signing.dumps(
            {
                'email': email,
                'register': True,
            }
        )

        # render email
        html_content = render_to_string('accounts/emails/register_confirm_email.html',
            {
                'signed_value': signed_value,
                'MEDIA_URL': settings.MEDIA_URL,
                'site': site,
            }
        )
        subject = '%s - Confirme sua conta' % site.name
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = email
        msg = EmailMessage(subject, html_content, from_email, [to_email])
        msg.content_subtype = 'html'
        msg.send(fail_silently=True)


class RegisterForm(forms.Form):

    name = forms.CharField(
        label=u'Nome',
        min_length=3,
        required=True,
        help_text=u'Seu nome completo.'
    )

    username = forms.RegexField(
        label=u'Login',
        regex=r'^[\w]+$',
        error_messages={
            'invalid': u'Use apenas letras e números para o login.'
        },
        min_length=3,
        max_length=30,
        required=True,
        help_text=u'Escolha um login.'
    )

    password1 = forms.CharField(
        label=u'Senha',
        max_length=16,
        min_length=6,
        required=True,
        widget=forms.PasswordInput,
        help_text=u'Escolha uma senha com seis caracteres ou mais.'
    )
    password2 = forms.CharField(
        label=u'Confirmar senha',
        max_length=16,
        min_length=6,
        required=True,
        widget=forms.PasswordInput,
        help_text=u'Repita a senha escolhida acima.'
    )
    
    def __init__(self, *args, **kwargs):
        # load super class 
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'signup-confirm'
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'
        self.helper.form_action = '.'

        self.helper.add_input(Submit('submit', 'Enviar'))

    def clean_username(self):
        username = self.cleaned_data.get('username', None)
        if User.objects.filter(username=username):
            raise forms.ValidationError(u'Login já cadastrado.')
        if username != username.lower():
            raise forms.ValidationError(u'Use apenas caracteres minúsculos para o login.')
        return username

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1', None)
        password2 = self.cleaned_data.get('password2', None)
        if password1 != password2:
            raise forms.ValidationError(u'As duas senhas não conferem.')
        return password2

    def save(self, email, unit=None):
        # get fields
        password = self.cleaned_data.get('password2')
        name = self.cleaned_data.get('name')
        username = self.cleaned_data.get('username')

        # create user
        user = User.objects.create_user(username, email, password)
        split_name = name.split(' ', 1)
        user.first_name = split_name[0]
        if len(split_name) == 2:
            user.last_name = split_name[1]
        user.save()

        # return user authenticated
        return authenticate(username=username, password=password)


class LoginForm(forms.Form):
    
    username = forms.CharField(
        label=u'Login',
        required=True,
        help_text=u'Entre com seu login.'
    )
    password = forms.CharField(
        label=u'Senha',
        required=True,
        widget=forms.PasswordInput,
        help_text=u'Entre com sua senha.'
    )

    def __init__(self, *args, **kwargs):
        # load super class 
        super(LoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'login-form'
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'
        self.helper.form_action = '.'
        self.helper.layout = Layout(
            Fieldset(
                '',
                'username',
                'password',
            ),
            Hidden('next', '{{ next }}'),
            FormActions(
                Submit('submit', 'Submit')
            )
        )

    def clean_username(self):
        username = self.cleaned_data.get('username', None)
        if not User.objects.filter(username=username):
            raise forms.ValidationError(u'Login não cadastrado.')
        return username

    def clean_password(self):
        username = self.cleaned_data.get('username', None)
        password = self.cleaned_data.get('password', None)
        if not authenticate(username=username, password=password):
            raise forms.ValidationError(u'Senha inválida.')
        return password

    def clean(self):
        username = self.cleaned_data.get('username', None)
        password = self.cleaned_data.get('password', None)
        user = authenticate(username=username, password=password)
        if user:
            if not user.is_active:
                raise forms.ValidationError(u'Conta inativa.')
        return self.cleaned_data

    def save(self):
        username = self.cleaned_data.get('username', None)
        password = self.cleaned_data.get('password', None)
        return authenticate(username=username, password=password)


class ForgotPasswordForm(forms.Form):

    email = forms.EmailField(
        label=u'E-mail',
        required=True,
        help_text=u'Entre com o seu e-mail.'
    )
    
    def __init__(self, *args, **kwargs):
        super(ForgotPasswordForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'forgot-password-form'
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'
        self.helper.form_action = '.'

        self.helper.add_input(Submit('submit', 'Enviar'))

    def clean_email(self):
        email = self.cleaned_data.get('email', None)
        if not User.objects.filter(email=email):
            raise forms.ValidationError(u'E-mail não cadastrado.')
        return email

    def save(self):
        # get email
        email = self.cleaned_data.get('email')

        # get site
        site = Site.objects.get_current()

        # create signed
        signed_value = signing.dumps(
            {
                'email': email,
                'forgot-password': True,
            }
        )

        # render email
        html_content = render_to_string('accounts/emails/forgot_password.html',
            {
                'signed_value': signed_value,
                'MEDIA_URL': settings.MEDIA_URL,
                'site': site,
            }
        )
        subject = '%s - Redefina sua senha.' % site.name
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = email
        msg = EmailMessage(subject, html_content, from_email, [to_email])
        msg.content_subtype = 'html'
        msg.send(fail_silently=True)


class ForgotPasswordConfirmForm(forms.Form):

    password1 = forms.CharField(
        label=u'Nova senha',
        max_length=16,
        min_length=6,
        required=True,
        widget=forms.PasswordInput,
        help_text=u'Escolha uma nova senha.'
    )
    password2 = forms.CharField(
        label=u'Confirmar nova senha',
        max_length=16,
        min_length=6,
        required=True,
        widget=forms.PasswordInput,
        help_text=u'Repita a senha escolhida acima.'
    )

    def __init__(self, *args, **kwargs):
         # get user
        self.user = kwargs.pop('user', None)

        # load super class 
        super(ForgotPasswordConfirmForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'forgot-password-form-confirm'
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'
        self.helper.form_action = '.'

        self.helper.add_input(Submit('submit', 'Enviar'))

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1', None)
        password2 = self.cleaned_data.get('password2', None)
        if password1 != password2:
            raise forms.ValidationError(u'As duas senhas não conferem.')
        return password2

    def save(self):
        # get user and password
        user = self.user
        password2 = self.cleaned_data.get('password2')

        # set user password
        user.set_password(password2)

        # return user
        return user.save()
