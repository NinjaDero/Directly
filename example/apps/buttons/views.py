from django.shortcuts import render_to_response
from django.template import RequestContext


def index(request):
    # Somehow get the html delivered, everything else is usually JavaScript in Ext
    return render_to_response('index.html', RequestContext(request))