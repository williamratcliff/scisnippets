from django.conf.urls.defaults import *

from cab.views import snippets

urlpatterns = patterns('',
    url(r'^$',
        snippets.snippet_list,
        name='cab_snippet_list'),
    url(r'^(?P<snippet_id>\d+)/$',
        snippets.snippet_detail,
        name='cab_snippet_detail'),
    url(r'^(?P<snippet_id>\d+)/rate/$',
        snippets.rate_snippet,
        name='cab_snippet_rate'),
    url(r'^(?P<snippet_id>\d+)/download/$',
        snippets.download_snippet,
        name='cab_snippet_download'),
    url(r'^(?P<snippet_id>\d+)/edit/$',
        snippets.edit_snippet,
        name='cab_snippet_edit'),
    url(r'^add/$',
        snippets.edit_snippet,
        name='cab_snippet_add'),
)
