# -*- coding: utf-8 -*-
from django.contrib import admin

from dashboard.models import SocialSearch, Item


class SocialSearchAdmin(admin.ModelAdmin):
    pass


class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'social_item_id', 'social_item_text')


admin.site.register(SocialSearch, SocialSearchAdmin)
admin.site.register(Item, ItemAdmin)
