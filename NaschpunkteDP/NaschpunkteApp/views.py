from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.core.exceptions import ValidationError
import md5

from google.appengine.ext import ndb

from NaschpunkteApp.models import ActivityEntity, NaschEntity, PointEntity, EventEntity, UserEntity

def index(request):
    context = {}
    user = ndb.Key(urlsafe=request.session['user_id']).get()
    if user is None:
        return redirect("/login/")
    return redirect("/lse/")
    
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
    return render_to_response('entities/listEventEntities.html', context, context_instance=RequestContext(request))

def create_event(request):
    if request.method == 'GET':
        context = {}
        entities = NaschEntity.query().fetch()
        entities += ActivityEntity.query().fetch()
        context["entities"] = entities
        return render_to_response('entities/createEvent.html', context, context_instance=RequestContext(request))
    elif request.method == 'POST':
        e = EventEntity()
        #e.pointEntity = ndb.Key("PointEntity", request.POST["pointEntity"])
        e.pointEntity = ndb.Key(urlsafe=request.POST["pointEntity"])
        try:
            e.value = float(request.POST["value"])
        except ValueError:
            raise ValidationError(
                    _('Ungueltiger Zahlenwert: %(value)s'),
                    params={'value': request.POST["value"]},
           )
        e.put()
        return redirect("/lse/")

def create_user(request):
    if request.method == 'GET':
        context = {}
        return render_to_response('user/createUser.html', context, context_instance=RequestContext(request))
    elif request.method == 'POST':
        u = UserEntity()
        u.username = request.POST["username"]
	u.secret = md5.new(request.POST["password"]).hexdigest()
        u.put()
	request.session['user_id'] = u.key.urlsafe()
        return redirect("/")

def login_user(request):
    if request.method == 'GET':
        context = {}
        return render_to_response('user/login.html', context, context_instance=RequestContext(request))
    elif request.method == 'POST':
        u = UserEntity.query(UserEntity.username==request.POST["username"]).get()
	if u is None:
		raise ValidationError('Unbekannter Nutzer!')
	if u.secret != md5.new(request.POST["password"]).hexdigest():
		raise ValidationError('Falsches Passwort!')
        #user is successfully authenticated at this point
	request.session['user_id'] = u.key.urlsafe()
        return redirect("/")
