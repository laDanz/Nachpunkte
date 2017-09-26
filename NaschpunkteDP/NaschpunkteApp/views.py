from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from NaschpunkteApp.models import ActivityEntity, NaschEntity
import uuid

def index(request):
    a = ActivityEntity()
    a.name="Test"
    a.id=uuid.uuid1().hex
    a.put()
    return HttpResponse(
        'Hello, World. This is Django running on Google App Engine')
    
def list_activities(request):
    context = {}
    activities = ActivityEntity.query()
    context["activities"] = activities
    return render_to_response('entities/listActivities.html', context, context_instance=RequestContext(request))