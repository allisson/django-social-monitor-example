# -*- coding: utf-8 -*-
from django.test import TestCase
from django.core.urlresolvers import reverse


# Test Views
class IndexViewTest(TestCase):
    
    def setUp(self):
        self.url = reverse('staticpages_index')
    
    def test_render(self):
        # load view
        response = self.client.get(self.url)

        # check status code
        self.assertEquals(response.status_code, 200)


class AboutViewTest(TestCase):
    
    def setUp(self):
        self.url = reverse('staticpages_about')
    
    def test_render(self):
        # load view
        response = self.client.get(self.url)

        # check status code
        self.assertEquals(response.status_code, 200)
