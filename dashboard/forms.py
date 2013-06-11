# -*- coding: utf-8 -*-
from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Hidden
from crispy_forms.bootstrap import FormActions

from dashboard.models import SocialSearch, Item


class SocialSearchForm(forms.ModelForm):

    class Meta:
        model = SocialSearch
        exclude = ('user',)

    def __init__(self, *args, **kwargs):
        # load super class 
        super(SocialSearchForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'search-form'
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'
        self.helper.form_action = '.'

        self.helper.add_input(Submit('submit', 'Enviar'))
