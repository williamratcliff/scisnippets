from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import slugify

AWS_AFFILIATE_ID = getattr(settings, 'AWS_AFFILIATE_ID', '')


class ResourceCategory(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=200, editable=False)
    sort_order = models.IntegerField(default=0)
    
    class Meta:
        verbose_name_plural = 'Resource categories'
        ordering = ('sort_order', 'title')
    
    def __unicode__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('resource_category_detail', args=[self.slug])
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(ResourceCategory, self).save(*args, **kwargs)
    
    def recommended(self):
        return self.resources.filter(recommended=True)


class MediaType(models.Model):
    title = models.CharField(max_length=255)
    
    def __unicode__(self):
        return self.title


class Resource(models.Model):
    asin = models.CharField(max_length=15, editable=False)
    category = models.ForeignKey(ResourceCategory, related_name='resources', null=True)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    media_type = models.ForeignKey(MediaType, null=True)
    pub_date = models.DateField(blank=True, null=True)
    pages = models.IntegerField(blank=True, null=True)
    cover_image = models.ImageField(upload_to='amazon_resources', blank=True)
    recommended = models.BooleanField(default=False)
    
    class Meta:
        ordering = ('title',)
    
    def __unicode__(self):
        return self.title
    
    def get_absolute_url(self):
        return 'http://www.amazon.com/dp/%s/?tag=%s' % (self.asin, AWS_AFFILIATE_ID)
    
    def thumbnail(self):
        if not self.cover_image:
            return '<p>No image</p>'
        return '<img src="%s" alt="%s" />' % (self.cover_image.url, self.title)
    thumbnail.short_description = 'Image thumbnail'
    thumbnail.allow_tags = True
    thumbnail.safe = True
