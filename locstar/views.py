# -*- coding: utf-8 -*- 
from django.shortcuts import render, redirect
from .forms import ContactForm
from django.core.mail import EmailMessage
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
import urllib
import json
from django.conf import settings
from django.contrib import messages

def facebook (request):
	return HttpResponseRedirect('https://www.facebook.com/LocstarPL/')
	
def twitter (request):
	return HttpResponseRedirect('https://twitter.com/LocStarPL')
	
def linkedin (request):
	return HttpResponseRedirect('https://www.linkedin.com/company/2171495/')
	
	
def error_404(request):
    data = {}
    print('HALO')
    return render(request,'404.html', data)

def emailform():
	form=ContactForm()
	context = {
			'form': form,
			'email': True,
	}
	return context
	
def emailformOK(request):
	form=ContactForm(request.POST)
	context = {
		'form': form,
		'email': False,
		'captcha': False,
		}
	if form.is_valid():
		name = form.cleaned_data['name']
		emaila = form.cleaned_data['email']
		message = form.cleaned_data['message']
		email = EmailMessage(_(u'Zapytanie ze strony Locstar: ')+name+', '+emaila, message, to=['info@locstar.pl'])
		email.send()
		email = EmailMessage(_(u'Zapytanie ze strony Locstar: ')+name+', '+emaila, message, to=[emaila])
		print(u'wysyłamy')
		email.send()
		context = {
			'form': form,
			'email': False,
			'captcha': True,
			}
	return context
	

def renderwithemail(request, link):
	if request.method == 'POST':
		emailOK=emailformOK(request)
		if emailOK['captcha']:
			return render(request, 'locstar/email.html', emailOK)
	return render(request, link, emailform())

def locstar (request):
	return renderwithemail(request, 'locstar/locstar.html')
def people (request):
	return renderwithemail(request, 'locstar/people.html')
def onas (request):
	return renderwithemail(request, 'locstar/onas.html')
def special (request):
	return renderwithemail(request, 'locstar/special.html')
def prices (request):
	return renderwithemail(request, 'locstar/prices.html')
def contact (request):
	return renderwithemail(request, 'locstar/contact.html')
def technologie (request):
	return renderwithemail(request, 'locstar/technologie.html')
def tm (request):
	return renderwithemail(request, 'locstar/tm.html')
def servicegrid (request):
	return renderwithemail(request, 'locstar/servicegrid.html')
def servicetl (request):
	return renderwithemail(request, 'locstar/servicetl.html')				
def terminology (request):
	return renderwithemail(request, 'locstar/terminology.html')
def tools (request):
	return renderwithemail(request, 'locstar/tools.html')		
def mt (request):
	return renderwithemail(request, 'locstar/mt.html')	
def customers (request):
	return renderwithemail(request, 'locstar/customers.html')	
def translation (request):
	return renderwithemail(request, 'locstar/translation.html')	
def localization (request):
	return renderwithemail(request, 'locstar/localization.html')			
def website (request):
	return renderwithemail(request, 'locstar/website.html')	
def other (request):
	return renderwithemail(request, 'locstar/other.html')		