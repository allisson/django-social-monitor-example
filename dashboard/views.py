# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from dashboard.models import SocialSearch, Item
from dashboard.forms import SocialSearchForm


@login_required
def index(request):
    return redirect('dashboard_search_list')


@login_required
def search_list(request):
    social_search_list = request.user.social_searchs.all()
    return render(request, 'dashboard/search_list.html', 
        {'social_search_list': social_search_list}
    )

@login_required
def search_new(request):
    if request.method == 'POST':
        form = SocialSearchForm(request.POST)
        if form.is_valid():
            social_search = form.save(commit=False)
            social_search.user = request.user
            social_search.save()
            messages.success(request, u'Busca adicionada com sucesso.')
            return redirect('dashboard_search_list')
    else:
        form = SocialSearchForm()
    return render(request, 'dashboard/search_new.html', {'form': form})


@login_required
def search_edit(request, pk):
    social_search = get_object_or_404(SocialSearch, user=request.user, pk=pk)
    if request.method == 'POST':
        form = SocialSearchForm(request.POST, instance=social_search)
        if form.is_valid():
            form.save()
            messages.success(request, u'Busca atualizada com sucesso.')
            return redirect('dashboard_search_list')
    else:
        form = SocialSearchForm(instance=social_search)
    return render(request, 'dashboard/search_edit.html', {'form': form})


def search_delete(request, pk):
    social_search = get_object_or_404(SocialSearch, user=request.user, pk=pk)
    if request.method == 'POST':
        social_search.delete()
        messages.success(request, u'Busca excluída com sucesso.')
        return redirect('dashboard_search_list')
    return render(request, 'dashboard/search_delete.html', {'social_search': social_search})


@login_required
def item_list(request):
    social_search_ids = request.user.social_searchs.all().values_list('pk', flat=True)
    item_list = Item.objects.filter(social_search__in=social_search_ids)
    return render(request, 'dashboard/item_list.html', {'item_list': item_list})


@login_required
def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if item.social_search.user != request.user:
        messages.error(request, u'Você não pode excluir esse item.')
        return redirect('dashboard_item_list')

    if request.method == 'POST':
        item.delete()
        messages.success(request, u'Item excluído com sucesso.')
        return redirect('dashboard_item_list')
    return render(request, 'dashboard/item_delete.html', {'item': item})
