from django.shortcuts import render
from django import forms
from django.forms import formset_factory, modelformset_factory
from django.http import HttpResponse, JsonResponse
from django.template import loader
from .models import Termbase, UserTermbase, Term, Language, Description
from .forms import NameForm, DocumentForm, Termbases, Sourcelanguage, Targetlanguage
from .serializers import TermSerializer, TermbaseSerializer
from django.contrib.auth import authenticate, login
from django.db.models import Q
from django.contrib import admin
from django.conf.urls import url
from channels import Channel, Group
from channels.sessions import channel_session
import json
import os
from rest_framework import viewsets
from glos.serializers import UserSerializer, GroupSerializer, UserTermbaseSerializer, TermbaseSerializer, LanguageSerializer, ResultsSerializer, UserTermbaseSerial
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
	
@api_view(['POST'])
#@permission_classes([DjangoModelPermissions, ])
@csrf_exempt
@permission_classes([IsAuthenticated, ])
def term_list_old(request):
	print(request.user)
	queryset = User.objects.none()  
	#if request.user.is_authenticated: 
	if request.method == 'POST':
		data = JSONParser().parse(request)
		print(data["search"])
		print(data["selectedTermbases"])
		print("BIGSTART",time.time());
		sourcelanguagename = Language.objects.filter(value=data["index"])[0]
		if data["mode"]=="Standard":		
			#results = Term.objects.filter(value__istartswith=data["search"], language=sourcelanguagename, termbase__termbase_name__in=data["selectedTermbases"])[:10]
			#results2 = Term.objects.filter(value__istartswith=data["search"], language=sourcelanguagename, termbase__termbase_name__in=data["selectedTermbases"]).order_by('entry').values('entry').distinct()[:2]
			results2 = Term.objects.filter(value=data["search"], language=sourcelanguagename, termbase__termbase_name__in=data["selectedTermbases"]).order_by('entry').values('entry').distinct()[:3]
		else:
			#results = Term.objects.filter(value__icontains=data["search"], language=sourcelanguagename, termbase__termbase_name__in=data["selectedTermbases"])[:10]
			results2 = Term.objects.filter(value__icontains=data["search"], language=sourcelanguagename, termbase__termbase_name__in=data["selectedTermbases"]).order_by('entry').values('entry').distinct()[:2]
		print("results2",results2)
		#results = Term.objects.filter(entry__in=results2)
		print("BIGEND",time.time());
		allTBX = get_target_array(results2, sourcelanguagename, data["selectedTermbases"])
		print("ALL",time.time());
		#snippets = Term.objects.filter(value__istartswith=data["search"])		 list(Owner.objects.filter(fill_name="Scott Lobdell").values_list("id", flat=True))
		#serializer = TermSerializer(snippets, many=True)
		serializer = ResultsSerializer(allTBX, many=True)
		
		return JsonResponse(serializer.data, safe=False)
	#else:
		#JsonResponse(serializer.data, safe=False)
		
@api_view(['POST'])
@csrf_exempt
@permission_classes([IsAuthenticated, ])
def term_list(request):
	print(request.user)
	#print(request)
	queryset = User.objects.none()  
	if request.method == 'POST':
		data = JSONParser().parse(request)
		print(data["search"])
		print(data["selectedTermbases"])
		print("BIGSTART",time.time());
		sourcelanguagename = Language.objects.filter(value=data["index"])[0]
		#test =["information", "database"]
		if data["mode"]=="Standard":		
			#results2 = Term.objects.filter(value__in=data["search"], language=sourcelanguagename, termbase__termbase_name__in=data["selectedTermbases"]).order_by('entry').values('entry').distinct()[:10]
			results2 = Term.objects.filter(value__in=data["search"], language=sourcelanguagename, termbase__termbase_name__in=data["selectedTermbases"]).order_by('entry').values('entry').distinct()[:10]
		else:
			results2 = Term.objects.filter(value__icontains=data["search"], language=sourcelanguagename, termbase__termbase_name__in=data["selectedTermbases"]).order_by('entry').values('entry').distinct()[:2]
		print("results2",results2)
		print("BIGEND",time.time());
		allTBX = get_target_array(results2, sourcelanguagename, data["selectedTermbases"])
		print("ALL",time.time());
		serializer = ResultsSerializer(allTBX, many=True)
		
		return JsonResponse(serializer.data, safe=False)
	
@api_view(['POST'])
@csrf_exempt
@permission_classes([IsAuthenticated, ])
def user_termbase_list(request):
	ruser = request.user
	#queryset = User.objects.none()  
	#termResult=UserTermbase.objects.filter(user=ruser).values('termbase')
	termResult=UserTermbase.objects.filter(user=ruser)
	#if request.method == 'POST':
	serializer = UserTermbaseSerial(termResult, many=True)
	print(serializer.data)
	#return JsonResponse(data)
	return JsonResponse(serializer.data, safe=False)
	#else:
		#JsonResponse(serializer.data, safe=False)

@api_view(['POST'])
@csrf_exempt
@permission_classes([IsAuthenticated, ])
def termbase_create(request):
	#data = JSONParser().parse(request)
	print("start")
	serializer = TermbaseSerializer(data=request.data)
	if serializer.is_valid():
		serializer.save()
		print("Termbase saved")
		serializer2 = UserTermbaseSerial(data=request.data)
		print(request.data)
		if not serializer2.is_valid():
			print(serializer2.errors)
		else:
			#print(serializer2.data)
			serializer2.save()
			print("UserTermbase saved")
			return Response(serializer.data, status=status.HTTP_201_CREATED)
	return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@csrf_exempt
@permission_classes([IsAuthenticated, ])
def term_create(request):
	data = JSONParser().parse(request)
	print(data)
	counter=0
	for batch in data:
		processentry(batch, counter, request.user)
	respond =  "{\"created\": \"OK\"}"
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
        print("Language saved")
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
		termbase = Termbase.objects.get(termbase_name=data["termbase_name"])
	except Exception as e:
		return Response(status=status.HTTP_404_NOT_FOUND)
	serializer = TermbaseSerializer(termbase)
	termbase.delete()	
	return JsonResponse(serializer.data, safe=False)
	
@api_view(['DELETE'])
@csrf_exempt
@permission_classes([IsAuthenticated, ])
def termbase_new(request):
	data = JSONParser().parse(request)
	print(data)
	serializer = TermbaseSerializer(data=data)
	if serializer.is_valid():
		return JsonResponse(serializer.data, safe=False)
	else:
		return Response(status=status.HTTP_404_NOT_FOUND)
	
class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
# Create your views here.
#def index(request):
#	latest_question_list = Terms.objects.order_by('-sourceTerm')[:50]
	#    output = ', '.join([q.sourceTerm for q in latest_question_list])
#	context = {
#		'latest_question_list': latest_question_list,
#	}
#	return render(request, 'glos/index.html', context)


def index(request):
	#token = Token.objects.get_or_create(user=request.user)
	#print (token)
	if request.user.is_authenticated:
		if request.method == 'POST':
			form = NameForm(request.POST)
			form2 =Sourcelanguage(request.POST)
			form3 =Targetlanguage(request.POST)
			
			
			if form.is_valid():
				search = form.cleaned_data['searchTerm']
				sourcelanguage = request.POST.get('source')
				targetlanguage = request.POST.get('target')
				print ('Search: |%s| |%s|' % (search, sourcelanguage))
				myuser=request.user
				termResult=UserTermbase.objects.filter(user=myuser)
				sourcelanguagename = Language.objects.filter(pk=sourcelanguage)[0].value
				targetlanguagename = Language.objects.filter(pk=targetlanguage)[0].value
				selectedtermbases = request.POST.getlist('checks[]')
				
				# main DB query
				results2 = Term.objects.filter(value=search, language=sourcelanguage, termbase__termbase_name__in=selectedtermbases).order_by('entry').values('entry').distinct()[:10]
				#if not results:
				#results = Term.objects.filter(value__istartswith=search, language=sourcelanguage, termbase__termbase_name__in=selectedtermbases)[:10]
				if not results2:
					results2 = Term.objects.filter(value__istartswith=search, language=sourcelanguage, termbase__termbase_name__in=selectedtermbases).order_by('entry').values('entry').distinct()[:10]
				if not results2:
					#results = Term.objects.filter(value__icontains=search, language=sourcelanguage, termbase__termbase_name__in=selectedtermbases)[:10]
					results2 = Term.objects.filter(value__icontains=search, language=sourcelanguage, termbase__termbase_name__in=selectedtermbases).order_by('entry').values('entry').distinct()[:10]
				#print('CHOSEN: ',selectedtermbases)
				allTBX = []
				if len(search)>=3:
					tooshort = False
					allTBX = get_target_array(results2, sourcelanguagename, targetlanguagename, selectedtermbases)
				else:
					tooshort=True
				print('TOOSHORT: ',tooshort)
				print(sourcelanguagename)
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
				}
				
			return render(request, 'glos/index.html', context)
		else:
			form=NameForm()
			#form2 = Termbases(user=request.user)
			form2 = Sourcelanguage(initial={'source': Language.objects.all()[0]})
			form3 = Targetlanguage(initial={'target': Language.objects.all()[1]})
			myuser=request.user
			termbasesResult=UserTermbase.objects.filter(user=myuser)
			selectedtermbases = []
			for termb in termbasesResult:
				selectedtermbases.append(termb.termbase.termbase_name)
			#selectedtermbases = termbasesResult
			print ('chosen',selectedtermbases)
			context = {
				'has_permission': True,
				'termbases': termbasesResult,
				'selectedtermbases': selectedtermbases,
				'form': form,
				'form2': form2,
				'form3': form3,
			}
			return render(request, 'glos/index.html', context)
	else:
		return render(request, 'registration/login.html', {})
	


#def slownik(request, question_id):
#	return HttpResponse("Ogladasz termin %s." % question_id)

def slownik (request, question_id):
    if request.user.is_authenticated:
    	
        context = {
		     'Term':Terms.objects.get(pk=question_id),
	    }
        return HttpResponse(request.user.username)
        # return render(request, 'glos/detail.html', context)
    else:
    	return render(request, 'registration/login.html', {})
    	
def searchterm(request):
	# if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = NameForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            myuser=request.user
            if request.user.is_authenticated():

	            termbasesResult=UserTermbase.objects.filter(user=myuser).values('termbase')
	            results=Terms.objects.filter(sourceTerm__contains=form.cleaned_data['searchTerm']).filter(termbase__in=termbasesResult).exclude(targetTerm='')[:30]
            else:
            	#return HttpResponse('What? Are you kidding? Zaloguj sie glupolu')
            	#return render(request, 'glos/name.html', {'form': form})
            	return render(request, 'registration/login.html', {})
            context={
            	'results':results,
            	'form':form,
            }
            return render(request, 'glos/result.html', context)
       # if a GET (or any other method) we'll create a blank form
    else:
        form = NameForm()

    return render(request, 'glos/name.html', {'form': form })
    
class EditEntry(forms.Form):
	source = forms.CharField(label='Source term', max_length=100)
	#target = forms.CharField(label='Target term', max_length=100)
	
#class EntryForm(forms.ModelForm):
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

def editentry(request, entry_id):
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

	
	


def importpage(request):
	return render(request, 'glos/import.html', context)

def home(request):
    return render(request, 'index.htm', {'what':'Django File Upload'})
 
def upload(request):
    if request.method == 'POST':
        handle_uploaded_file(request.FILES['file'], str(request.FILES['file']))
        return HttpResponse("Successful")
 
    return HttpResponse("Failed")
 
def handle_uploaded_file(file, filename):
    if not os.path.exists('upload/'):
        os.mkdir('upload/')
 
    with open('upload/' + filename, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
            
def my_view(request):
    return HttpResponse("Hello!")
    
def get_target_array(results2, sourcelanguagename, targetlanguagename, selectedtermbases):
	allTBX = []
	langs = Term.objects.all().order_by().values('language').distinct()   #  all distinct languages of entry (index+target)
	all = Term.objects.filter(entry__in = results2, termbase__termbase_name__in=selectedtermbases)
	for term in all:
		alldescrips = Description.objects.filter(term=term)
		termbase=[termbasename for termbasename in allTBX if term.termbase == termbasename.name]
		if not termbase:
			termbase = TermBase()
			allTBX.append(termbase)			
		else:
			termbase=termbase[0]
		termbase.name=term.termbase
		if not hasattr(termbase, 'entries'):
			entries = []
			termbase.entries=entries
		
		entry=[entryid for entryid in termbase.entries if term.entry == entryid.id]	
		if not entry:
			entry = TbxItem()  
			entry.istarget = False
			termbase.entries.append(entry)
		else:
			entry = entry[0]
		#allindex = allTBX.index(entry)
		entry.termbase = term.termbase
	#	entry.descripGrp.append(alldescrips.filter(level=Description.ENTRY_LEVEL))  # wazna zmiana!!!!!!!!!!!!!!!!!
		entry.descripGrp = alldescrips.filter(level=Description.ENTRY_LEVEL)
		if not hasattr(entry, 'languages'):
			languages = []
			entry.languages=languages
			#print('create languages')
		language = [langid for langid in entry.languages if term.language==langid.lang]
		#print("lang1",language)
		if not language:
			language = LanguageItem()
			entry.languages.append(language)
			#print('create lang')
		else:
			language=language[0]
		#langindex = entry.languages.index(language)
		language.descripGrp = alldescrips.filter(level=Description.LANGUAGE_LEVEL)
		
		language.lang = term.language
		
		if not hasattr(language, 'termGrp'):
			termGrp =[]  #  termgroup array
		else:
			termGrp=language.termGrp
		termgroup = TermGroup()  #  termgroup element
		entry.id = term.entry
		print(term.language.value,term.entry, term.value)
		if sourcelanguagename==term.language.value:
			entry.term = term.value
		if targetlanguagename==term.language.value:
			entry.istarget=True
		alldescrips= Description.objects.filter(term=term)  #  descriptions for term
		termgroup.value = term.value  #  term
		termgroup.id = term.pk  #  id number of term
		termgroup.descripGrp = alldescrips.filter(level=Description.TERM_LEVEL)
		#print('termgrp', termGrp)
		termGrp.append(termgroup)
		language.termGrp = termGrp
		
	end=time.time()
	#print("Finish:",end)
	#print("Time:",end-start)
	#print(allTBX)
	return allTBX
	
def get_target_array_new2(results, results2):
	start=time.time()
	print("Start:",start)
	reallyall = Term.objects.filter(entry__in = results2) # all terms (source and target)
	allTBX = []
	#langs = list(Term.objects.all().order_by().values_list('language', flat=True).distinct())#  all distinct languages of entry (index+target)
	langs = Term.objects.all().order_by().values('language').distinct() # all languges
	#langs = reallyall.order_by().values('language').distinct()
	#print(langs)
	#print("1start:",start1)		all_animals = set(Animal.objects.all().values_list('name', flat=True))
	#for term in results:
	for term in reallyall:
		entry = TbxItem()  # entry element
		entry.termbase = term.termbase  #  termbase of entry
		tentry=term.entry  #  term entry id
		entry.term = term.value
		entry.id = tentry
		languageValue=term.language  #  language of term - search index language
		languages = []  #  languages array
		
		#langs = Term.objects.filter(entry=tentry).order_by().values('language').distinct()   #  all distinct languages of entry (index+target)
		#allterms=Term.objects.filter(entry=tentry)  #  all entry terms 
		#for ulang in langs:
		for ulang in langs:				
			language = LanguageItem()  #  language element
			ln=ulang.get('language')  #  one language (index or target)
			print(ln)
			alllangterms=Term.objects.filter(entry=tentry,language=ln)  #  all terms for this language !!!!!!!!?????????????????????????
			print(alllangterms)
			#alllangterms=allterms.filter(language=ln)  #  all terms for this language
			#print("LANGSTART",time.time())
			
			#print("LANGEND",time.time())
			termGroup =[]  #  termgroup array
			start1=time.time()
			for gterm in alllangterms:
			
				termgroup = TermGroup()  #  termgroup element
				termgroup.value = gterm.value  #  term
				print(termgroup.value)
				termgroup.id = gterm.pk  #  id number of term
				termgroup.descripGrp= Description.objects.filter(term=gterm, level=Description.TERM_LEVEL)  #  descriptions for term
				termGroup.append(termgroup)  #  add termgroup element to termgroup array
			language.lang = str(alllangterms[0].language)  #  language name
			end1=time.time()
			#print("1end:",end1)
			print("time:",end1-start1)
			language.termGrp = termGroup  #  termgroup array
			language.descripGrp=Description.objects.filter(term=alllangterms[0], level=Description.LANGUAGE_LEVEL)  #  descriptions for language
			print(language.descripGrp)
			languages.append(language)	#  adda language to languges array		
			
		entry.descripGrp = Description.objects.filter(term=term, level=Description.ENTRY_LEVEL)  #  descriptions for entry
		entry.languages = languages	 #  languages array
		allTBX.append(entry)  #  add entry element to all entries array
		
	end=time.time()
	print("Finish:",end)
	print("Time:",end-start)
	return allTBX

def get_target_array_new(results, results2):
	allTBX = []
	langs = Language.objects.all()
	for ids in results2:
		terms = results.filter(entry=ids.get('entry'))
		entry = TbxItem() 
		entry.id = ids.get('entry')
		entry.termbase = terms[0].termbase
		languages = []  #  languages array
		for lang in langs:
			language = LanguageItem()  #  language element
			alllangterms = terms.filter(language=lang)
			language.lang = lang
			termGroup =[]  #  termgroup array
			for gterm in alllangterms:
				termgroup = TermGroup()  #  termgroup element
				termgroup.value = gterm.value  #  term
				termgroup.id = gterm.pk  #  id number of term
				termGroup.append(termgroup)  #  add termgroup element to termgroup array
			language.termGrp = termGroup  #  termgroup array
			languages.append(language)	#  adda language to languges array
		entry.languages = languages	 #  languages array
		allTBX.append(entry)  #  add entry element to all entries array
	return allTBX
	
def processentry(entry,counter, user):	
	print(entry)	
	
	#source = Language.objects.filter(value="EN")[0]
	#target = Language.objects.filter(value="PL")[0]
	ts=entry['termbase']
	print(ts)	
	counter+= 1
	if (counter % 100) == 0:
		print('Imported: ',counter)
	termb=Termbase.objects.filter(termbase_name=ts)[0]
	for lang in entry['languages']:		
		languageid=None
		languageid = Language.objects.filter(value=lang['lang'].upper())[0]
		
		#if source.value.lower() in lang['lang'].lower(): 
		#	languageid=source
		#if target.value.lower() in lang['lang'].lower(): 
		#	languageid=target
		if languageid:
			isanylanguage=True
			print('LanguageID: ', languageid)
			print('EntryID: ',entry['ID'])
		
			for term in lang['termGrp']:
				print('Term: ',term['value'])
				newterm, nt = Term.objects.get_or_create(entry = entry['ID'], termbase=termb, language=languageid, value=term['value'], creator=user)
				newterm.save
				for tdescrip in term['descripGrp']:
					newedescrip, ned = Description.objects.get_or_create(term=newterm, name=tdescrip['name'] , type=tdescrip['type'], value=tdescrip['value'], level=Description.TERM_LEVEL)
					newedescrip.save
				for descrip in lang['descripGrp']:
					newedescrip, ned = Description.objects.get_or_create(term=newterm, name=descrip['name'] , type=descrip['type'], value=descrip['value'], level=Description.LANGUAGE_LEVEL)
					newedescrip.save
				for edescrip in entry['descripGrp']:
					newedescrip, ned = Description.objects.get_or_create(term=newterm, name=edescrip['name'] , type=edescrip['type'], value=edescrip['value'], level=Description.ENTRY_LEVEL)
					newedescrip.save	
	