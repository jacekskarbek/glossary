# -*- coding: utf-8 -*- 
from django.shortcuts import render
from django import forms
from django.forms import formset_factory, modelformset_factory
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.template import loader
from .models import Termbase, UserTermbase, Term, Language, Description, Hits, Dtype
from .forms import NameForm, DocumentForm, Termbases, Sourcelanguage, Targetlanguage, ContactForm, SearchHits
from .serializers import TermSerializer, TermbaseSerializer
from django.contrib.auth import authenticate, login
from django.db.models import Q
from django.contrib import admin
from django.conf.urls import url
#from channels import Channel, Group
#from channels.sessions import channel_session
import json
import os
from rest_framework import viewsets
from glos.serializers import UserSerializer, GroupSerializer, UserTermbaseSerializer, TermbaseSerializer, LanguageSerializer, ResultsSerializer, UserTermbaseSerial, TermbaseResultsSerializer
from django.contrib.auth.models import User, Group
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, DjangoModelPermissions
from rest_framework.response import Response
import time
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import EmailMessage
from django.contrib.postgres.search import TrigramSimilarity
from django.contrib.postgres.search import SearchQuery, SearchVector
import re
#from stemming.porter2 import stem


class DescriptionItem:
	pass
class TermGroup:
	pass
class LanguageItem:
	pass
class TbxItem:
	pass
class TermBase:
	pass
class TBelement:
	pass
def lspsoftware (request):
    return HttpResponseRedirect('http://www.lspsoftware.pl/uslugi/locterms-serwer-terminologii-online')
    
def error_404(request):
        data = {}
        return render(request,'glos/404.html', data)


def create_post(request):
	if request.method == 'POST':
		search = request.POST.get('search')
		search=search.strip().lower()
		if len(search)>=3:
			hit=request.POST.get('hit')
			hitstext=Hits.objects.filter(pk=hit)[0].hit
			hits=int(hitstext)
			normal=True
			start=True
			full = True
			stem=False
			sourcelanguage = request.POST.get('source')
			targetlanguage = request.POST.get('target')
			sourcelanguagename = Language.objects.filter(pk=sourcelanguage)[0].name
			targetlanguagename = Language.objects.filter(pk=targetlanguage)[0].name
			selectedtermbases = request.POST.getlist('selectedtermbases[]')	
			if search[-1]=='*':
				search=search[:-1]
				normal=False
			if search[0]=='*':
				search=search[1:]
				normal=False
				start=False
			if 'stemsearching' in selectedtermbases:
				stem=True
			if ('fulltext' in selectedtermbases) or ('stemsearching' in selectedtermbases):
				normal=False
				start=False	
			
			myuser=request.user
			if not request.user.is_authenticated:
				myuser = User.objects.get(username='anonymous')
			termResult=UserTermbase.objects.filter(user=myuser)
			print(selectedtermbases)
			print('START',time.time())
			source=''
			target=''
			#targetlength=0
			if normal:
				source = Term.objects.filter(lowvalue__exact=search, language=sourcelanguage, termbase__name__in=selectedtermbases)
				source_entries = source.order_by('entry').values('entry').distinct()
				target = Term.objects.filter(entry__in = source_entries, language=targetlanguage)[:hits]
			if not target and start:
				print("istart")
				source = Term.objects.filter(lowvalue__startswith=search, language=sourcelanguage, termbase__name__in=selectedtermbases)
				source_entries = source.order_by('entry').values('entry').distinct()
				target = Term.objects.filter(entry__in = source_entries, language=targetlanguage)[:hits]	
			print('START1',time.time())	
			if not target:
				if stem:
					print("STEM")
					svector=SearchQuery(search, config='english')
					#pvector=plainto_tsquery
					source = Term.objects.annotate(search=SearchVector('lowvalue', config='english')).filter(search=svector, language=sourcelanguage, termbase__name__in=selectedtermbases)
				else:
					print("NOSTEM ************************************")
					#source = Term.objects.annotate(search=SearchVector('lowvalue', config='english')).filter(search=search, language=sourcelanguage, termbase__name__in=selectedtermbases)
					source = Term.objects.filter(lowvalue__contains=search, language=sourcelanguage, termbase__name__in=selectedtermbases)
				source_entries = source.order_by('entry').values('entry').distinct()
				target = Term.objects.filter(entry__in = source_entries, language=targetlanguage)[:hits]
				
			print('START2',time.time())	
			targetlength = 'Target terms found: '+str(target.count())
			#counts='Liczba terminów: '+str(Term.objects.all().count())
			tooshort = False
			allTBX = target_array(source, target, myuser, False, search)
			print('START3: ',time.time())
			print(targetlength)
			context = {
			'too_short': tooshort,
			'has_permission': True,
			'termbases': termResult,
			'selectedtermbases': selectedtermbases,
			'results': allTBX,			
			'sourcelanguage':sourcelanguagename,
			'targetlanguage':targetlanguagename,
			'targetlength': targetlength,
			'hits': hitstext,
			#'user': myuser,
			}
			#print("uuaa", context)
			html = render_to_string('glos/search.html', context)
			
			#print("a")
			return HttpResponse(html)
		else:
			tooshort=True
			context = {
			'too_short': tooshort,
			'has_permission': True,	
			}
			html = render_to_string('glos/search.html', context)
			#print(html)
			return HttpResponse(html)

@api_view(['POST'])
@csrf_exempt
@permission_classes([IsAuthenticated, ])
def term_list(request):
	myuser = request.user
	queryset = User.objects.none()  
	if request.method == 'POST':
		data = JSONParser().parse(request)
		search=data["search"]
		print(search)
		print(data["selectedTermbases"])
		print("BIGSTART",time.time());
		sourcelanguagename = Language.objects.filter(name=data["index"])[0]
		targetlanguagename = Language.objects.filter(name=data["target"])[0]
		print(sourcelanguagename, targetlanguagename)
		if data["mode"]=="Normal":
			print("NORMAL")		
			source = Term.objects.filter(lowvalue__exact=search, language=sourcelanguagename, termbase__name__in=data["selectedTermbases"])
			source_entries = source.order_by('entry').values('entry').distinct()
			target = Term.objects.filter(entry__in = source_entries, language=targetlanguagename)[:10]
		else:
			source = Term.objects.filter(lowvalue__in=search, language=sourcelanguagename, termbase__name__in=data["selectedTermbases"])
			source_entries = source.order_by('entry').values('entry').distinct()
			target = Term.objects.filter(entry__in = source_entries, language=targetlanguagename)[:10]
			
		allTBX = target_array(source, target, myuser, True, search)
		print("ALL",time.time());
		print("LANGS",sourcelanguagename, targetlanguagename)
		serializer = TermbaseResultsSerializer(allTBX, many=True)
		printTBX(allTBX)
		return JsonResponse(serializer.data, safe=False)
		

@api_view(['GET'])
@csrf_exempt
@permission_classes([IsAuthenticated, ])
def user_termbase_list(request):
	ruser = request.user
	termResult=UserTermbase.objects.filter(user=ruser)
	serializer = UserTermbaseSerial(termResult, many=True)
	return JsonResponse(serializer.data, safe=False)

@api_view(['POST'])
@csrf_exempt
@permission_classes([IsAuthenticated, ])
def termbase_create(request):
	serializer = TermbaseSerializer(data=request.data)
	if serializer.is_valid():
		serializer.save()
		serializer2 = UserTermbaseSerial(data=request.data)
		print(request.data)
		if not serializer2.is_valid():
			print(serializer2.errors)
		else:
			serializer2.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
	return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@csrf_exempt
@permission_classes([IsAuthenticated, ])
def term_create(request):
	data = JSONParser().parse(request)
	#print(data)
	#counter=0
	print("Start database",time.time())
	for batch in data:
	#	print(batch)
		processentry(batch, request.user, 'NORMAL')
	respond =  {'name': 'OK'}
	print("End database",time.time())
	return Response(respond, status=status.HTTP_201_CREATED)
	
@api_view(['POST'])
@csrf_exempt
@permission_classes([IsAuthenticated, ])
def term_create_merge(request):
	data = JSONParser().parse(request)
	#print(data)
	#counter=0
	print("Start database",time.time())
	for batch in data:
	#	print(batch)
		processentry(batch, request.user, 'MERGE')
	respond =  {'name': 'OK'}
	print("End database",time.time())
	return Response(respond, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@csrf_exempt
@permission_classes([IsAuthenticated, ])
def language_create(request):
    data = JSONParser().parse(request)
    print(data)
    serializer = LanguageSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@csrf_exempt
@permission_classes([IsAuthenticated, ])
def language_list(request):
	languages = Language.objects.all()
	serializer = LanguageSerializer(languages, many=True)
	return JsonResponse(serializer.data, safe=False)

@api_view(['GET'])
@csrf_exempt
@permission_classes([IsAuthenticated, ])
def dtype_update(request):
	descriptions = []
	alldescrip = Description.objects.all().values('type').distinct()
	for value in alldescrip:
		if value['type'] not in descriptions:
			descriptions.append(value['type'])
	for onedesc in descriptions:
		newedescrip, nd =Dtype.objects.get_or_create(type=onedesc)
		newedescrip.save
	respond =  {'name': 'OK'}
	return Response(respond, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@csrf_exempt
@permission_classes([IsAuthenticated, ])
def termbase_list(request):
	termbases = Termbase.objects.all()
	serializer = TermbaseSerializer(termbases, many=True)
	return JsonResponse(serializer.data, safe=False)
	
@api_view(['DELETE'])
@csrf_exempt
@permission_classes([IsAuthenticated, ])
def termbase(request):
	data = JSONParser().parse(request)
	try:
		termbase = Termbase.objects.get(name=data["name"])
	except Exception as e:
		return Response(status=status.HTTP_404_NOT_FOUND)
	serializer = TermbaseSerializer(termbase)
	termbase.delete()	
	return JsonResponse(serializer.data, safe=False)
	
def index(request):
	#token = Token.objects.get_or_create(user=request.user)
	#print (token)
		if request.user.is_authenticated:
			auten=True
			user = request.user
		else:
			auten=False
			user = User.objects.get(username='anonymous')
		descriptions = []
		#descriptions.append('all')
		if request.method == 'POST':
			form = NameForm(request.POST)
			form2 =Sourcelanguage(request.POST)
			form3 =Targetlanguage(request.POST)
			
			if form.is_valid():
				search = form.cleaned_data['searchTerm']
				if len(search)>=3:
					sourcelanguage = request.POST.get('source')
					targetlanguage = request.POST.get('target')
					print ('Search: |%s| |%s|' % (search, sourcelanguage))
					myuser=request.user
					if not request.user.is_authenticated:
						myuser = User.objects.get(username='anonymous')
					termResult=UserTermbase.objects.filter(user=myuser)
					sourcelanguagename = Language.objects.filter(pk=sourcelanguage)[0].name
					targetlanguagename = Language.objects.filter(pk=targetlanguage)[0].name
					selectedtermbases = request.POST.getlist('checks[]')
					seldescrip = request.POST.getlist('checks[]')
					print("SEL:",seldescrip)
					print('Selected',selectedtermbases)
					#print ('SELTERMBASES',selectedtermbases)
					# main DB query
					source = Term.objects.filter(value__iexact=search, language=sourcelanguage, termbase__name__in=selectedtermbases)
					source_entries = source.order_by('entry').values('entry').distinct()
					target = Term.objects.filter(entry__in = source_entries, language=targetlanguage)[:10]
					if not target:
						print("istart")
						source = Term.objects.filter(value__istartswith=search, language=sourcelanguage, termbase__name__in=selectedtermbases)
						source_entries = source.order_by('entry').values('entry').distinct()
						target = Term.objects.filter(entry__in = source_entries, language=targetlanguage)[:10]
					if not target:
						print("icontains")
						source = Term.objects.filter(value__icontains=search, language=sourcelanguage, termbase__name__in=selectedtermbases)
						source_entries = source.order_by('entry').values('entry').distinct()
						target = Term.objects.filter(entry__in = source_entries, language=targetlanguage)[:10]
						tooshort = False
						allTBX = target_array(source, target, myuser, search)
				else:
					tooshort=True
				context = {
					'too_short': tooshort,
					'has_permission': True,
					'termbases': termResult,
					'selectedtermbases': selectedtermbases,
					'results': allTBX,
					'form': form,
					'form2': form2,
					'form3': form3,
					'sourcelanguage':sourcelanguagename,
					'targetlanguage':targetlanguagename,
					'descriptions': descriptions,
					'seldescrip': seldescrip,
					'user': user,
					'auten': auten,
					#'counts': counts,
				}
				
			return render(request, 'glos/index.html', context)
		else:
			form=NameForm()
			#counts=[]
			alldescriptions=[]
			allLang = Language.objects.all()
			hits=Hits.objects.all()
			#for onelang in allLang:
			#	count = Term.objects.filter(language=onelang).count()
			#	print(onelang.name,count)
			#	counts.append(onelang.name+': '+str(count))
			#counts.append('TOTAL: '+str(Term.objects.all().count()))
			#alldescrip = Description.objects.all().values('type').distinct()
			alldescrip = Dtype.objects.all().values('type')
			for value in alldescrip:
				if value['type'] not in descriptions:
					descriptions.append(value['type'])
			#print(alldescriptions)
			
			#form = Termbases(user=request.user)
			form2 = Sourcelanguage(initial={'source': allLang[0]})
			form3 = Targetlanguage(initial={'target': allLang[1]})
			all = Hits.objects.filter(hit='100')[0]
			hitform = SearchHits(initial={'hit': all})
			selectedtermbases = []
			#descriptions = []
			seldescrip=[]
			#descriptions.append('all')
			myuser=request.user
			if not request.user.is_authenticated:
				myuser = User.objects.get(username='anonymous')
			termbasesResult=UserTermbase.objects.filter(user=myuser)
			
			for termb in termbasesResult:
				selectedtermbases.append(termb.termbase.name)
			for desc in descriptions:
				selectedtermbases.append(desc)
			#selectedtermbases = termbasesResult
			sourcelanguage = Language.objects.all()[0]
			targetlanguage = Language.objects.all()[1]
			#sourceall = Term.objects.filter(language=sourcelanguage, termbase__name__in=selectedtermbases)
			#source_entries_all = sourceall.order_by('entry').values('entry').distinct()
			#targetall = Term.objects.filter(entry__in = source_entries_all, language=targetlanguage).count()
			counts='Terminów razem: '+str(Term.objects.all().count())
			#counts='Liczba terminów: '+str(targetall)
			print ('chosen',selectedtermbases)
			context = {
				'has_permission': True,
				'termbases': termbasesResult,
				'selectedtermbases': selectedtermbases,
				'form': form,
				'form2': form2,
				'form3': form3,
				'hitform':hitform,
				'user': user,
				'counts': counts,
				'descriptions': descriptions,
				'fulltext':'full',
				'auten': auten,
				#'seldescrip': seldescrip,
			}
			return render(request, 'glos/index.html', context)
	#else:
		#return render(request, 'registration/login.html', {})
		#return HttpResponseRedirect('/accounts/login/')

class EntryForm(forms.Form):
	id = forms.CharField(widget=forms.Textarea(attrs={'cols': 16, 'rows': 1}), label='Term ID')
	value = forms.CharField(widget=forms.Textarea(attrs={'cols': 30, 'rows': 4}), label='Source term')
	termbase = forms.ModelChoiceField(queryset=Termbase.objects.all(), label='Termbase')
	language = forms.ModelChoiceField(queryset=Language.objects.all(), label='Language')
	creator = forms.ModelChoiceField(queryset=User.objects.all(), label='Creator')
	#datetime = forms.DateField(widget=forms.widgets.DateInput(format='%m/%d/%Y %H:%M:%S'))
	def save(self):
		#print('entry',entry)
		data = self.cleaned_data
		updated = Term.objects.get(id=data['id'])
		if not updated.value==data['value']:
			print('Entry:',updated.entry)
			print('ID',data['id'])
			updated.value = data['value']
			print('UP',data['value'])
			updated.save(update_fields=['value','updated'])

class EntryDescr(forms.Form):
	name=forms.CharField(widget=forms.Textarea(attrs={'cols': 30, 'rows': 1}), label='Description name')
	type=forms.CharField(widget=forms.Textarea(attrs={'cols': 30, 'rows': 1}), label='Description type')
	value=forms.CharField(widget=forms.Textarea(attrs={'cols': 30, 'rows': 5}), label='Description value')

def is_member(user):
    return user.groups.filter(name='Editor').exists()
    
@permission_classes([IsAuthenticated, ])
def editentry(request, entry_id):
	user=request.user
	if is_member(user):
		initials =[]
		updated =[]
		dinitials=[]
		forms = formset_factory(form=EntryForm, extra=0)
		dforms=formset_factory(form=EntryDescr, extra=1)
		term = Term.objects.filter(id=entry_id)
		entries = Term.objects.filter(entry=term[0].entry)
		for entry in entries:
				initial = {'value':entry.value, 
					'id':entry.id,
					'language':entry.language, 
					'termbase':entry.termbase, 
					'creator':entry.creator, 
					'datetime': entry.updated}
				initials.append(initial)
				updated.append({'updated':entry.updated.strftime("%Y-%m-%d %H:%M:%S"),
								'termbase': entry.termbase,
								'language': entry.language,
								'creator': entry.creator})
				termdescriptions=Description.objects.filter(term=entry, level=Description.ENTRY_LEVEL)
				for termdescription in termdescriptions:
					dinitial = {'name': termdescription.name,
								'type': termdescription.type,
								'value':termdescription.value}
					dinitials.append(dinitial)
					
		data ={
		#	'form-TOTAL_FORMS': '3',
		#	'form-INITIAL_FORMS': '3',
		#	'form-MAX_NUM_FORMS': '3',
		}
		
		if request.method == 'POST':
		# create a form instance and populate it with data from the request:
			print("POST:",request.POST)
			formset = forms(request.POST, data)
			dformset = dforms(request.POST, data)
			context = {
				'has_permission': True,
				'forms': formset,
				'dforms':dformset,
				'entry': term[0].entry,
				'updated': updated,
				}
			# check whether it's valid:
			if formset.is_valid():
				print("VALID")
				for form in formset:
					form.save()
				return render(request, 'glos/change_form.html', context)
			else:
				print(formset.errors)
				return render(request, 'glos/change_form.html', context)
		# if a GET (or any other method) we'll create a blank form
		else:
			
				#print('UHU:',updated)
			formset = forms(initial=initials)
			dformset = dforms(initial=dinitials)
			print('di',dinitials)
				#forms.append(form)
			context = {
				'has_permission': True,
				#'eno': eno,
				#'selectedtermbases': selectedtermbases,
				'forms': formset,
				'dforms':dformset,
				'entry': term[0].entry,
				'updated': updated,
		        
				}
			#print(dformset)
			return render(request, 'glos/change_form.html', context)
	else:
		return HttpResponse("The login data you supplied did not grant access to edit this item!")

    

def get_target_array(results2, sourcelanguagename, targetlanguagename, selectedtermbases, myuser):
	allTBX = []
	langs = Term.objects.all().order_by().values('language').distinct()   #  all distinct languages of entry (index+target)
	#all = Term.objects.filter(entry__in = results2, termbase__name__in=selectedtermbases)
	all = Term.objects.filter(entry__in = results2)
	for term in all:
		if (('{}'.format(sourcelanguagename)=='{}'.format(term.language.name)) or ('{}'.format(targetlanguagename)=='{}'.format(term.language.name))):
			alldescrips = Description.objects.filter(term=term)
			#Check if termbase exists in results
			termbase=[termbasename for termbasename in allTBX if term.termbase == termbasename.name]
			#If not create new, check user access and set access
			if not termbase:
				termbase = TermBase()		
				allTBX.append(termbase)			
			else:
				#if exists get it
				termbase=termbase[0]
			termbase.name=term.termbase
			
			print(term.termbase)
			if not hasattr(termbase, 'entries'):
				entries = []
				termbase.entries=entries
			entry=[entryid for entryid in termbase.entries if term.entry == entryid.id]	
			if not entry:
				entry = TbxItem()  
				entry.istarget = False    # necessary?#########################
				termbase.entries.append(entry)
			else:
				entry = entry[0]
				
			entry.termbase = term.termbase
			print(term.entry)
			if myuser == User.objects.get(username='anonymous'):
				myuser = User.objects.get(username='anon')
			#print('MYUSER',myuser)
			termResult=UserTermbase.objects.filter(user=myuser)
			#print('termresult',termResult)
			termbase.access=False
			for item in termResult:
				if item.termbase==entry.termbase:
					termbase.access=True
			
		#	entry.descripGrp.append(alldescrips.filter(level=Description.ENTRY_LEVEL))  # wazna zmiana!!!!!!!!!!!!!!!!!
			entry.descripGrp = alldescrips.filter(level=Description.ENTRY_LEVEL)
			if not hasattr(entry, 'languages'):
				languages = []
				entry.languages=languages
				#print('create languages')
			language = [langid for langid in entry.languages if term.language==langid.lang]
		
			if not language:
				language = LanguageItem()
				entry.languages.append(language)
				#print('create lang')
			else:
				language=language[0]
			
		
			print('LANGUAGE', term.language.name)
			
			#langindex = entry.languages.index(language)
			language.descripGrp = alldescrips.filter(level=Description.LANGUAGE_LEVEL)	
			language.lang = term.language	
			#print("lang1",language.lang)
			if not hasattr(language, 'termGrp'):
				termGrp =[]  #  termgroup array
			else:
				termGrp=language.termGrp
			termgroup = TermGroup()  #  termgroup element
			entry.id = term.entry
			#print(sourcelanguagename, term.language.name,term.entry, term.value)
			#if sourcelanguagename==term.language.value:
			if '{}'.format(sourcelanguagename)=='{}'.format(term.language.name):
				entry.term = term.value
				print('Entry term:', entry.term)
			if '{}'.format(targetlanguagename)=='{}'.format(term.language.name):
				entry.istarget=True
				print('TARGET')
			alldescrips= Description.objects.filter(term=term)  #  descriptions for term
			
			termgroup.value = term.value
			termgroup.id = term.pk  #  id number of term
			termgroup.descripGrp = alldescrips.filter(level=Description.TERM_LEVEL)
			#print('termgrp', termGrp)
			termGrp.append(termgroup)
			language.termGrp = termGrp
		
	end=time.time()
	#print("Finish:",end)
	#print("Time:",end-start)
	print("***************************************")

	return allTBX
	
def target_array(source, target,  myuser, client, search):
	allTBX = []
	print('#', time.time())
	for term in target:
		alldescrips = Description.objects.filter(term=term)
		#Check if termbase exists in allTBX table
		termbase=[termbasename for termbasename in allTBX if term.termbase == termbasename.name]
		#If not create new
		if not termbase:
			termbase = TermBase()
			#add termbase name 
			termbase.name=term.termbase
			termbase.description=Termbase.objects.filter(name=term.termbase)[0].description
			#print('DECSRIPTION:', termbase.description)
			#add entries space
			entries = []
			termbase.entries=entries	
			#and add to allTBX table	
			allTBX.append(termbase)	
			# Set termbase access
			if myuser == User.objects.get(username='anonymous'):
					myuser = User.objects.get(username='anon')
			termbaseResult=UserTermbase.objects.filter(user=myuser)
			termbase.access=False
			for item in termbaseResult:
				if item.termbase==term.termbase:
					termbase.access=True		
			######################					
		else:
			#if exists get it
			termbase=termbase[0]
			
		entry=[entryid for entryid in termbase.entries if term.entry == entryid.id]	
		if not entry:
			entry = TbxItem()  
			termbase.entries.append(entry)
			entry.id = term.entry
			languages = []
			entry.languages=languages
			for sourceterm in source:
				if sourceterm.entry==term.entry:
					alldescripssource = Description.objects.filter(term=sourceterm)
					processlanguage(entry, sourceterm, alldescripssource, client, search, True)
					entry.term=sourceterm.value
		else:
			entry = entry[0]
		entry.istarget=True
		#########################################################################################
		#entry.term = term.value
		processlanguage(entry, term, alldescrips, client, search, False)
		
	#end=time.time()
	#printTBX(allTBX)
	return allTBX
	
def processlanguage(entry, term, alldescrips, client, search, highlight):
	#entry.descripGrp = alldescrips.filter(level=Description.ENTRY_LEVEL)
	entry.descripGrp = CNEdescrip(alldescrips, client)
	#print(entry.descripGrp)
	language = [langid for langid in entry.languages if term.language==langid.lang]
	if not language:
		language = LanguageItem()
		entry.languages.append(language)
	else:
		language=language[0]
	language.descripGrp = alldescrips.filter(level=Description.LANGUAGE_LEVEL)	
	language.lang = term.language  
	if not hasattr(language, 'termGrp'):
		termGrp =[]  #  termgroup array
	else:
		termGrp=language.termGrp
	termgroup = TermGroup()  #  termgroup element
	#print(search, client)
	if client or not highlight:
		termgroup.value = term.value
	else:
		termgroup.value = term.value
		test = re.findall(search, term.value, flags=re.IGNORECASE)
		#print(test)
		for ones in test:
			termgroup.value = term.value.replace(ones, '<span style="color: red;">'+ones+'</span>')
			
				
			#print('REPLACE',termgroup.value)

	#termgroup.value = term.value
#	print("Term value", term.value)
	termgroup.id = term.pk  #  id number of term
	
	termgroup.descripGrp = alldescrips.filter(level=Description.TERM_LEVEL)
	
	termGrp.append(termgroup)
	language.termGrp = termGrp
	
def CNEdescrip_old(alldescrips, client):
	all = alldescrips.filter(level=Description.ENTRY_LEVEL)
	#print(all)
	
	list = {'ModifiedDate': '', 'ModifiedBy': '', 'Tenant': '', 'Project': '', 'ResID':''}
	for onedesc in all:
	#	print(onedesc.value)
	#	print(list[onedesc.name])
		if onedesc.value not in list[onedesc.name]:
			if list[onedesc.name]=='':
				list[onedesc.name] = onedesc.value
			else:
				if client:
					list[onedesc.name] = list[onedesc.name]+'///'+onedesc.value
				else:
					list[onedesc.name] = list[onedesc.name]+'<span style="color: red;">///</span>'+onedesc.value
	alllist=[]
	for key, value in list.items():
		onedesc=DescriptionItem()
		onedesc.type = key
		onedesc.name = key
		onedesc.value = value
		alllist.append(onedesc)
	
	#print('WYNIK',alllist)
	return alllist
def CNEdescrip(alldescrips, client):
	all = alldescrips.filter(level=Description.ENTRY_LEVEL)
	
	list = {}
	for onedesc in all:
	#	print(onedesc.value)
		#print(list[onedesc.name])
		if not onedesc.name in list:
			list[onedesc.name]=""
		if onedesc.value not in list[onedesc.name]:
			if list[onedesc.name]=='':
				list[onedesc.name] = onedesc.value
			else:
				if client:
					list[onedesc.name] = list[onedesc.name]+'///'+onedesc.value
				else:
					list[onedesc.name] = list[onedesc.name]+'<span style="color: red;">///</span>'+onedesc.value
	alllist=[]
	for key, value in list.items():
		onedesc=DescriptionItem()
		onedesc.type = key
		onedesc.name = key
		onedesc.value = value
		alllist.append(onedesc)
	
	#print('WYNIK',alllist)
	return alllist
def printTBX(allTBX):
	for termbase in allTBX:
		print('Termbase name', termbase.name)
		for tbxitem in termbase.entries:
			print('     Term', tbxitem.term)
			for lang in tbxitem.languages:
				print('         Language', lang.lang)
				for termgroup in lang.termGrp:
					print('             Term',termgroup.value)
def alldesc(allTBX):
	all=[]
	for termbase in allTBX:
		for tbxitem in termbase.entries:
			for desc in tbxitem.descripGrp:
				if desc.type not in all:
					all.append(desc.type)
			for lang in tbxitem.languages:
				for desc in lang.descripGrp:
					if desc.type not in all:
						all.append(desc.type)
				for termgroup in lang.termGrp:
					for desc in termgroup.descripGrp:
						if desc.type not in all:
							all.append(desc.type)
	return all
					
def processdescription(newterm, descrip, level, entry):
	newedescrip, nd =Description.objects.get_or_create(term=newterm, name=descrip['name'] , type=descrip['type'], value=descrip['value'], level=level, entry=entry)
	newedescrip.save

def checktodelete(entryID, entry):
	
	term = Term.objects.filter(entry=entryID)
	#print(id_exists)
	desc= []
	if term:
		desc = Description.objects.filter(term=term[0], level=Description.ENTRY_LEVEL, entry=entry)
	if not desc:
		desc = Description.objects.filter(level=Description.ENTRY_LEVEL, entry=entry)
		#print('UWAGA',desc, entry)
		if desc:
			term=desc[0].term
			#print('TERM:',term)
			desc.delete()
			desc = Description.objects.filter(term=term)
			if not desc:
				Term.objects.filter(entry=term.entry).delete()
				#Term.objects.filter(pk=term.id).delete()
			
							
def processentry(entry, user, type):	
	ts=entry['termbase']
	termb=Termbase.objects.filter(name=ts)[0]
	if type=='MERGE':
		#entryID = "|"+str(termb.pk)+entry['ID']+"|"
		entryID = "|"+str(termb.pk)+"|"
		for lang in entry['languages']:		
			languageid=None
			slang=lang['lang'][0]+lang['lang'][1]
			#print('1',slang)
			languageid = Language.objects.filter(name=slang.upper())
			if languageid:
				languageid=languageid[0]
				for term in lang['termGrp']:
					value =  term['value']
					entryID=entryID+value+"|"
		checktodelete(entryID, entry['ID'])
	else:
		entryID = 10000000*termb.pk+int(entry['ID'])
	#print("ID:", entryID)
	
	for lang in entry['languages']:		
		languageid=None
		slang=lang['lang'][0]+lang['lang'][1]
		#print('1',slang)
		languageid = Language.objects.filter(name=slang.upper())
		if languageid:
			languageid=languageid[0]
			for term in lang['termGrp']:
				value =  term['value']
				lowvalue=value.lower()
				if lowvalue.endswith('.'):
					lowvalue=lowvalue[:-1]
				
				newterm, nt = Term.objects.get_or_create(entry = entryID, termbase=termb, language=languageid, value=value, lowvalue=lowvalue, creator=user)
				newterm.save
				for tdescrip in term['descripGrp']:
					processdescription(newterm, tdescrip, Description.TERM_LEVEL, entry['ID'])
				for descrip in lang['descripGrp']:
					processdescription(newterm, descrip, Description.LANGUAGE_LEVEL, entry['ID'])
				for edescrip in entry['descripGrp']:
					processdescription(newterm, edescrip, Description.ENTRY_LEVEL, entry['ID'])
				
				
def processdescription_old(newterm, descrip, level):
	newedescrip = Description.objects.filter(term=newterm, name=descrip['name'] , type=descrip['type'], level=level)
	if newedescrip:
		#print("IS",newedescrip)
		if not descrip['value'] in newedescrip[0].value:
			newvalue=newedescrip[0].value+"|"+descrip['value']
			newedescrip, ned = Description.objects.update_or_create(term=newterm, name=descrip['name'] , type=descrip['type'], level=level, defaults={"value": newvalue})
			newedescrip.save
	else:
		newedescrip, ned=Description.objects.get_or_create(term=newterm, name=descrip['name'] , type=descrip['type'], value=descrip['value'], level=level)
		newedescrip.save
		
def checktodelete_old(entryID, entry):
	id_exists = Term.objects.filter(entry=entryID)
	if len(id_exists)==0:
		#nowy termin, sprawdzic czy nie aktualizacja starego (nowe tlumaczenie)
		#terms = Terms.objects.filter(Q(entry____contains=5000) | Q(entry____contains=True))
		for edescrip in entry['descripGrp']:
			if edescrip['name']=='ResID':
				resid=edescrip['value']
			if edescrip['name']=='Tenant':
				tenant=edescrip['value']
			if edescrip['name']=='Project':
				project=edescrip['value']
		if resid:
			delete=False
			isresids = Description.objects.filter(name='ResID', type='ResID', value__contains=resid,  level=Description.ENTRY_LEVEL)
			print(resid)
			terms=[]
			if len(isresids)>0:
				for isresid in isresids:
					print(isresid.term.value)
					terms.append(isresid.term)
				print(terms)
				istenants = Description.objects.filter(term__in = terms, name='Tenant', type='Tenant', value__contains=tenant,  level=Description.ENTRY_LEVEL)
				
				print(istenants)
				terms=[]
				if len(istenants)>0:
					for istenant in istenants:
						print(istenant.term.value)
						terms.append(istenant.term)
					print(terms)
					isprojects = Description.objects.filter(term__in = terms, name='Project', type='Project', value__contains=project,  level=Description.ENTRY_LEVEL)
					print(isprojects)
					for isproject in isprojects:
						_resid= Description.objects.filter(term = isproject.term, name='Project', type='Project', value__contains=project,  level=Description.ENTRY_LEVEL)
						isproject.term.delete()
						print("deleted")
						
"""
FULLTEXT
#elem=
				#print('stem',stem(search))
				#source = Term.objects.filter(lowvalue__contains=search, language=sourcelanguage, termbase__name__in=selectedtermbases)
				source = Term.objects.annotate(search=SearchVector('lowvalue', config='english')).filter(search=svector, language=sourcelanguage, termbase__name__in=selectedtermbases)
				#source = Term.objects.filter(lowvalue__search=search, language=sourcelanguage, termbase__name__in=selectedtermbases)
				source_entries = source.order_by('entry').values('entry').distinct()
				target = Term.objects.filter(entry__in = source_entries, language=targetlanguage)[:hits]
				
				
				#results3 = Term.objects.annotate(search=SearchVector('value', config='english')).
				filter(search=SearchQuery(data["search"], config='english'), language=sourcelanguagename, termbase__name__in=data["selectedTermbases"]).
				order_by('entry').values('entry').distinct()
				
			#restest = Term.objects.annotate(search=SearchVector('value', config='english'))
			#Post.objects.annotate(search=SearchVector('body', config='german')).filter
			
"""