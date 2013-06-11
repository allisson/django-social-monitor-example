# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings


admin.autodiscover()


urlpatterns = patterns('',
    # admin app
    url(r'^admin/', include(admin.site.urls)),

    # staticpages app
    url(r'^$', 'staticpages.views.index', name='staticpages_index'),
    url(r'^about/$', 'staticpages.views.about', name='staticpages_about'),

    # accounts app
    url(r'^signup/$', 'accounts.views.register_confirm_email',
        name='accounts_register_confirm_email'),
    url(r'^signup/(?P<token>[\w:-]+)/$', 'accounts.views.register',
        name='accounts_register'),
    url(r'^login/$', 'accounts.views.login', name='accounts_login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout',
        {'next_page': '/',}, name='accounts_logout'),
    url(r'^forgot-password/$', 'accounts.views.forgot_password',
        name='accounts_forgot_password'),
    url(r'^forgot-password/(?P<token>[\w:-]+)/$', 'accounts.views.forgot_password_confirm',
        name='accounts_forgot_password_confirm'),
    url(r'^account/social/$', 'accounts.views.social_account_list', 
        name='accounts_social_account_list'),
    url(r'^account/social/(?P<pk>[0-9]+)/delete/$', 'accounts.views.social_account_delete', 
        name='accounts_social_account_delete'),
    url(r'^account/connect/twitter/$', 'accounts.views.connect_twitter', 
        name='accounts_connect_twitter'),
    url(r'^account/connect/twitter/callback/$', 'accounts.views.connect_twitter_callback', 
        name='accounts_connect_twitter_callback'),

    # dashboard app
    url(r'^dashboard/$', 'dashboard.views.index', name='dashboard_index'),
    url(r'^dashboard/searchs/$', 'dashboard.views.search_list', 
        name='dashboard_search_list'),
    url(r'^dashboard/searchs/new/$', 'dashboard.views.search_new', 
        name='dashboard_search_new'),
    url(r'^dashboard/searchs/(?P<pk>[0-9]+)/edit/$', 'dashboard.views.search_edit', 
        name='dashboard_search_edit'),
    url(r'^dashboard/searchs/(?P<pk>[0-9]+)/delete/$', 'dashboard.views.search_delete', 
        name='dashboard_search_delete'),
    url(r'^dashboard/items/$', 'dashboard.views.item_list', 
        name='dashboard_item_list'),
    url(r'^dashboard/items/(?P<pk>[0-9]+)/delete/$', 'dashboard.views.item_delete', 
        name='dashboard_item_delete'),
)


if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    )


urlpatterns += staticfiles_urlpatterns()
