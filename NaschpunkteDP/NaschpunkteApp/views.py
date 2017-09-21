from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from NaschpunkteApp.models import Activity
import uuid

def index(request):
    a = Activity()
    a.name="Test"
    a.id=uuid.uuid1().hex
    a.put()
    return HttpResponse(
        'Hello, World. This is Django running on Google App Engine')