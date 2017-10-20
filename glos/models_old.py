from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import User


	
# Create your models here.
class Termbase(models.Model):
	#group = models.ForeignKey(Group)
	termbase_name = models.CharField(max_length=50)
	def __str__(self):
		return self.termbase_name

class UserTermbase(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='term')
	termbase = models.ForeignKey(Termbase, on_delete=models.CASCADE, related_name='term')
	read = models.BooleanField(default=True)
	write = models.BooleanField(default=True)
	class Meta:
	    unique_together = ['user', 'termbase']
	def __str__(self):
		return self.user.username+"__"+self.termbase.termbase_name

class Terms(models.Model):	
	termbase = models.ForeignKey(Termbase, on_delete=models.CASCADE)
	sourceTerm = models.CharField(max_length=50)
	targetTerm = models.CharField(max_length=50) 	                                                                                                    
	sense = models.CharField(max_length=50) 
	collocator = models.CharField(max_length=50)
	worclass = models.CharField(max_length=50)
	topic = models.CharField(max_length=50)
	def __str__(self):
		return self.sourceTerm+": "+self.targetTerm
	class Meta:
		default_permissions = ('add', 'change', 'delete', 'view')
		unique_together = ['sourceTerm', 'targetTerm']

class Entry(models.Model):
	termbase = models.ForeignKey(Termbase, on_delete=models.CASCADE)
	ind = models.CharField(max_length=20, unique=True)
	def __str__(self):
		return self.ind

class Language(models.Model):
	entry = models.ForeignKey(Entry, on_delete=models.CASCADE)
	value = models.CharField(max_length=5)
	def __str__(self):
		return self.value

class Term(models.Model):
	language = models.ForeignKey(Language, on_delete=models.CASCADE)
	value = models.CharField(db_index=True, max_length=50)
	def __str__(self):
		return self.value
			
class TermDescrip(models.Model):
	term = models.ForeignKey(Term, on_delete=models.CASCADE)
	name = models.CharField(max_length=20)
	type = models.CharField(max_length=20)
	value = models.CharField(max_length=200)
	def __str__(self):
		return self.name+"_"+self.type
	
class LanguageDescrip(models.Model):
	language = models.ForeignKey(Language, on_delete=models.CASCADE)
	name = models.CharField(max_length=20)
	type = models.CharField(max_length=20)
	value = models.CharField(max_length=200)
	def __str__(self):
		return self.name+"_"+self.type
	
class EntryDescrip(models.Model):
	entry = models.ForeignKey(Entry, on_delete=models.CASCADE)
	name = models.CharField(max_length=20)
	type = models.CharField(max_length=20)
	value = models.CharField(max_length=200)
	def __str__(self):
		return self.name+"_"+self.type