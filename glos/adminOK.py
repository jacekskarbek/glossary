from django.contrib import admin
from .models import Termbase, UserTermbase, Terms
from django.utils.safestring import mark_safe
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.contrib.admin import helpers
from django.template.response import TemplateResponse
from django import forms
from django.shortcuts import render, render_to_response
from django.contrib.auth import authenticate, login
from django.template import Template, RequestContext


from django.contrib.admin.views.main import ChangeList


from django.contrib.auth.models import User
from django.conf.urls import *
from functools import update_wrapper



# Register your models here.

class UserInline(admin.TabularInline):
    model = UserTermbase

class UserTermbaseAdmin(admin.ModelAdmin):
	
	# ktore pola będą wyświetlane w Admin
	# fields = ('user','termbase','read','write')
	list_display = ('user','termbase','read','write')

class TermbaseAdmin(admin.ModelAdmin):
	inlines = [UserInline]
	# ktore pola będą wyświetlane w Admin
	# fields = ('user','termbase','read','write')
	#def importpage(self, obj):
		# return mark_safe('<a class="addlink">'+str(obj.id)+'</a>')
		#return mark_safe('<a class="addlink" href="'+str(obj.id)+'">Import</a>')
		
	#importpage.short_description = 'Import'
	#importpage.allow_tags = True
	actions = ['make_published','export_selected_objects', 'add_tag']
	
	list_display = ('termbase_name',)
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
		_selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
		termbase = forms.ModelChoiceField(UserTermbase.objects)
	def add_tag(self, request, queryset):
		form = None
		self.message_user(request, 'uwga!!!!!.')
		if 'cancel' in request.POST:
			self.message_user(request, 'Canceled series linking.')
			return

		if 'apply' in request.POST:
			print (request.POST)
			form = self.AddTagForm(request.POST)
			if form.is_valid():
			#	usertermbase = form.cleaned_data['usertermbase']
				count = 0
				for termbase in queryset:
					#termbase
					count +=1
				plural = ''
				if count !=1:
					plural = 's'
				self.message_user(request, 'Selected %s' % (count))
				return HttpResponseRedirect(request.get_full_path())
		if not form:
			
			form = self.AddTagForm(initial={'_selected_actions': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})
		return render(request, 'admin/add_tag.html', {'articles': queryset,
														
														'tag_form': form,
														'path':request.get_full_path(),
														})
														
	add_tag.short_description = "Add tag to articles"
	

	
	
admin.site.register(UserTermbase, UserTermbaseAdmin)
admin.site.register(Termbase, TermbaseAdmin)
admin.site.register(Terms)

