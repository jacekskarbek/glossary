import xml.etree.ElementTree as ET
import xml.dom.pulldom as pulldom
import xml.dom.minidom as minidom

class Description:
	pass
class TermGroup:
	pass
class Language:
	pass
class TbxItem:
	pass

def processDescrip(descrip):
	description = Description()
	description.name = descrip.nodeName
	description.type = descrip.getAttribute('type')
	description.value = descrip.childNodes[0].nodeValue
	#print('Node Name: ',description.name, description.value, description.type)
	return description

def processDescrips(descrips):
	descriptions=[]
	for descrip in descrips.childNodes:
		if descrip.nodeType==1:
			descriptions.append(processDescrip(descrip))
	return descriptions

def multitermparse(node, events):		
	item = TbxItem()
	languages = []
	item.descripGrp = []
	events.expandNode(node)
	for conlandes in node.childNodes: #concept or languageGrp or descripGrp
		element = False
		if conlandes.nodeType==1:
			if conlandes.tagName=='concept':			
				item.ID = conlandes.childNodes[0].nodeValue
				print('concept',item.ID)
			if conlandes.nodeName=='descripGrp':
				item.descripGrp = processDescrips(conlandes)
			if conlandes.tagName=='languageGrp':
				language = Language()
				language.descripGrp = []
				element=True
				termList = []
				for lantermdescr in conlandes.childNodes: # language or termGrp or descripGrp
					if lantermdescr.nodeType==1:
						if lantermdescr.tagName=='language':
							language.lang = lantermdescr.getAttribute('lang')
						if lantermdescr.tagName=='descripGrp':
							language.descripGrp = processDescrips(lantermdescr)
						if lantermdescr.tagName=='termGrp':
							termGrp = TermGroup()
							descrips = []
							for term in lantermdescr.childNodes: #term or descripGrp
								if term.nodeType==1:
									if term.tagName == 'descripGrp':
										#print('termdesc:',term)
										descrips = processDescrips(term)
									if term.tagName == 'term':
										termGrp.term = term.childNodes[0].nodeValue
										print('termvalue:')
										for node in term.childNodes:
											print(node.nodeValue)
									termGrp.descripGrp=descrips
							termList.append(termGrp)
				language.termGrp=termList
			if element:
				languages.append(language)
	item.languages = languages
	return item

def pulldomparseentry(node, events):		
	item = TbxItem()
	languages = []
	item.ID = node.getAttribute('id')
	item.descripGrp = []
	#print (item.ID, node.tagName)
	events.expandNode(node)
	for conceptLevel in node.childNodes: # descripGrp or langSet or \n
		element = False		
		if conceptLevel.nodeName=='descripGrp':
			item.descripGrp = processDescrips(conceptLevel)
		if conceptLevel.nodeName=='langSet':
			language = Language()
			element=True
			termList = []
			language.lang = conceptLevel.getAttribute('xml:lang')
			language.descripGrp = []
			#print('Language: ', language.lang)
			for tig in conceptLevel.childNodes:
				if tig.nodeName=='descripGrp':
					language.descripGrp = processDescrips(tig)
				if (tig.nodeName=='tig') or (tig.nodeName=='ntig'):
					if tig.nodeName=='tig':
						terms = tig.childNodes
					else:
						terms = tig.getElementsByTagName('termGrp')[0].childNodes
					termGrp = TermGroup()
					descrips = []
					for term in terms:   # term or descr
						if term.nodeName == 'term':
							termGrp.term = term.childNodes[0].nodeValue
						else:
							if term.nodeType==1:
								descrips.append(processDescrip(term))
					termGrp.descripGrp = descrips
					termList.append(termGrp)
			language.termGrp = termList
		if element:
			languages.append(language)
	item.languages = languages
	return item


