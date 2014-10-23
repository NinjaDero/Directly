from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    # Get this into our app... Usually I try to keep app-specific URLs inside those apps
    url(r'', include('apps.buttons.urls')),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve'),
)