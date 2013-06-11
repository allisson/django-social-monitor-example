# -*- coding: utf-8 -*-
from django.shortcuts import render


def index(request):
    return render(request, 'staticpages/index.html')


def about(request):
    return render(request, 'staticpages/about.html')
