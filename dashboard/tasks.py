# -*- coding: utf-8 -*-
from django.conf import settings

from urlparse import parse_qs, urlparse
from datetime import datetime
from celery import task
from twython import Twython
from dashboard.models import SocialSearch, Item


@task(ignore_result=True)
def collect_all_social_searchs():
    social_search_list = SocialSearch.objects.all()
    for social_search in social_search_list:
        collect_social_search.apply_async(args=[social_search.id])


@task(ignore_result=True)
def collect_social_search(social_search_id):
    try:
        social_search = SocialSearch.objects.get(id=social_search_id)
    except SocialSearch.DoesNotExist:
        return

    social_account = social_search.social_account
    app_key = settings.TWITTER_APP_KEY 
    app_secret = settings.TWITTER_APP_SECRET
    oauth_token = social_account.access_token
    oauth_token_secret = social_account.access_token_secret
    search_term = social_search.search_term
    since_id = social_search.since_id

    t = Twython(app_key, app_secret, oauth_token, oauth_token_secret)

    items = t.search(q=search_term, result_type='recent', count=100, since_id=since_id)    

    if items['search_metadata']['count'] > 0:
        for item in items['statuses']:
            item_object = Item()
            item_object.social_search = social_search
            item_object.social_item_id = item['id']
            item_object.social_item_text = item['text']
            item_object.social_user_id = item['user']['id']
            item_object.social_user_screen_name = item['user']['screen_name']
            item_object.social_user_name = item['user']['name']
            item_object.social_user_avatar = item['user']['profile_image_url']
            item_object.save()

    social_search.last_collection_date = datetime.now()
    social_search.item_count = Item.objects.filter(social_search=social_search).count()
    social_search.since_id = items['search_metadata']['max_id']
    social_search.save()

    return
