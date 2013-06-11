# -*- coding: utf-8 -*-
from django.contrib import admin

from accounts.models import SocialAccount

class SocialAccountAdmin(admin.ModelAdmin):
    pass

admin.site.register(SocialAccount, SocialAccountAdmin)
