from django.shortcuts import render
from .forms import ContactForm
from django.core.mail import EmailMessage

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

def special (request):
	if request.method == 'POST':
		emailformOK(request)
		return render(request, 'glos/email.html', emailformOK(request))
	else:
		return render(request, 'glos/special.html', emailform())	
def prices (request):
	if request.method == 'POST':
		emailformOK(request)
		return render(request, 'glos/email.html', emailformOK(request))
	else:
		return render(request, 'glos/prices.html', emailform())		