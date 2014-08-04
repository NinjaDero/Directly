#################################################
#
# Author: Alex Mannhold / Ninjadero
# 
# Contact me on GitHub in case there's a problem,
# or a change that doesn't qualify for a post in
# the issues thread.
# I will respond as soon as I can.
#
#################################################

import json
import inspect
from datetime import datetime
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

# Convert datetime objects into an ISO String 'Y-m-d\TH:i:s'
datetime_iso = (lambda obj:
                    obj.isoformat() if isinstance(obj, datetime) else None)

# Regular screwup
class ExtDirectlyException(Exception):
    def __init__(self, message):
        self.__value = message

    def __str__(self):
        return repr(self.__value)

# Minor screwup
class ExtDirectlyMethodException(Exception):
    def __init__(self, method):
        msg = 'Method \'{0}\' decorated. '.format(method.__name__) + \
              'One parameter needed to catch the HttpRequest'
        self.__value = msg

    def __str__(self):
        return repr(self.__value)

class DirectlyClass():
    """
    Alternative to class decorator. All we need is that tag.
    """
    _is_ext = True
    def __init__(self): pass


class Ext():
    @staticmethod
    def use(request, direct_mods, debug=False):
        """
        Takes RPC from request and searches a list or tuple direct_mods
        for ExtDirect classes and methods to take.
        """
        try:
            rpc_in = json.loads(request.body)
        except ValueError:
            # Body is not JSON
            return HttpResponse(
                content=json.dumps(None),
                content_type='application/json')
        # Print to console if debug is True
        # Call function for custom printing or testing if it's callable
        if type(debug) == bool and debug:
            print rpc_in
        elif callable(debug):
            debug(rpc_in)

        # Is it one or multiple modules?
        if type(direct_mods) not in [tuple, list]:
            direct_mods = [direct_mods]
        
        # If it's not batched, we still want a list to iterate over
        if not type(rpc_in) == list:
            rpc_in = [rpc_in]

        content = []

        for rpc in rpc_in:
            # Extract usefull information
            if rpc['type'] == 'rpc':
                action = rpc['action']
                method = rpc['method']
                data = rpc['data']
                tid = rpc['tid']

                # Start looking to called method
                method_return = Ext.getMethod(
                                direct_mods, action, method, data, request)
                # Create an answer object
                answer_rpc = {
                    'type': 'rpc',
                    'tid': tid,
                    'action': action,
                    'method': method,
                    'result': method_return
                }

                content.append(answer_rpc)
        # Return empty list or list of objects
        return HttpResponse(
                content=json.dumps(
                    content,
                    default=datetime_iso,
                    ensure_ascii=False
                ),
                content_type='application/json')

    @staticmethod
    def getMethod(direct_mods, action, method, data, request):
        """
        Uses the extracted data, iterates through the modules and
        calls the correct method if found.
        """
        # Check every module/file
        for mod in direct_mods:
            for name, obj in inspect.getmembers(mod):
                # Then each class in it
                if inspect.isclass(obj) and hasattr(obj, '_is_ext'):
                    if name == action:
                        for sub_name, sub_obj in inspect.getmembers(obj):
                            # Then each staticfunction inside
                            if (inspect.isfunction(sub_obj) and
                                hasattr(sub_obj, '_is_ext')):
                                if sub_name == method:
                                    # Method found, use it!
                                    return Ext.useMethod(
                                        sub_obj, data, request)
        return None

    @staticmethod
    def useMethod(method, data, request):
        """
        Checks a given method for number of arguments and calls it
        including the Django-request, in case the user needs it.
        """
        answer = None
        
        args, varargs, keywords, defaults = inspect.getargspec(method)
        # If defaults or data is missing or 0, they become NoneType.
        # So we just turn them back into something we can count.
        if not type(defaults) == tuple:
            defaults = []
        if not type(data) == list:
            data = []
        
        # We expect the user to catch 'request' as first argument.
        # Therefore argument count - 1 = REAL argument count
        if len(data) < (len(args) - len(defaults)) - 1:
            pass
            # Not enough args, can't use
        elif len(data) > len(args) - 1:
            # Too many args, cut off the last ones and use it anyway...
            data = data[:len(args) - 1]
        answer = method(request, *data)

        return answer

    @staticmethod
    def generateApi(namespace, direct_mods, url, request):
        """
        Generates the API JavaScript part using provided modules, 
        namespace and calling url
        Also we need request just to be able to serve both, 
        the browser and Architect
        """
        # In case the user provides a single module
        # Tuple or list doesn't matter, it needs to iterate
        if type(direct_mods) not in [tuple, list]:
            direct_mods = [direct_mods]

        classes = dict()
        provider = dict()
        provider['type'] = 'remoting'
        provider['namespace'] = namespace
        provider['url'] = url

        # Iterate modules, then classes, then methods
        for mod in direct_mods:
            if inspect.ismodule(mod):
                for name, obj in inspect.getmembers(mod):
                    if inspect.isclass(obj):
                        if hasattr(obj, '_is_ext'):
                            classes[name] = []
                            for m_name, m_obj in inspect.getmembers(obj):
                                if inspect.isfunction(m_obj):
                                    if hasattr(m_obj, '_is_ext'):
                                        method = dict()
                                        method['name'] = m_name
                                        method['len'] = len(inspect.getargspec(
                                                            m_obj)[0])-1
                                        classes[name].append(method)
        # At this point the provider dict is complete
        provider['actions'] = classes

        # This is what Sencha Architect expects. I deliver!
        if 'format' in request.REQUEST and request.REQUEST['format'] == 'json':
            js_content = 'Ext.require(\'Ext.direct.*\');' + \
            'Ext.namespace(\'' + namespace + '\');'+ namespace + \
            '.REMOTING_API = ' + json.dumps(provider,
                                            default=datetime_iso) + ';'
        else:
            # Browser/regular .js
            js_content = 'Ext.direct.Manager.addProvider(' + \
            json.dumps(provider, default=datetime_iso) + ');'

        return HttpResponse(js_content, content_type="application/javascript")

    @staticmethod
    def getApi(namespace='Directly', apis=[], url='/directly'):
        """
        Returns modified function, so we can use it in the urls config
        """
        return lambda request, *args: Ext.generateApi(
                                        namespace, apis, url, request)
    
    @staticmethod
    def rpc(apis=[], debug=False, exempt=True):
        """
        Used to bind in urls.
        exempt = False to keep the CSRF_TOKEN
        """
        if type(exempt) == bool and exempt:
            return csrf_exempt(
                lambda request, *args, **kwargs: Ext.use(request, apis, debug))
        else:
            return (
                lambda request, *args, **kwargs: Ext.use(request, apis, debug)

    @staticmethod
    def method(method):
        """
        Wrapper for Ext-Methods, so only expose those in the API
        """
        if inspect.isfunction(method):
            args, vargs, kw, defs = inspect.getargspec(method)
            # We always deliver the HttpRequest to the first parameter
            if len(args) >= 1:
                method._is_ext = True
            else:
                raise ExtDirectlyMethodException(method)
        return method

    @staticmethod
    def cls(clss):
        """
        Wrapper for Ext-Classes, so we only expose those in the API
        """
        if inspect.isclass(clss):
            clss._is_ext = True
        return clss
