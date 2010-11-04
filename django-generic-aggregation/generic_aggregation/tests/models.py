import datetime

from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

class Food(models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name


class Rating(models.Model):
    rating = models.IntegerField()
    created = models.DateTimeField(default=datetime.datetime.now)
    object_id = models.IntegerField()
    content_type = models.ForeignKey(ContentType)
    content_object = GenericForeignKey(ct_field='content_type', fk_field='object_id')
    
    def __unicode__(self):
        return '%s rated %s' % (self.content_object, self.rating)


class CharFieldGFK(models.Model):
    name = models.CharField(max_length=255)
    object_id = models.CharField(max_length=10)
    content_type = models.ForeignKey(ContentType)
    content_object = GenericForeignKey(ct_field='content_type', fk_field='object_id')
