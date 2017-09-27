from django.db import models

from google.appengine.ext import ndb

# Create your models here.
class PointEntity(ndb.Model):
    name = ndb.StringProperty()
    einheit = ndb.StringProperty()
    punkte = ndb.IntegerProperty()
    defaultValue = ndb.IntegerProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    
    def _pre_put_hook(self):
        pass

class ActivityEntity(PointEntity):
    pass

class NaschEntity(PointEntity):
    pass

class EventEntity(ndb.Model):
    pointEntity = ndb.KeyProperty(kind=PointEntity)
    value = ndb.FloatProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
