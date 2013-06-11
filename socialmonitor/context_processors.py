# -*- coding: utf-8 -*-
from django.conf import settings


def inject_settings(request):
    return {'settings': settings}