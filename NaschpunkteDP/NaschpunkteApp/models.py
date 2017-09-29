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

class UserEntity(ndb.Model):
	username = ndb.StringProperty()
	secret = ndb.StringProperty()

class EventEntity(ndb.Model):
    userEntity = ndb.KeyProperty(kind=UserEntity)
    pointEntity = ndb.KeyProperty()
    value = ndb.FloatProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    @property
    def punkte(self):
        return self.value * self.p.punkte / self.p.defaultValue
    @property
    def p(self):
        return self.pointEntity.get()
