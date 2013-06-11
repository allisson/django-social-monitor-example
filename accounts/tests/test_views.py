# -*- coding: utf-8 -*-
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core import mail
from django.contrib.auth import authenticate
from django.core import signing
from django.conf import settings
from django.utils.http import urlquote

from datetime import date


class RegisterConfirmEmailViewTest(TestCase):

    def setUp(self):
        self.url = reverse('accounts_register_confirm_email')
        self.user1 = User.objects.create_user(
            'user1',
            'user1@email.com',
            '123456'
        )

    def test_render(self):
        # load view
        response = self.client.get(self.url)

        # check status code
        self.assertEquals(response.status_code, 200)

    def test_empty_form(self):
        # load post
        response = self.client.post(self.url)

        # check form errors
        self.assertFormError(
            response,
            'form',
            'email',
            u'Este campo é obrigatório.'
        )

    def test_form_with_registered_email(self):
        # load post
        response = self.client.post(
            self.url,
            {
                'email': 'user1@email.com',
            }
        )

        # check form errors
        self.assertFormError(
            response,
            'form',
            'email',
            u'E-mail já cadastrado.'
        )

    def test_valid_form(self):
        # check mailbox
        self.assertEqual(len(mail.outbox), 0)

        # load post
        response = self.client.post(
            self.url,
            {
                'email': 'user2@email.com',
            },
            follow=True
        )
        # check redirect
        self.assertRedirects(response, self.url)

        # check message
        self.assertContains(response, u'Verifique o link que foi enviado para o seu e-mail.')

        # check mailbox
        self.assertEqual(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].subject, u'example.com - Confirme sua conta')


class RegisterViewTest(TestCase):

    def setUp(self):
        self.token = signing.dumps(
            {
                'email': 'user1@email.com',
                'register': True
            }
        )
        self.url = reverse('accounts_register', args=[self.token])

    def test_render_with_invalid_token(self):
        # load view
        response = self.client.get(
            reverse('accounts_register', args=[self.token + 'a']),
            follow=True
        )

        # check redirect
        self.assertRedirects(response, reverse('accounts_register_confirm_email'))

        # check message
        self.assertContains(
            response,
            u'Link de ativação inválido.'
        )

    def test_render_with_processed_token(self):
        # create new user
        user = User.objects.create_user(
            u'user1',
            u'user1@email.com',
            u'123456'
        )

        # load view
        response = self.client.get(
            reverse('accounts_register', args=[self.token]),
            follow=True
        )

        # check redirect
        self.assertRedirects(response, reverse('accounts_register_confirm_email'))

        # check message
        self.assertContains(response, u'E-mail já cadastrado.')

    def test_render_with_registered_email(self):
        # create new user
        user = User.objects.create_user(
            u'user1',
            u'user1@email.com',
            u'123456'
        )

        # load view
        response = self.client.get(self.url, follow=True)

        # check message
        self.assertContains(
            response,
            u'E-mail já cadastrado.'
        )

    def test_render_with_valid_token(self):
        # load view
        response = self.client.get(self.url, follow=True)

        # check status code
        self.assertEquals(response.status_code, 200)

    def test_empty_form(self):
        # load post
        response = self.client.post(self.url)

        # check form errors
        self.assertFormError(
            response,
            'form',
            'name',
            u'Este campo é obrigatório.'
        )
        self.assertFormError(
            response,
            'form',
            'username',
            u'Este campo é obrigatório.'
        )
        self.assertFormError(
            response,
            'form',
            'password1',
            u'Este campo é obrigatório.'
        )
        self.assertFormError(
            response,
            'form',
            'password2',
            u'Este campo é obrigatório.'
        )

    def test_form_with_dont_match_passwords(self):
        # load post
        response = self.client.post(
            self.url,
            {
                'password1': '123456',
                'password2': '1234567',
                }
        )

        # check form errors
        self.assertFormError(
            response,
            'form',
            'password2',
            u'As duas senhas não conferem.'
        )

    def test_form_with_registered_username(self):
        # create new user
        user = User.objects.create_user(
            u'user1',
            u'user1@email.com.br',
            u'123456'
        )

        # load post
        response = self.client.post(
            self.url,
            {
                'username': 'user1',
            }, follow=True
        )

        # check form errors
        self.assertFormError(
            response,
            'form',
            'username',
            u'Login já cadastrado.'
        )

    def test_form_with_upper_username(self):
        # load post
        response = self.client.post(
            self.url,
            {
                'username': 'User1',
            }, follow=True
        )

        # check form errors
        self.assertFormError(
            response,
            'form',
            'username',
            u'Use apenas caracteres minúsculos para o login.'
        )

    def test_form_with_invalid_username(self):
        # load post
        response = self.client.post(
            self.url,
            {
                'username': 'user1@email.com',
            }, follow=True
        )

        # check form errors
        self.assertFormError(
            response,
            'form',
            'username',
            u'Use apenas letras e números para o login.'
        )

    def test_valid_form(self):
        # load post
        response = self.client.post(
            self.url,
            {
                'name': u'User One',
                'username': u'user1',
                'password1': u'123456',
                'password2': u'123456'
            },
            follow=True
        )

        # check redirect
        self.assertRedirects(response, reverse('staticpages_index'))

        # check message
        self.assertContains(
            response,
            u'Conta criada com sucesso.'
        )

        # check user
        self.assertTrue(User.objects.filter(username=u'user1'))


class LoginViewTest(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(
            'user1',
            'user1@email.com',
            '123456'
        )
        self.url = reverse('accounts_login')

    def test_render(self):
        # load view
        response = self.client.get(self.url)

        # check status code
        self.assertEquals(response.status_code, 200)

    def test_empty_form(self):
        # load post
        response = self.client.post(self.url)

        # check form errors
        self.assertFormError(
            response,
            'form',
            'username',
            u'Este campo é obrigatório.'
        )
        self.assertFormError(
            response,
            'form',
            'password',
            u'Este campo é obrigatório.'
        )

    def test_form_with_invalid_username(self):
        # load post
        response = self.client.post(
            self.url,
            {
                'username': 'user2',
            }
        )

        # check form errors
        self.assertFormError(
            response,
            'form',
            'username',
            u'Login não cadastrado.'
        )

    def test_form_with_invalid_password(self):
        # load post
        response = self.client.post(
            self.url,
            {
                'username': 'user1',
                'password': '1234567',
            }
        )

        # check form errors
        self.assertFormError(
            response,
            'form',
            'password',
            u'Senha inválida.'
        )

    def test_form_with_inactive_account(self):
        # make account inactive
        self.user1.is_active = False
        self.user1.save()

        # load post
        response = self.client.post(
            self.url,
            {
                'username': 'user1',
                'password': '123456',
            }, follow=True
        )

        # check form errors
        self.assertFormError(
            response,
            'form',
            None,
            u'Conta inativa.'
        )

    def test_valid_form(self):
        # load post
        response = self.client.post(
            self.url,
            {
                'username': 'user1',
                'password': '123456',
            }, follow=True
        )
        # check redirect
        self.assertRedirects(response, settings.LOGIN_REDIRECT_URL)

    def test_form_valid_with_next(self):
        # load post
        response = self.client.post(
            self.url,
            {
                'username': 'user1',
                'password': '123456',
                'next': '/about/',
            }, follow=True
        )

        # check redirect
        self.assertRedirects(response, reverse('staticpages_about'))


class ForgotPasswordViewTest(TestCase):

    def setUp(self):
        self.url = reverse('accounts_forgot_password')
        self.user1 = User.objects.create_user(
            'user1@email.com',
            'user1@email.com',
            '123456'
        )

    def test_render(self):
        # load view
        response = self.client.get(self.url)

        # check status code
        self.assertEquals(response.status_code, 200)

    def test_empty_form(self):
        # load post
        response = self.client.post(self.url)

        # check form errors
        self.assertFormError(
            response,
            'form',
            'email',
            u'Este campo é obrigatório.'
        )

    def test_form_with_not_registered_email(self):
        # load post
        response = self.client.post(
            self.url,
            {
                'email': 'user2@email.com',
            }
        )

        # check form errors
        self.assertFormError(
            response,
            'form',
            'email',
            u'E-mail não cadastrado.'
        )

    def test_form_valid(self):
        # check mailbox
        self.assertEqual(len(mail.outbox), 0)

        # load post
        response = self.client.post(
            self.url,
            {
                'email': 'user1@email.com',
            }, follow=True
        )

        # check redirect
        self.assertRedirects(response, self.url)
        
        # check message
        self.assertContains(response, u'Verifique o link que foi enviado para o seu e-mail.')

        # check mailbox
        self.assertEqual(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].subject, u'example.com - Redefina sua senha.')


class ForgotPasswordConfirmViewTest(TestCase):

    def setUp(self):
        self.token = signing.dumps(
            {'email': 'user1@email.com', 'forgot-password': True}
        )
        self.user1 = User.objects.create_user(
            'user1',
            'user1@email.com',
            '123456'
        )
        self.url = reverse(
            'accounts_forgot_password_confirm', args=[self.token]
        )

    def test_render_with_invalid_token(self):
        # load view
        response = self.client.get(
            reverse(
                'accounts_forgot_password_confirm', args=[self.token + 'a']
            ), follow=True
        )

        # check redirect
        self.assertRedirects(response, reverse('accounts_forgot_password'))

        # check message
        self.assertContains(response, u'Link inválido.')

    def test_render_with_not_registered_user(self):
        self.user1.delete()

        # load view
        response = self.client.get(self.url, follow=True)

        # check redirect
        self.assertRedirects(response, reverse('accounts_forgot_password'))

        # check message
        self.assertContains(response, u'E-mail não cadastrado.')

    def test_render_with_valid_user(self):
        # load view
        response = self.client.get(self.url)

        # check status code
        self.assertEquals(response.status_code, 200)

    def test_empty_form(self):
        # load post
        response = self.client.post(self.url)

        # check form errors
        self.assertFormError(
            response,
            'form',
            'password1',
            u'Este campo é obrigatório.'
        )
        self.assertFormError(
            response,
            'form',
            'password2',
            u'Este campo é obrigatório.'
        )

    def test_form_with_dont_match_passwords(self):
        # load post
        response = self.client.post(
            self.url,
            {
                'password1': '123456',
                'password2': '1234567',
            }
        )

        # check form errors
        self.assertFormError(
            response,
            'form',
            'password2',
            u'As duas senhas não conferem.'
        )

    def test_valid_form(self):
        # load post
        response = self.client.post(
            self.url,
            {
                'password1': '1234567',
                'password2': '1234567',
            }, follow=True
        )

        # check redirect
        self.assertRedirects(response, reverse('accounts_login'))

        # check message
        self.assertContains(
            response, 
            u'Senha alterada com sucesso.'
        )

        # check user new password
        self.assertTrue(
            authenticate(username='user1', password='1234567')
        )
