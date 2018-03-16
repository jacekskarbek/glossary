# -*- coding: utf-8 -*- 
from django import forms
from captcha.fields import ReCaptchaField
from django.utils.translation import ugettext_lazy as _

class ContactForm(forms.Form):
    #searchTerm = forms.CharField(label='Term: ', label_suffix="", max_length=100, widget=forms.TextInput(attrs={'class' : 'form-control input-cls'}))
    name = forms.CharField(required=True, label='', label_suffix="", max_length=100, widget=forms.TextInput(attrs={'class' : 'contactSearchBar', 'placeholder': _(u'Imię i nazwisko')})  )
    email = forms.EmailField(required=True, label='', label_suffix="", max_length=100, widget=forms.EmailInput(attrs={'class' : 'contactSearchBar', 'placeholder': _(u'Adres e-mail')}), localize=True )
    message = forms.CharField(required=True, label='', label_suffix="", max_length=100, widget=forms.Textarea(attrs={'class' : 'contactSearchBar', 'placeholder': _(u'Wiadomość')}), localize=True )
    captcha = ReCaptchaField(required=True)