from django.db import models

from google.appengine.ext import ndb
# Create your models here.
class Activity(ndb.Model):
    name = ndb.StringProperty()
    punkte = ndb.IntegerProperty()
    id = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)