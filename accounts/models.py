# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User


SITE_CHOICES = (
    (u'twitter', u'Twitter'),
)


class SocialAccount(models.Model):
    
    user = models.ForeignKey(
        User,
        verbose_name=u'Usuário',
        related_name='social_accounts'
    )

    site = models.CharField(
        u'Site',
        max_length=20,
        db_index=True,
        choices=SITE_CHOICES
    )

    access_token = models.CharField(
        u'Access token',
        max_length=100
    )

    access_token_secret = models.CharField(
        u'Access token secret',
        max_length=100
    )

    account_user_id = models.CharField(
        u'User id',
        max_length=50
    )

    account_screen_name = models.CharField(
        u'Screen name',
        max_length=50
    )

    # Audit fields
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'Site: %s - Usuário: %s' % (self.get_site_display(), self.user)

    class Meta:
        verbose_name = u'Conta social'
        verbose_name_plural = u'Contas sociais'
