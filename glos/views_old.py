from django.shortcuts import render
from django import forms
from django.forms import formset_factory, modelformset_factory
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.template import loader
from .models import Termbase, UserTermbase, Term, Language, Description
from .forms import NameForm, DocumentForm, Termbases, Sourcelanguage, Targetlanguage, ContactForm
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
	
def lspsoftware (request):
    return HttpResponseRedirect('http://www.lspsoftware.pl')
    
#def handler404(request):
#    return render(request, '404.html', status=404)


def emailform():
	form=ContactForm()
	context = {
			'has_permission': True,
			'form': form,
	}
	return context
	
def emailformOK(req):
	form=ContactForm(req.POST)
	if form.is_valid():
		name = form.cleaned_data['name']
		email = form.cleaned_data['email']
		message = form.cleaned_data['message']
		context = {
		'has_permission': True,
		'form': form,
		'OK': 'OK',
		}
		email = EmailMessage(name, message, to=[email])
		email.send()
		return context
			
def locstar (request):
	if request.method == 'POST':
		emailformOK(request)
		return render(request, 'glos/email.html', emailformOK(request))
	else:
		return render(request, 'glos/locstar.html', emailform())
def onas (request):
	if request.method == 'POST':
		emailformOK(request)
		return render(request, 'glos/email.html', emailformOK(request))
	else:
		return render(request, 'glos/onas.html', emailform())
def contact (request):
	if request.method == 'POST':
		emailformOK(request)
		return render(request, 'glos/email.html', emailformOK(request))
	else:
		return render(request, 'glos/contact.html', emailform())
def technologie (request):
	if request.method == 'POST':
		emailformOK(request)
		return render(request, 'glos/email.html', emailformOK(request))
	else:
		return render(request, 'glos/technologie.html', emailform())
def tm (request):
	if request.method == 'POST':
		emailformOK(request)
		return render(request, 'glos/email.html', emailformOK(request))
	else:
		return render(request, 'glos/tm.html', emailform())
def servicegrid (request):
	if request.method == 'POST':
		emailformOK(request)
		return render(request, 'glos/email.html', emailformOK(request))
	else:
		return render(request, 'glos/servicegrid.html', emailform())
def servicetl (request):
	if request.method == 'POST':
		emailformOK(request)
		return render(request, 'glos/email.html', emailformOK(request))
	else:
		return render(request, 'glos/servicetl.html', emailform())					
def terminology (request):
	if request.method == 'POST':
		emailformOK(request)
		return render(request, 'glos/email.html', emailformOK(request))
	else:
		return render(request, 'glos/terminology.html', emailform())		
def tools (request):
	if request.method == 'POST':
		emailformOK(request)
		return render(request, 'glos/email.html', emailformOK(request))
	else:
		return render(request, 'glos/tools.html', emailform())		
def mt (request):
	if request.method == 'POST':
		emailformOK(request)
		return render(request, 'glos/email.html', emailformOK(request))
	else:
		return render(request, 'glos/mt.html', emailform())		
def customers (request):
	if request.method == 'POST':
		emailformOK(request)
		return render(request, 'glos/email.html', emailformOK(request))
	else:
		return render(request, 'glos/customers.html', emailform())		
def translation (request):
	if request.method == 'POST':
		emailformOK(request)
		return render(request, 'glos/email.html', emailformOK(request))
	else:
		return render(request, 'glos/translation.html', emailform())		
def localization (request):
	if request.method == 'POST':
		emailformOK(request)
		return render(request, 'glos/email.html', emailformOK(request))
	else:
		return render(request, 'glos/localization.html', emailform())		
def website (request):
	if request.method == 'POST':
		emailformOK(request)
		return render(request, 'glos/email.html', emailformOK(request))
	else:
		return render(request, 'glos/website.html', emailform())		
def other (request):
	if request.method == 'POST':
		emailformOK(request)
		return render(request, 'glos/email.html', emailformOK(request))
	else:
		return render(request, 'glos/other.html', emailform())		

def create_post(request):
	if request.method == 'POST':
		search = request.POST.get('search')
		sourcelanguage = request.POST.get('source')
		targetlanguage = request.POST.get('target')
		myuser=request.user
		if not request.user.is_authenticated:
			myuser = User.objects.get(username='anonymous')
		termResult=UserTermbase.objects.filter(user=myuser)
		sourcelanguagename = Language.objects.filter(pk=sourcelanguage)[0].name
		targetlanguagename = Language.objects.filter(pk=targetlanguage)[0].name
		selectedtermbases = request.POST.getlist('selectedtermbases[]')	
		print('START',time.time())
		source = Term.objects.filter(value__iexact=search, language=sourcelanguage, termbase__name__in=selectedtermbases)
		
		source_entries = source.order_by('entry').values('entry').distinct()

		target = Term.objects.filter(entry__in = source_entries, language=targetlanguage)[:10]
		
		print('STARTST',time.time())	
		dl=len(target)
		print('STARTTG',time.time())	
		sl=len(source)
		print(sl)
		print('STARTTG2',time.time())	
		if dl==0:
			print("istart")
			source = Term.objects.filter(value__istartswith=search, language=sourcelanguage, termbase__name__in=selectedtermbases)
			source_entries = source.order_by('entry').values('entry').distinct()
			target = Term.objects.filter(entry__in = source_entries, language=targetlanguage)[:10]
			
		print('START1',time.time())	
		if not target:
			print("icontains")
			source = Term.objects.filter(value__icontains=search, language=sourcelanguage, termbase__name__in=selectedtermbases)
			source_entries = source.order_by('entry').values('entry').distinct()
			target = Term.objects.filter(entry__in = source_entries, language=targetlanguage)[:10]
		print('START2',time.time())	
		"""
		if not source:
			print('Ouch')
			target=[]
			source_entries = []
			"""
		#print('SOURCE',source[0].value)
		print('Start4',time.time())
		#target_entries = target.order_by('entry').values('entry').distinct()[:10]
		
		allTBX = []
		
		if len(search)>=3:
			tooshort = False
			allTBX = target_array(source, target, myuser)
		else:
			tooshort=True
		print('START3: ',time.time())
		print(sourcelanguagename)
		context = {
			'too_short': tooshort,
			'has_permission': True,
			'termbases': termResult,
			'selectedtermbases': selectedtermbases,
			'results': allTBX,
			
			'sourcelanguage':sourcelanguagename,
			'targetlanguage':targetlanguagename,
			#'user': myuser,
		}
		html = render_to_string('glos/search.html', context)
		return HttpResponse(html)

@api_view(['POST'])
@csrf_exempt
@permission_classes([IsAuthenticated, ])
def term_list(request):
	myuser = request.user
	queryset = User.objects.none()  
	if request.method == 'POST':
		data = JSONParser().parse(request)
		print(data["search"])
		print(data["selectedTermbases"])
		print("BIGSTART",time.time());
		sourcelanguagename = Language.objects.filter(name=data["index"])[0]
		targetlanguagename = Language.objects.filter(name=data["target"])[0]
		print(sourcelanguagename, targetlanguagename)
		if data["mode"]=="Normal":
			print("NORMAL")		
			source = Term.objects.filter(lowvalue__iexact=data["search"], language=sourcelanguagename, termbase__name__in=data["selectedTermbases"])
			source_entries = source.order_by('entry').values('entry').distinct()
			target = Term.objects.filter(entry__in = source_entries, language=targetlanguagename)[:10]
		else:
			source = Term.objects.filter(lowvalue__in=data["search"], language=sourcelanguagename, termbase__name__in=data["selectedTermbases"])
			source_entries = source.order_by('entry').values('entry').distinct()
			target = Term.objects.filter(entry__in = source_entries, language=targetlanguagename)
			
		allTBX = target_array(source, target, myuser)
		print("ALL",time.time());
		print("LANGS",sourcelanguagename, targetlanguagename)
		serializer = TermbaseResultsSerializer(allTBX, many=True)
		printTBX(allTBX)
		return JsonResponse(serializer.data, safe=False)
		
@api_view(['POST'])
@csrf_exempt
@permission_classes([IsAuthenticated, ])
def term_list_new(request):
	myuser = request.user
	queryset = User.objects.none()  
	if request.method == 'POST':
		data = JSONParser().parse(request)
		print(data["search"])
		print(data["selectedTermbases"])
		print("BIGSTART",time.time());
		sourcelanguagename = Language.objects.filter(name=data["index"])[0]
		targetlanguagename = Language.objects.filter(name=data["target"])[0]
		print(sourcelanguagename, targetlanguagename)
		if data["mode"]=="Normal":
			print("NORMAL")		
			source = Term.objects.filter(value__iexact=data["search"], language=sourcelanguagename, termbase__name__in=data["selectedTermbases"])
			source_entries = source.order_by('entry').values('entry').distinct()
			target = Term.objects.filter(entry__in = source_entries, language=targetlanguagename)[:10]
		else:
			source1 = Term.objects.filter(language=sourcelanguagename, termbase__name__in=data["selectedTermbases"])
			source = Term.objects.none()
			for d in data["search"]:
				print(d)
				source |= source1.filter(value__iexact=d)
			source_entries = source.order_by('entry').values('entry')
			target = Term.objects.filter(entry__in = source_entries, language=targetlanguagename)[:10]
		#for item in source:
		#	print item
		print("source",source)
		print("target",target)
		print("BIGEND",time.time());
		allTBX = target_array(source, target, myuser)
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
	#print(data)
	#counter=0
	print("Start database",time.time())
	for batch in data:
		processentry(batch, request.user)
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
		termbase = Termbase.objects.get(name=data["name"])
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
	
def index(request):
	#token = Token.objects.get_or_create(user=request.user)
	#print (token)
	#if request.user.is_authenticated:
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
				if not request.user.is_authenticated:
					myuser = User.objects.get(username='anonymous')
				termResult=UserTermbase.objects.filter(user=myuser)
					
				sourcelanguagename = Language.objects.filter(pk=sourcelanguage)[0].value
				targetlanguagename = Language.objects.filter(pk=targetlanguage)[0].value
				selectedtermbases = request.POST.getlist('checks[]')
				print ('SELTERMBASES',selectedtermbases)
				# main DB query
				results2 = Term.objects.filter(value=search, language=sourcelanguage).order_by('entry').values('entry').distinct()[:10]
				#if not results:
				#results = Term.objects.filter(value__istartswith=search, language=sourcelanguage, termbase__termbase_name__in=selectedtermbases)[:10]
				if not results2:
					results2 = Term.objects.filter(value__istartswith=search, language=sourcelanguage).order_by('entry').values('entry').distinct()[:10]
				if not results2:
					#results = Term.objects.filter(value__icontains=search, language=sourcelanguage, termbase__termbase_name__in=selectedtermbases)[:10]
					results2 = Term.objects.filter(value__icontains=search, language=sourcelanguage).order_by('entry').values('entry').distinct()[:10]
				#print('CHOSEN: ',selectedtermbases)
				allTBX = []
				if len(search)>=3:
					tooshort = False
					allTBX = get_target_array(results2, sourcelanguagename, targetlanguagename, selectedtermbases, myuser)
				else:
					tooshort=True
				print('TOOSHORT: ',tooshort)
				print(sourcelanguagename)
				#counts=[]
				allLang = Language.objects.all()
				#for onelang in allLang:
				#	count = Term.objects.filter(language=onelang).count()
				#	print(onelang.value,count)
				#	counts.append(onelang.value+': '+str(count))
				#counts.append('TOTAL: '+str(Term.objects.all().count()))
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
				#	'user': myuser,
				#	'counts': counts,
				}
				
			return render(request, 'glos/index.html', context)
		else:
			form=NameForm()
			#counts=[]
			allLang = Language.objects.all()
			#for onelang in allLang:
			#	count = Term.objects.filter(language=onelang).count()
			#	print(onelang.value,count)
			#	counts.append(onelang.value+': '+str(count))
			#counts.append('TOTAL: '+str(Term.objects.all().count()))
			#form = Termbases(user=request.user)
			form2 = Sourcelanguage(initial={'source': allLang[0]})
			form3 = Targetlanguage(initial={'target': allLang[1]})
			selectedtermbases = []
			myuser=request.user
			if not request.user.is_authenticated:
				myuser = User.objects.get(username='anonymous')
			termbasesResult=UserTermbase.objects.filter(user=myuser)
			for termb in termbasesResult:
				selectedtermbases.append(termb.termbase.name)
			#selectedtermbases = termbasesResult
			print ('chosen',selectedtermbases)
			context = {
				'has_permission': True,
				'termbases': termbasesResult,
				'selectedtermbases': selectedtermbases,
				'form': form,
				'form2': form2,
				'form3': form3,
			#	'user': myuser,
			#	'counts': counts,
			}
			return render(request, 'glos/index.html', context)
	#else:
		#return render(request, 'registration/login.html', {})
		#return HttpResponseRedirect('/accounts/login/')

    
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

    
def get_target_array_old(results2, sourcelanguagename, targetlanguagename, selectedtermbases, myuser):
	allTBX = []
	langs = Term.objects.all().order_by().values('language').distinct()   #  all distinct languages of entry (index+target)
	all = Term.objects.filter(entry__in = results2, termbase__name__in=selectedtermbases)
	#print(all)
	#ajax
	#all = Term.objects.filter(entry__in = results2)
	for term in all:
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
		entry.termbase = term.termbase
		
		if myuser == User.objects.get(username='anonymous'):
			myuser = User.objects.get(username='anon')
		#print('MYUSER',myuser)
		termResult=UserTermbase.objects.filter(user=myuser)
		#print('termresult',termResult)
		termbase.access=False
		for item in termResult:
			if item.termbase==entry.termbase:
				termbase.access=True
		
		#allindex = allTBX.index(entry)
		
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
	"""
	for terb in allTBX:
		notarget=True
		for entr in terb.entries:
			print("*")
			entrynotarget=True
			for lang in entr.languages:
				#print(targetlanguagename, lang.lang)
				#print('{} {}'.format(lang.lang,targetlanguagename))
				if '{}'.format(targetlanguagename)=='{}'.format(lang.lang):
					notarget=False
					entrynotarget=False
					print("Entry has target")
			if entrynotarget:
				terb.entries.remove(entr)
				print("removed",entr)
		print('Notarget', notarget)
		if notarget:
			 allTBX.remove(terb)
	"""		
	return allTBX
	
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
	"""
	for terb in allTBX:
		notarget=True
		for entr in terb.entries:
			print("*")
			entrynotarget=True
			for lang in entr.languages:
				#print(targetlanguagename, lang.lang)
				#print('{} {}'.format(lang.lang,targetlanguagename))
				if '{}'.format(targetlanguagename)=='{}'.format(lang.lang):
					notarget=False
					entrynotarget=False
					print("Entry has target")
			if entrynotarget:
				terb.entries.remove(entr)
				print("removed",entr)
		print('Notarget', notarget)
		if notarget:
			 allTBX.remove(terb)
	"""		
	return allTBX
	
def target_array(source, target,  myuser):
	print("NEW!!!!!!", myuser)
	allTBX = []
	if source:
		print('AHA1')
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
			print('DECSRIPTION:', termbase.description)
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
			#entry.descripGrp = alldescrips.filter(level=Description.ENTRY_LEVEL)
			#print(entry.descripGrp)
			entry.id = term.entry
			languages = []
			entry.languages=languages
			#print('#przed', time.time())
			for sourceterm in source:
				#print('po#', time.time())
				alldescripssource = Description.objects.filter(term=sourceterm)
				if sourceterm.entry==term.entry:
					processlanguage(entry, sourceterm, alldescripssource)
					entry.term=sourceterm.value
		else:
			entry = entry[0]
		entry.istarget=True
		
		##########################################################################################entry.term = term.value
		processlanguage(entry, term, alldescrips)
		
	end=time.time()
	#printTBX(allTBX)
	return allTBX
	
def processlanguage(entry, term, alldescrips):
	entry.descripGrp = alldescrips.filter(level=Description.ENTRY_LEVEL)
	print(entry.descripGrp)
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
	termgroup.value = term.value
	print("Term value", term.value)
	termgroup.id = term.pk  #  id number of term
	termgroup.descripGrp = alldescrips.filter(level=Description.TERM_LEVEL)
	termGrp.append(termgroup)
	language.termGrp = termGrp
	
		
def printTBX(allTBX):
	for termbase in allTBX:
		print('Termbase name', termbase.name)
		for tbxitem in termbase.entries:
			print('     Term', tbxitem.term)
			for lang in tbxitem.languages:
				print('         Language', lang.lang)
				for termgroup in lang.termGrp:
					print('             Term',termgroup.value)
				
def processdescription(newterm, descrip, level):
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

def processentry(entry, user):	
	ts=entry['termbase']
	termb=Termbase.objects.filter(name=ts)[0]
	entryID = 10000000*termb.pk+int(entry['ID'])
	print("ID:", entryID)
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
				#oldentry(entryID, languaueid, termb, value)		
				newterm, nt = Term.objects.get_or_create(entry = entryID, termbase=termb, language=languageid, value=value, lowvalue=lowvalue, creator=user)
				newterm.save
				for tdescrip in term['descripGrp']:
					processdescription(newterm, tdescrip, Description.TERM_LEVEL)
				for descrip in lang['descripGrp']:
					processdescription(newterm, descrip, Description.LANGUAGE_LEVEL)
				for edescrip in entry['descripGrp']:
					processdescription(newterm, edescrip, Description.ENTRY_LEVEL)
				
	
	
	


@api_view(['POST'])
@csrf_exempt
@permission_classes([IsAuthenticated, ])
def term_list_test(request):
	myuser = request.user
	queryset = User.objects.none()  
	if request.method == 'POST':
		data = JSONParser().parse(request)
		print(data["search"])
		print(data["selectedTermbases"])
		print("BIGSTART",time.time());
		sourcelanguagename = Language.objects.filter(name=data["index"])[0]
		targetlanguagename = Language.objects.filter(name=data["target"])[0]
		print(sourcelanguagename, targetlanguagename)
		if data["mode"]=="Normal":
			print("NORMAL")		
			source = Term.objects.filter(value__iexact=data["search"], language=sourcelanguagename, termbase__name__in=data["selectedTermbases"])
			source_entries = source.order_by('entry').values('entry').distinct()
			target = Term.objects.filter(entry__in = source_entries, language=targetlanguagename)[:10]
		else:
			source1 = Term.objects.filter(language=sourcelanguagename, termbase__name__in=data["selectedTermbases"])
			source = Term.objects.none()
			print (source1)
			allTBX=[]
			target = Term.objects.none()
			source = Term.objects.none()
			for d in data["search"]:
				print(d)
				#source |= source1.filter(value__iexact=d)
				source |= source1.filter(value__iexact=d)
				source_entries = source.order_by('entry').values('entry')
				target |= Term.objects.filter(entry__in = source_entries, language=targetlanguagename)
			#allTBXone = target_array(source, target, myuser)
			#allTBX=allTBX+allTBXone
			#print("BIGEND",time.time());
		allTBX = target_array(source, target, myuser)
		print("ALL",time.time());
		print("LANGS",sourcelanguagename, targetlanguagename)
		serializer = TermbaseResultsSerializer(allTBX, many=True)
		printTBX(allTBX)
		return JsonResponse(serializer.data, safe=False)
		
		
		
	#results2 = Term.objects.filter(value=data["search"], language=sourcelanguagename, termbase__name__in=data["selectedTermbases"]).order_by('entry').values('entry').distinct()[:10]
			#results3 = Term.objects.filter(value__iexact=data["search"], language=sourcelanguagename, termbase__name__in=data["selectedTermbases"]).order_by('entry').values('entry').distinct()
			#TEST   Author.objects.annotate(distance=TrigramDistance('name', test),).filter(distance__lte=0.7).order_by('distance')
			# similarity=TrigramSimilarity('name', test),).filter(similarity__gt=0.3).order_by('-similarity')
			#results3 = Term.objects.annotate(similarity=TrigramSimilarity('value', data["search"]),).filter(similarity__gt=0.7, language=sourcelanguagename, termbase__name__in=data["selectedTermbases"]).order_by('entry').values('entry').distinct()
				#results3 = Term.objects.annotate(search=SearchVector('value', config='english')).filter(search=SearchQuery(data["search"], config='english'), language=sourcelanguagename, termbase__name__in=data["selectedTermbases"]).order_by('entry').values('entry').distinct()
			#restest = Term.objects.annotate(search=SearchVector('value', config='english'))
			#Post.objects.annotate(search=SearchVector('body', config='german')).filter(search=SearchQuery('programmierung', config='german'))
			
			