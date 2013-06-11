# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User

from accounts.models import SocialAccount


SEARCH_TYPE_CHOICES = (
    (u'twitter-search', u'Twitter - Busca'),
)


class SocialSearch(models.Model):

    user = models.ForeignKey(
        User,
        verbose_name=u'Usuário',
        related_name='social_searchs'
    )

    social_account = models.ForeignKey(
        SocialAccount,
        verbose_name=u'Conta social',
        related_name='social_searchs'
    )

    search_type = models.CharField(
        u'Tipo de pesquisa',
        max_length=30,
        db_index=True,
        choices=SEARCH_TYPE_CHOICES
    )

    search_term = models.CharField(
        u'Termo de pesquisa',
        max_length=250
    )

    last_collection_date = models.DateTimeField(
        u'Data da última coleta',
        null=True,
        blank=True,
        editable=False
    )

    item_count = models.PositiveIntegerField(
        u'Quantidade de itens',
        default=0,
        editable=False
    )

    since_id = models.BigIntegerField(
        u'Since id',
        default=0,
        editable=False
    )

    # Audit fields
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return '%s - %s' % (self.get_search_type_display(), self.search_term)

    class Meta:
        verbose_name = u'Busca social'
        verbose_name_plural = u'Buscas sociais'


class Item(models.Model):

    social_search = models.ForeignKey(
        SocialSearch,
        verbose_name=u'Busca social',
        related_name='items'
    )

    social_item_id = models.CharField(
        u'Id do item',
        max_length=50
    )

    social_item_text = models.TextField(
        u'Texto',
    )

    social_user_id = models.CharField(
        u'Id do usuário',
        max_length=50
    )

    social_user_screen_name = models.CharField(
        u'Nome de usuário',
        max_length=50
    )

    social_user_name = models.CharField(
        u'Nome',
        max_length=100
    )

    social_user_avatar = models.URLField(
        u'Avatar do usuário',
        max_length=250
    )

    # Audit fields
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return '%s - %s' % (self.social_search, self.id)

    class Meta:
        verbose_name = u'Item'
        verbose_name_plural = u'Items'
        ordering = ['-created_on']
