from django import forms
from .models import UserTermbase, Language, Hits
class NameForm(forms.Form):
    #searchTerm = forms.CharField(label='Term: ', label_suffix="", max_length=100, widget=forms.TextInput(attrs={'class' : 'form-control input-cls'}))
    searchTerm = forms.CharField(label='', label_suffix="", max_length=100, widget=forms.TextInput(attrs={'class' : 'form-control input-cls'}))
class ContactForm(forms.Form):
    #searchTerm = forms.CharField(label='Term: ', label_suffix="", max_length=100, widget=forms.TextInput(attrs={'class' : 'form-control input-cls'}))
    name = forms.CharField(required=True, label='', label_suffix="", max_length=100, widget=forms.TextInput(attrs={'class' : 'contactSearchBar', 'placeholder': 'Your Name'}))
    email = forms.EmailField(required=True, label='', label_suffix="", max_length=100, widget=forms.EmailInput(attrs={'class' : 'contactSearchBar', 'placeholder': 'Email Address'}))
    message = forms.CharField(required=True, label='', label_suffix="", max_length=100, widget=forms.Textarea(attrs={'class' : 'contactSearchBar', 'placeholder': 'Your message'}))
class Sourcelanguage(forms.Form):
    source = forms.ModelChoiceField(Language.objects, label='Source language', widget=forms.Select(attrs={'class':'form-control input-cls-small'}))

class Targetlanguage(forms.Form):
    target = forms.ModelChoiceField(Language.objects, label='Target language', widget=forms.Select(attrs={'class':'form-control input-cls-small'}))
   
class SearchHits(forms.Form):
    hit = forms.ModelChoiceField(Hits.objects, label='Search Hits', widget=forms.Select(attrs={'class':'form-control input-cls-small'}))
    
class DocumentForm(forms.Form):
    docfile = forms.FileField(
        label='Select a file',
        #help_text='max. 42 megabytes'
    )

class Termbases(forms.Form):
	termy = forms.MultipleChoiceField(
			widget  = forms.CheckboxSelectMultiple,
		)
	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user',None)
		super(Termbases, self).__init__(*args, **kwargs)
		#self.fields['termy'].choices = UserTermbase.objects.filter(user=self.user).values('termbase')
		print (UserTermbase.objects.filter(user=self.user))
		self.fields['termy'].choices = (('1','w1'),('2','w2'))