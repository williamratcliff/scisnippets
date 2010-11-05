from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()



urlpatterns = patterns('',
    # Example:
    (r'^tags/',include('external_apps.cab.urls.tags')),
    (r'^bookmarks/',include('external_apps.cab.urls.bookmarks')),
    (r'^languages/',include('external_apps.cab.urls.languages')),
    (r'^popular/',include('external_apps.cab.urls.popular')),
    (r'^snippets/',include('external_apps.cab.urls.snippets')),
    # (r'^scisnippets/', include('scisnippets.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)

#urlpatterns += include('external_apps.cab.urls')
