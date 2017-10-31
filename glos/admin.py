from django.contrib import admin
from .models import Termbase, UserTermbase, Language, Term, Description, Hits
from django.utils.safestring import mark_safe
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.contrib.admin import helpers
from django.template.response import TemplateResponse
from django import forms
from django.shortcuts import render, render_to_response
from django.contrib.auth import authenticate, login
from django.template import Template, RequestContext
from .forms import DocumentForm
#from .tbx import parse
#from channels import Channel, Group
import os
from django.contrib.admin.views.main import ChangeList
from django.core import serializers
from django.contrib.admin import DateFieldListFilter
from django.contrib.auth.models import User
from django.conf.urls import *
from functools import update_wrapper

from django.db import connection

# Register your models here.

class UserInline(admin.TabularInline):
    model = UserTermbase
class TermbaseInline(admin.TabularInline):
    model = Termbase
class TermInline(admin.TabularInline):
	model = Term
class DescrInline(admin.TabularInline):
	model = Description

	

class TMPairAdmin(admin.ModelAdmin):
	#list_display = ('source','target',)
	actions = ['add_TM',]
	class InitTMForm(forms.Form):
		# mylaca nazwa - wstawia  zaznaczone pozycje (termbase name) do kodu html. aby wyslac je do pierwotnej strony
		# jest to wareunek ponownego wejscia w funkcje add_tag, w przeciwnym razie komunikat,ze nic nie zaznaczono
		_selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
		#Wstawia liste wyboru z UserTermbase
		#termbase = forms.ModelChoiceField(UserTermbase.objects)
		source = forms.ModelChoiceField(Language.objects, label='Source language')
		target = forms.ModelChoiceField(Language.objects, label='Target language')
		
	def add_TM(self, request, queryset):
		form = None
		selected_action = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
		#source = request.POST.get('source')
		#target = request.POST.get('target')
		source =queryset[0].source.name
		
		print ('ST: ', source)
		if len(selected_action)!=1:
			self.message_user(request, 'Select one TM to init!')
			return
		if 'cancel' in request.POST:
			self.message_user(request, 'TM Init canceled.')
			return
		if 'apply' in request.POST:
			print ('INIT')
			form = self.InitTMForm(request.POST)
			print('Formularz')
			if form.is_valid():
				cursor=connection.cursor()	
				sql="CREATE TABLE sources_%(slang)s (sid SERIAL PRIMARY KEY, text TEXT NOT NULL, vector TSVECTOR NOT NULL, length INTEGER NOT NULL);" % {'slang': source}
				print(sql)
				cursor.execute(sql)
				sql="CREATE UNIQUE INDEX sources_%(slang)s_text_unique_idx ON sources_%(slang)s (text);" % {'slang': source}
				cursor.execute(sql)
				sql="CREATE INDEX sources_%(slang)s_text_idx ON sources_%(slang)s USING gin(vector);" % {'slang': source}
				cursor.execute(sql)
				#cursor.execute("CREATE TABLE sources_%slang (sid SERIAL PRIMARY KEY, text TEXT NOT NULL, vector TSVECTOR NOT NULL, length INTEGER NOT NULL);" % {'slang': source})
				#db.execute("CREATE INDEX {table_name}_index_tsv ON {table_name} USING gin(to_tsvector('english', {column_name}));"
                  #cursor.execute("SELECT foo FROM bar WHERE baz = %s", [self.baz])
                  
                  #CREATE UNIQUE INDEX sources_%(slang)s_text_unique_idx ON sources_%(slang)s (text);
					#CREATE INDEX sources_%(slang)s_text_idx ON sources_%(slang)s USING gin(vector);
			else:
				print('Oooooops....')
			
#CREATE UNIQUE INDEX sources_%(slang)s_text_unique_idx ON sources_%(slang)s (text);
#CREATE INDEX sources_%(slang)s_text_idx ON sources_%(slang)s USING gin(vector);
#
				
			self.message_user(request, 'Init OK')
			return HttpResponseRedirect(request.get_full_path())
		if not form:
			#wstawia wybrane pozycje do html - patrz wyzej
			form = self.InitTMForm(initial={'_selected_action': selected_action, 'target': Language.objects.all()[1], 'source': Language.objects.all()[0]})
			#form2 = DocumentForm()
			return render(request, 'admin/init_TM.html', {'articles': queryset,													
														'tag_form': form,
														'path':request.get_full_path(),
														})														
	add_TM.short_description = "Init TM"
	
class TermAdmin(admin.ModelAdmin):
	#fields = ('value', )
	list_display = ('value','language','termbase', 'entry', 'added','updated','creator')
	#list_filter = ('language__entry__termbase','language__language')
	inlines = [DescrInline]
	list_filter = ('termbase','language', ('added', DateFieldListFilter))
	search_fields = ('value',)
	list_per_page = 800

class UserTermbaseAdmin(admin.ModelAdmin):
	
	# ktore pola beda wyswietlane w Admin
	# fields = ('user','termbase','read','write')
	list_display = ('user','termbase','read','write')

class TermbaseAdmin(admin.ModelAdmin):
	inlines = [UserInline]
	# ktore pola beda wyswietlane w Admin
	# fields = ('user','termbase','read','write')
	#def importpage(self, obj):
		# return mark_safe('<a class="addlink">'+str(obj.id)+'</a>')
		#return mark_safe('<a class="addlink" href="'+str(obj.id)+'">Import</a>')
		
	#importpage.short_description = 'Import'
	#importpage.allow_tags = True
	actions = ['make_published','export_selected_objects', 'add_tag', 'add_TM']
	
	list_display = ('name',)
	def make_published(self, request, queryset):
		# rows_updated = queryset.update(status='p')
		if request.POST.get('post'):
			if len(queryset) == 1:
				message_bit = "OK "
			else:
				message_bit = "Wybrano %s pozycji" % len(queryset)
				self.message_user(request, "%s test, nic nie zrobiono" % message_bit)
		else:
			context = {
				'title': 'Are you sure?',
				'queryset': queryset,
				'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
			}
			return TemplateResponse(request, '/export/',
				context, current_app=self.admin_site.name)
				
	def export_selected_objects(modeladmin, request, queryset):
		selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
		ct = ContentType.objects.get_for_model(queryset.model)
		return HttpResponseRedirect("/export/?ct=%s&ids=%s" % (ct.pk, ",".join(selected)))
		
	class AddTagForm(forms.Form):
		# mylaca nazwa - wstawia  zaznaczone pozycje (termbase name) do kodu html. aby wyslac je do pierwotnej strony
		# jest to wareunek ponownego wejscia w funkcje add_tag, w przeciwnym razie komunikat,ze nic nie zazaczono
		_selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
		#Wstawia liste wyboru z UserTermbase
		#termbase = forms.ModelChoiceField(UserTermbase.objects)
		source = forms.ModelChoiceField(Language.objects, label='Source language')
		target = forms.ModelChoiceField(Language.objects, label='Target language')
		docfile = forms.FileField(
        	label='Select a file',
        	help_text=''
        	)
        
	def add_tag(self, request, queryset):
		form = None
		selected_action = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
		source = request.POST.get('source')
		target = request.POST.get('target')
		#print ('ST: ', source)
		if len(selected_action)!=1:
			self.message_user(request, 'Select one termbase for import to!')
			return
		if 'cancel' in request.POST:
			self.message_user(request, 'Import canceled.')
			return
		if 'apply' in request.POST:
			print ('POST')
			form = self.AddTagForm(request.POST, request.FILES)
			if form.is_valid():
				filename = request.FILES['docfile']
				handle_uploaded_file(filename, str(filename))
				file = filename.name
				print (file)
				
				
				
				self.message_user(request, 'Sent to process')
				return HttpResponseRedirect(request.get_full_path())
		if not form:
			#wstawia wybrane pozycje do html - patrz wyzej
			form = self.AddTagForm(initial={'_selected_action': selected_action, 'target': Language.objects.all()[1], 'source': Language.objects.all()[0]})
			#form2 = DocumentForm()
			return render(request, 'admin/add_tag.html', {'articles': queryset,													
														'tag_form': form,
														'path':request.get_full_path(),
														})														
	add_tag.short_description = "Import terms"
	
	



def handle_uploaded_file(file, filename):
    if not os.path.exists('upload/'):
        os.mkdir('upload/')
 
    with open('upload/' + filename, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
            
admin.site.register(UserTermbase, UserTermbaseAdmin)
admin.site.register(Termbase, TermbaseAdmin)
admin.site.register(Language)
admin.site.register(Term, TermAdmin)
admin.site.register(Description)
admin.site.register(Hits)
#admin.site.register(TM)
#admin.site.register(TMPair, TMPairAdmin)
#admin.site.register(UserTM)
