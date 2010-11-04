from django.conf.urls.defaults import *

urlpatterns = patterns('amazon_resources.views',
    url(r'^$', 'category_list', name='category_list'),
    url(r'^all/$', 'resource_list', name='resource_list'),
    url(r'^(?P<category_slug>[-\w]+)/$', 'resource_list', name='resource_category_detail'),
)
