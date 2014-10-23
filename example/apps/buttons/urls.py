from django.conf.urls import patterns, url

from Directly import Ext
from apps.buttons.methods import Buttons, Notepad, Store

# I combine all classes I want to access under the same namespace in an array
CLASSES = [
    Buttons,
    Notepad,
    Store
]

urlpatterns = patterns('',

    url(r'^$', 'apps.buttons.views.index'),




    # The interesting part

    # Generate an API at /exampleAPI - could also be exampleAPI.js for clarity
    url(r'^exampleAPI', Ext.getApi(namespace='Example', url='/exampleAction', apis=CLASSES)),
    # Forward everything to /exampleAction and print all Requests to console
    url(r'^exampleAction', Ext.rpc(apis=CLASSES, debug=True)),
)