from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse
# Create your views here.
def home_view(request):
    return HttpResponse(_('Hello World!'))