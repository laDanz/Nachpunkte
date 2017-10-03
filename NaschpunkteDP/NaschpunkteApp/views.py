from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.core.exceptions import ValidationError
from django.middleware import csrf
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta, date
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
        user_id = None
        try:
            user_id = request.session['user_id']
        except KeyError:
            try:
                user_id = request.GET['user_id']
            except KeyError:
                try:
                    user_id = request.POST['user_id']
                except KeyError:
                    pass
        if user_id is None:
            return HttpResponse('Unauthorized', status=401)
        user = ndb.Key(urlsafe=user_id).get()
        if user is None:
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
        u = UserEntity()
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
        media_type='text/html'
        if request.META.has_key('CONTENT_TYPE'):
            media_type = request.META['CONTENT_TYPE'].split(';')[0]
        if media_type.lower() == 'application/json':
            body = json.loads(request.body)
            u = UserEntity.query(UserEntity.username==body["username"]).get()
            if u is None:
                raise ValidationError('Unbekannter Nutzer!')
            if u.secret != md5.new(body["password"]).hexdigest():
                raise ValidationError('Falsches Passwort!')
            res = HttpResponse("""{ "ResponseCode": "Success"}""", content_type="application/json; charset=UTF-8")
            res['user_id'] = u.key.urlsafe()
            return res
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

def json_serial(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

def toList(entities):
    res = []
    for a in entities:
        d = a.to_dict()
        d["urlsafe"] = a.key.urlsafe()
        res.append(d)
    return res	

@csrf_exempt
@user_authenticated_or_401
def rest(request):
	user_id = None
	try:
		user_id = request.GET["user_id"]
	except KeyError:
		try:
			user_id = request.POST["user_id"]
		except KeyError:
			try:
				user_id = request.session['user_id']
			except KeyError:
				pass
	if "lsp" in request.path:
		events = EventEntity.query(EventEntity.created > getBeginOfWeek(), EventEntity.userEntity == ndb.Key(urlsafe=user_id)).fetch()
		punkteSum = 0
		if len(events)>0:
			punkteSum = int(reduce(lambda x,y: x+y, map(lambda e:e.punkte, events)))
		return HttpResponse(str(punkteSum))
	if "lsa" in request.path:
		activities = ActivityEntity.query().fetch()
		return HttpResponse(json.dumps(toList(activities), default=json_serial))
	if "lsn" in request.path:
		naschies = NaschEntity.query().fetch()
		return HttpResponse(json.dumps(toList(naschies), default=json_serial))
	if "cre" in request.path:
		e = EventEntity()
		e.userEntity = ndb.Key(urlsafe=request.POST['user_id'])
		e.pointEntity = ndb.Key(urlsafe=request.POST['event'])
		try:
			e.value = float(request.POST["value"])
		except ValueError:
			HttpResponse('Bad value', status=500)
		e.put()
		return HttpResponse(status=200)		
	return HttpResponse('Not Found', status=404)	
