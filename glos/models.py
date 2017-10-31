from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import User
from datetime import datetime, timedelta


# Create your models here.
class Termbase(models.Model):
	name = models.CharField(max_length=50, unique=True)
	description =  models.CharField(max_length=200, default="")
	def __str__(self):
		return self.name
"""		
class TM(models.Model):
	name = models.CharField(max_length=50, unique=True)
	description =  models.CharField(max_length=100, default="")
	def __str__(self):
		return self.name
"""
class UserTermbase(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	termbase = models.ForeignKey(Termbase, on_delete=models.CASCADE)
	read = models.BooleanField(default=True)
	write = models.BooleanField(default=True)
	class Meta:
	    unique_together = ['user', 'termbase']
	def __str__(self):
		return self.user.username+"__"+self.termbase.name
		
class Hits(models.Model):
	hit = models.CharField(max_length=5, unique=True)
	def __str__(self):
		return self.hit
"""
class UserTM(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	tm = models.ForeignKey(TM, on_delete=models.CASCADE)
	#read = models.BooleanField(default=True)
	write = models.BooleanField(default=True)
	class Meta:
	    unique_together = ['user', 'tm']
	def __str__(self):
		return self.user.username+"__"+self.tm.name
"""		
class Language(models.Model):
	name = models.CharField(max_length=5, unique=True)
	def __str__(self):
		return self.name

class Term(models.Model):
	entry = models.CharField(db_index=True, max_length=2500)
	language = models.ForeignKey(Language, on_delete=models.CASCADE)
	termbase = models.ForeignKey(Termbase, on_delete=models.CASCADE)
	value = models.CharField(db_index=True, max_length=1000)
	lowvalue = models.CharField(db_index=True, max_length=1000)
	added = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)
	creator = models.ForeignKey(User, on_delete=models.CASCADE)
	#modifier = models.ForeignKey(User, on_delete=models.CASCADE)
	#lclid = models.CharField(max_length=100, default="")
	def __unicode__(self):
		return self.value
"""
class TMPair(models.Model):
	source = models.ForeignKey(Language, on_delete=models.CASCADE, related_name="source_language")
	target = models.ForeignKey(Language, on_delete=models.CASCADE, related_name="target_language")
	#name = models.CharField(db_index=True, max_length=100)
	creator = models.ForeignKey(User, on_delete=models.CASCADE)
	def __str__(self):
		return self.source.name+"-"+self.target.name
"""				
class Description(models.Model):
	value = models.CharField(max_length=5000)
	name = models.CharField(max_length=20)
	type = models.CharField(max_length=20)
	term = models.ForeignKey(Term, on_delete=models.CASCADE)
	entry = models.CharField(db_index=True, max_length=200, default="")
	ENTRY_LEVEL = 1
	LANGUAGE_LEVEL = 2
	TERM_LEVEL = 3
	LEVEL_CHOICES =((ENTRY_LEVEL, "Entry"), (LANGUAGE_LEVEL, "Language"), (TERM_LEVEL, "Term"))
	level = models.IntegerField(choices=LEVEL_CHOICES, default=ENTRY_LEVEL)
	def __str__(self):
		return self.name+"_"+self.value
	
