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
	if form.is_valid():
		name = form.cleaned_data['name']
		emaila = form.cleaned_data['email']
		message = form.cleaned_data['message']
		context = {
		'form': form,
		'email': False,
		'captcha': False,
		}
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
	

def locstar (request):
	if request.method == 'POST':
		return render(request, 'locstar/email.html', emailformOK(request))
	else:
		return render(request, 'locstar/locstar.html', emailform())
		
def people (request):
	if request.method == 'POST':
		#emailformOK(request)
		return render(request, 'locstar/email.html', emailformOK(request))
	else:
		return render(request, 'locstar/people.html', emailform())
		
def onas (request):
	if request.method == 'POST':
		#emailformOK(request)
		return render(request, 'locstar/email.html', emailformOK(request))
	else:
		return render(request, 'locstar/onas.html', emailform())
def special (request):
	if request.method == 'POST':
		#emailformOK(request)
		return render(request, 'locstar/email.html', emailformOK(request))
	else:
		return render(request, 'locstar/special.html', emailform())
def prices (request):
	if request.method == 'POST':
		#emailformOK(request)
		return render(request, 'locstar/email.html', emailformOK(request))
	else:
		return render(request, 'locstar/prices.html', emailform())
def contact (request):
	if request.method == 'POST':
		#emailformOK(request)
		return render(request, 'locstar/email.html', emailformOK(request))
	else:
		return render(request, 'locstar/contact.html', emailform())
def technologie (request):
	if request.method == 'POST':
		#emailformOK(request)
		return render(request, 'locstar/email.html', emailformOK(request))
	else:
		return render(request, 'locstar/technologie.html', emailform())
def tm (request):
	if request.method == 'POST':
		#emailformOK(request)
		return render(request, 'locstar/email.html', emailformOK(request))
	else:
		return render(request, 'locstar/tm.html', emailform())
def servicegrid (request):
	if request.method == 'POST':
		#emailformOK(request)
		return render(request, 'locstar/email.html', emailformOK(request))
	else:
		return render(request, 'locstar/servicegrid.html', emailform())
def servicetl (request):
	if request.method == 'POST':
		emailformOK(request)
		return render(request, 'locstar/email.html', emailformOK(request))
	else:
		return render(request, 'locstar/servicetl.html', emailform())					
def terminology (request):
	if request.method == 'POST':
		#emailformOK(request)
		return render(request, 'locstar/email.html', emailformOK(request))
	else:
		return render(request, 'locstar/terminology.html', emailform())		
def tools (request):
	if request.method == 'POST':
		#emailformOK(request)
		return render(request, 'locstar/email.html', emailformOK(request))
	else:
		return render(request, 'locstar/tools.html', emailform())		
def mt (request):
	if request.method == 'POST':
		#emailformOK(request)
		return render(request, 'locstar/email.html', emailformOK(request))
	else:
		return render(request, 'locstar/mt.html', emailform())		
def customers (request):
	if request.method == 'POST':
		#emailformOK(request)
		return render(request, 'locstar/email.html', emailformOK(request))
	else:
		return render(request, 'locstar/customers.html', emailform())		
def translation (request):
	if request.method == 'POST':
		#emailformOK(request)
		return render(request, 'locstar/email.html', emailformOK(request))
	else:
		return render(request, 'locstar/translation.html', emailform())		
def localization (request):
	if request.method == 'POST':
		#emailformOK(request)
		return render(request, 'locstar/email.html', emailformOK(request))
	else:
		return render(request, 'locstar/localization.html', emailform())		
def website (request):
	if request.method == 'POST':
		#emailformOK(request)
		return render(request, 'locstar/email.html', emailformOK(request))
	else:
		return render(request, 'locstar/website.html', emailform())		
def other (request):
	if request.method == 'POST':
		#emailformOK(request)
		return render(request, 'locstar/email.html', emailformOK(request))
	else:
		return render(request, 'locstar/other.html', emailform())		