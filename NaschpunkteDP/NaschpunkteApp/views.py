from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.core.exceptions import ValidationError
from django.middleware import csrf
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
from functools import wraps
import md5, json

from google.appengine.ext import ndb

from NaschpunkteApp.models import ActivityEntity, NaschEntity, PointEntity, EventEntity, UserEntity

def user_authenticated(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        request = args[0]
        try:
            user = ndb.Key(urlsafe=request.session['user_id']).get()
            if user is None:
                return redirect("/login/")
        except KeyError:
            return redirect("/login/")
        #everthing passed, call the function
        return func(*args, **kwargs)
    return wrapped

def user_authenticated_or_401(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        request = args[0]
        try:
            user = ndb.Key(urlsafe=request.session['user_id']).get()
            if user is None:
                return HttpResponse('Unauthorized', status=401)
        except KeyError:
            return HttpResponse('Unauthorized', status=401)
        #everthing passed, call the function
        return func(*args, **kwargs)
    return wrapped

@user_authenticated
def index(request):
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

def getBeginOfWeek():
	now=datetime.now().replace(hour=0,minute=0,second=0,microsecond=0)
	return now - timedelta(days=now.weekday())

@user_authenticated
def list_events(request):
    context = {}
    events = EventEntity.query(EventEntity.created > getBeginOfWeek(), EventEntity.userEntity == ndb.Key(urlsafe=request.session['user_id']))
    context["events"] = events
    return render_to_response('entities/listEventEntities.html', context, context_instance=RequestContext(request))

@user_authenticated
def create_event(request):
    if request.method == 'GET':
        context = {}
        entities = NaschEntity.query().fetch()
        entities += ActivityEntity.query().fetch()
        context["entities"] = entities
        return render_to_response('entities/createEvent.html', context, context_instance=RequestContext(request))
    elif request.method == 'POST':
        e = EventEntity()
        e.userEntity = ndb.Key(urlsafe=request.session['user_id'])
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
        u = ndb.Key(urlsafe=request.session['user_id'])
        u.username = request.POST["username"]
	u.secret = md5.new(request.POST["password"]).hexdigest()
        u.put()
	request.session['user_id'] = u.key.urlsafe()
        return redirect("/")

@csrf_exempt
def login_user(request):
    if request.method == 'GET':
        context = {}
        if "csrf" in request.GET:
            return HttpResponse(csrf.get_token(request))
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

def logout_user(request):
    del request.session['user_id']
    return redirect("/")

@user_authenticated_or_401
def rest(request):
	if "lsp" in request.path:
		events = EventEntity.query(EventEntity.created > getBeginOfWeek(), EventEntity.userEntity == ndb.Key(urlsafe=request.session['user_id'])).fetch()
		punkteSum = int(reduce(lambda x,y: x+y, map(lambda e:e.punkte, events)))
		return HttpResponse(str(punkteSum))
	if "lsa" in request.path:
		activities = ActivityEntity.query().fetch()
		return HttpResponse(json.dumps(activities))
	if "lsn" in request.path:
		naschies = NaschEntity.query().fetch()
		return HttpResponse(json.dumps(naschies))
	return HttpResponse('Not Found', status=404)	
