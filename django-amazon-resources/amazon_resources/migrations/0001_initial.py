# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'ResourceCategory'
        db.create_table('amazon_resources_resourcecategory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=200, db_index=True)),
            ('sort_order', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('amazon_resources', ['ResourceCategory'])

        # Adding model 'MediaType'
        db.create_table('amazon_resources_mediatype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('amazon_resources', ['MediaType'])

        # Adding model 'Resource'
        db.create_table('amazon_resources_resource', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('asin', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['amazon_resources.ResourceCategory'], null=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('author', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('media_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['amazon_resources.MediaType'], null=True)),
            ('pub_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('pages', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('cover_image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('recommended', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
        ))
        db.send_create_signal('amazon_resources', ['Resource'])


    def backwards(self, orm):
        
        # Deleting model 'ResourceCategory'
        db.delete_table('amazon_resources_resourcecategory')

        # Deleting model 'MediaType'
        db.delete_table('amazon_resources_mediatype')

        # Deleting model 'Resource'
        db.delete_table('amazon_resources_resource')


    models = {
        'amazon_resources.mediatype': {
            'Meta': {'object_name': 'MediaType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'amazon_resources.resource': {
            'Meta': {'object_name': 'Resource'},
            'asin': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'author': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['amazon_resources.ResourceCategory']", 'null': 'True'}),
            'cover_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'media_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['amazon_resources.MediaType']", 'null': 'True'}),
            'pages': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'pub_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'recommended': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'amazon_resources.resourcecategory': {
            'Meta': {'object_name': 'ResourceCategory'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '200', 'db_index': 'True'}),
            'sort_order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['amazon_resources']
