from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template import loader
from .models import Termbase, UserTermbase, Term, Language, Description
from .forms import NameForm, DocumentForm, Termbases, Sourcelanguage
from .serializers import TermSerializer
from django.contrib.auth import authenticate, login
from django.db.models import Q
from django.contrib import admin
from django.conf.urls import url
from channels import Channel, Group
from channels.sessions import channel_session
import json
import os
from rest_framework import viewsets
from glos.serializers import UserSerializer, GroupSerializer
from django.contrib.auth.models import User, Group
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, DjangoModelPermissions
from rest_framework.response import Response



class DescriptionItem:
	pass
class TermGroup:
	pass
class LanguageItem:
	pass
class TbxItem:
	pass

@api_view(['POST'])
#@permission_classes([DjangoModelPermissions, ])
@csrf_exempt
@permission_classes([IsAuthenticated, ])
def term_list(request):
	print(request.user)
	queryset = User.objects.none()  
	#if request.user.is_authenticated: 
	if request.method == 'POST':
		
		data = JSONParser().parse(request)
		print(data["search"])
		snippets = Term.objects.filter(value__istartswith=data["search"])
		serializer = TermSerializer(snippets, many=True)
		#return JsonResponse(data)
		return JsonResponse(serializer.data, safe=False)
	#else:
		#JsonResponse(serializer.data, safe=False)



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

def index2(request):
	if request.method == 'POST':
		form = NameForm(request.POST)
		form2 = Termbases(request.POST, request=request)
		if form.is_valid():
			myuser=request.user
			termbasesResult=UserTermbase.objects.filter(user=myuser)
			termResult=UserTermbase.objects.filter(user=myuser).values('termbase')
			results=Terms.objects.filter(sourceTerm=form.cleaned_data['searchTerm']).filter(termbase__in=termResult).exclude(targetTerm='')[:10]
			context = {
				'has_permission': True,
				'termbases': termbasesResult,
				'results': results,
				'form': form,
				'form2': form2,
			}
		return render(request, 'glos/index.html', context)
	else:
		form=NameForm()
		myuser=request.user
		termbasesResult=UserTermbase.objects.filter(user=myuser)
		context = {
			'has_permission': True,
			'termbases': termbasesResult,
			'form': form,
		}
		return render(request, 'glos/index.html', context)
		

def index(request):
	#Group("chat-glos").send({
	#"text": "Komunikat",
	#})
	if request.user.is_authenticated:
		if request.method == 'POST':
			form = NameForm(request.POST)
			form2 =Sourcelanguage(request.POST)
			#form2 = Termbases(request.POST, user=request.user)
			#form2 = Termbases(request.POST,)
			
			if form.is_valid():
				search = form.cleaned_data['searchTerm']
				sourcelanguage = request.POST.get('source')
				print ('Search: |%s| |%s|' % (search, sourcelanguage))
				myuser=request.user
				termResult=UserTermbase.objects.filter(user=myuser)
				sourcelanguagename = Language.objects.filter(pk=sourcelanguage)[0].value
				selectedtermbases = request.POST.getlist('checks[]')
				
				# main DB query
				results = Term.objects.filter(value__iexact=search, language=sourcelanguage, termbase__termbase_name__in=selectedtermbases)[:10]
				if not results:
					results = Term.objects.filter(value__istartswith=search, language=sourcelanguage, termbase__termbase_name__in=selectedtermbases)[:10]
				#print('search count : ',results.count)
				if not results:
					results = Term.objects.filter(value__icontains=search, language=sourcelanguage, termbase__termbase_name__in=selectedtermbases)[:10]
				
				print('CHOSEN: ',selectedtermbases)
				allTBX = []
				if len(search)>=3:
					tooshort = False
					for term in results:
						print('Term: ',term.language)
						if term.termbase.termbase_name in selectedtermbases:
							#print('ID: ',termbase.termbase.id)
							print('TERMB',term.termbase.termbase_name)
							entry = TbxItem()
							entry.termbase = term.termbase
							tentry=term.entry
							entry.id = tentry
							languageValue=term.language
							print('Term language: ',languageValue) # search language
							#alllanguageterms=Term.objects.filter(entry=tentry) # all languages for entry
							#print ('alllanguageterms: ',alllanguageterms)
							#edescrips=EntryDescrip.objects.filter(entry=tentry)
							languages = []
							edescriptions = []
							langs = Term.objects.filter(entry=tentry).order_by().values('language').distinct()  
							print('test: ',langs)
							for ulang in langs:				
								language = LanguageItem()
								ln=ulang.get('language')
								print ('LANG: ',ln)
								alllangterms=Term.objects.filter(entry=tentry,language=ln)
								language.lang = str(alllangterms[0].language)
								#language.lang = Language.objects.filter(pk=ln)[0].value
								print('Langspacja?: |%s|' % language.lang)
								#language.termGrp = alllanguageterms.filter(language=lterm.language)
								
								termGroup =[]
								#for gterm in alllanguageterms.filter(language=lterm.language):
								for gterm in alllangterms:
									termgroup = TermGroup()
									termgroup.value = gterm.value
									termgroup.id = gterm.pk
									termgroup.descripGrp= Description.objects.filter(term=gterm, level=Description.TERM_LEVEL)
									termGroup.append(termgroup)
								
								language.termGrp = termGroup
								language.descripGrp=Description.objects.filter(term=alllangterms[0], level=Description.LANGUAGE_LEVEL)
								languages.append(language)			
							entry.descripGrp = Description.objects.filter(term=term, level=Description.ENTRY_LEVEL)
							entry.languages = languages	
							allTBX.append(entry)
				else:
					tooshort=True
				print('TOOSHORT: ',tooshort)
				context = {
					'too_short': tooshort,
					'has_permission': True,
					'termbases': termResult,
					'selectedtermbases': selectedtermbases,
					'results': allTBX,
					'form': form,
					'form2': form2,
					'sourcelanguage':sourcelanguagename,
				}
				
			return render(request, 'glos/index.html', context)
		else:
			form=NameForm()
			#form2 = Termbases(user=request.user)
			form2 = Sourcelanguage(initial={'source': Language.objects.all()[0]})
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

def editentry(request, entry_id):
	context = {
			'has_permission': True,
			#'termbases': termbasesResult,
			#'selectedtermbases': selectedtermbases,
			#'form': form,
			#'form2': form2,
	}
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

def get_target_array(results, selectedtermbases):
	allTBX = []
	for term in results:
		#if term.termbase.termbase_name in selectedtermbases:
		entry = TbxItem()  # entry element
		entry.termbase = term.termbase  #  termbase of entry
		tentry=term.entry  #  term entry id
		entry.id = tentry
		languageValue=term.language  #  language of term - search index language
		languages = []  #  languages array
		edescriptions = []  # descriptions array
		langs = Term.objects.filter(entry=tentry).order_by().values('language').distinct()   #  all distinct languages of entry (index+target)
		for ulang in langs:				
			language = LanguageItem()  #  language element
			ln=ulang.get('language')  #  one language (index or target)
			alllangterms=Term.objects.filter(entry=tentry,language=ln)  #  all terms for this language
			language.lang = str(alllangterms[0].language)  #  language name
			termGroup =[]  #  termgroup array
			for gterm in alllangterms:
				termgroup = TermGroup()  #  termgroup element
				termgroup.value = gterm.value  #  term
				termgroup.id = gterm.pk  #  id number of term
				termgroup.descripGrp= Description.objects.filter(term=gterm, level=Description.TERM_LEVEL)  #  descriptions for term
				termGroup.append(termgroup)  #  add termgroup element to termgroup array
			language.termGrp = termGroup  #  termgroup array
			language.descripGrp=Description.objects.filter(term=alllangterms[0], level=Description.LANGUAGE_LEVEL)  #  descriptions for language
			languages.append(language)	#  adda language to languges array		
		entry.descripGrp = Description.objects.filter(term=term, level=Description.ENTRY_LEVEL)  #  descriptions for entry
		entry.languages = languages	 #  languages array
		allTBX.append(entry)  #  add entry element to all entries array
		return allTBX

