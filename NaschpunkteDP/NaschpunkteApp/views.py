from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from google.appengine.ext import ndb

from NaschpunkteApp.models import ActivityEntity, NaschEntity, PointEntity, EventEntity

def index(request):
    a = ActivityEntity()
    a.name="Test"
    a.put()
    return HttpResponse(
        'Hello, World. This is Django running on Google App Engine')
    
def list_activities(request):
    context = {}
    activities = ActivityEntity.query()
    context["activities"] = activities
    return render_to_response('entities/listPointEntities.html', context, context_instance=RequestContext(request))

def list_naschies(request):
    context = {}
    naschies = NaschEntity.query()
    context["activities"] = naschies
    return render_to_response('entities/listPointEntities.html', context, context_instance=RequestContext(request))

def list_events(request):
    context = {}
    events = EventEntity.query()
    context["events"] = events
    return render_to_response('entities/listPointEntities.html', context, context_instance=RequestContext(request))

def create_event(request):
    if request.method == 'GET':
        context = {}
        entities = PointEntity.query()
        context["entities"] = entities
        return render_to_response('entities/createEvent.html', context, context_instance=RequestContext(request))
    elif request.method == 'POST':
        e = EventEntity()
        e.key = ndb.Key("PointEntity", request.POST["pointEntity"])
        e.value = request.POST["value"]
        e.put()
        redirect("list_naschies")