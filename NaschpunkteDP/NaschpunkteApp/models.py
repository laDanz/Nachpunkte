from django.db import models

from google.appengine.ext import ndb
# Create your models here.
class PointEntity(ndb.Model):
    name = ndb.StringProperty()
    einheit = ndb.StringProperty()
    punkte = ndb.IntegerProperty()
    defaultValue = ndb.IntegerProperty()
    id = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)

class ActivityEntity(PointEntity):
    pass

class NaschEntity(PointEntity):
    pass
