from channels.auth import channel_session_user_from_http
from channels import Group
from django.contrib.auth.models import User
from .tbx import multitermparse, pulldomparseentry
from django.core import serializers
import xml.etree.ElementTree as ET
import xml.dom.pulldom as pulldom
import xml.dom.minidom as minidom
import os
from .models import Termbase, UserTermbase, Term, Language, Term, Description
from channels.sessions import channel_session
import csv

def ws_message(message):
	# ASGI WebSocket packet-received and send-packet message types
	# both have a "text" key for their textual data.
	
	#message.reply_channel.send({
	#	"text": message.content['text'],
	#})
	
	
	#Group("%s" % <user>).add(message.reply_channel)
	Group("chat-glos").add(message.reply_channel)


def importer(message):
	file = message.content['file']
	filename, file_extension = os.path.splitext(file)
	print("File: ", file, "extension: ", file_extension)  # long running task or printing
	sourceno = message.content['source']
	targetno = message.content['target']
	senduser = message.content['user']
	source = Language.objects.filter(pk=sourceno)[0]
	target = Language.objects.filter(pk=targetno)[0]
	print('Source: ', sourceno, source)
	#Group("glos").send({"text": "Ala ma kota"}) 
	ts=message.content['termbase']
	#termbaseselected=serializers.deserialize('json',termbase)[0]
	####tree = ET.parse('upload/'+message.content['file'])
	####root=tree.getroot()
	user = User.objects.filter(username = senduser)[0]
	termbase=Termbase.objects.filter(termbase_name=ts)[0]
	#print('User: ',user)
	counter=0
	if file_extension==".xml":
		events=pulldom.parse('upload/'+file)
		for event, node in events:
			if event == 'START_ELEMENT' and node.tagName=='termEntry':
				entry=pulldomparseentry(node, events)
				processentry(entry, counter,termbase, source, target, user)
			if event == 'START_ELEMENT' and node.tagName=='conceptGrp':
				print(node)
				entry=multitermparse(node, events)
				printentry(entry)
				processentry(entry, counter,termbase, source, target, user)
	if file_extension==".msoffice":	
		with open('upload/'+file) as csvfile:
			spamreader = csv.reader(csvfile, delimiter=';', quotechar='"')
			for row in spamreader:
				print(row[0])
				print(', '.join(row))
				processcsventry(row, counter, termbase, source, target, user)
				
def processcsventry(row, counter, termbase, source, target, user):
	counter+= 1
	if (counter % 100) == 0:
		print('Imported: ',counter)
	newterm, nt = Term.objects.get_or_create(entry = row[0], termbase=termbase, language=source, value=row[1], creator=user)
	newterm.save
	newedescrip, ned = Description.objects.get_or_create(term=newterm, name="SourceApprovalStatus" , type="SourceApprovalStatus", value=row[2], level=Description.ENTRY_LEVEL)
	newedescrip.save
	newedescrip, ned = Description.objects.get_or_create(term=newterm, name="SourcePartOfSpeech" , type="SourcePartOfSpeech", value=row[3], level=Description.ENTRY_LEVEL)
	newedescrip.save
	newedescrip, ned = Description.objects.get_or_create(term=newterm, name="ConceptDefinition" , type="ConceptDefinition", value=row[8], level=Description.ENTRY_LEVEL)
	newedescrip.save
	newedescrip, ned = Description.objects.get_or_create(term=newterm, name="TargetProduct" , type="TargetProduct", value=row[11], level=Description.ENTRY_LEVEL)
	newedescrip.save
	newedescrip, ned = Description.objects.get_or_create(term=newterm, name="TargetUsageNote" , type="TargetUsageNote", value=row[14], level=Description.ENTRY_LEVEL)
	newedescrip.save
	newterm, nt = Term.objects.get_or_create(entry = row[0], termbase=termbase, language=target, value=row[6], creator=user)
	newterm.save
	
	
def processentry(entry, counter, termb, source, target, user):	
	#printentry(entry)		
	counter+= 1
	if (counter % 100) == 0:
		print('Imported: ',counter)
	
	for lang in entry.languages:		
		languageid=None
		if source.value.lower() in lang.lang.lower(): 
			languageid=source
		if target.value.lower() in lang.lang.lower(): 
			languageid=target
		if languageid:
			isanylanguage=True
			#print('LanguageID: ', languageid)
			for term in lang.termGrp:
				newterm, nt = Term.objects.get_or_create(entry = entry.ID, termbase=termb, language=languageid, value=term.term, creator=user)
				newterm.save
				for tdescrip in term.descripGrp:
					newedescrip, ned = Description.objects.get_or_create(term=newterm, name=tdescrip.name , type=tdescrip.type, value=tdescrip.value, level=Description.TERM_LEVEL)
					newedescrip.save
				#for descrip in lang.descripGrp:
				#	newedescrip, ned = Description.objects.get_or_create(term=newterm, name=descrip.name , type=descrip.type, value=descrip.value, level=Description.LANGUAGE_LEVEL)
				#	newedescrip.save
				for edescrip in entry.descripGrp:
					newedescrip, ned = Description.objects.get_or_create(term=newterm, name=edescrip.name , type=edescrip.type, value=edescrip.value, level=Description.ENTRY_LEVEL)
					newedescrip.save	

def printentry(entry):
	print('Entry',entry.ID)
	for d in entry.descripGrp:
		print('Description',d.name, d.type,d.value)
	for l in entry.languages:
		print('  Langauge',l.lang)
		for d in l.descripGrp:
			print('   Description',d.name, d.type,d.value)
		for t in l.termGrp:
			print('      Term',t.term)
			for d in t.descripGrp:
				print('      Description',d.name, d.type,d.value)
		
#def ws_message(message):
    # ASGI WebSocket packet-received and send-packet message types
    # both have a "text" key for their textual data.
    #message.reply_channel.send({
    #	"text": message.content['text'],
    #})
    #Group("glos").send({"text": "Ala ma kota"}) 
