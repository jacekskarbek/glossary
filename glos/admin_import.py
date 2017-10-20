from mysite.books.models import Book
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.admin.views.decorators import staff_member_required


def report(request):
    return render_to_response(
        "admin/glos/termbase/import.html",
        {'book_list' : termmbase.objects.all()},
        RequestContext(request, {}),
    )
report = staff_member_required(report)