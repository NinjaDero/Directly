#################################################
#
# Author: Alex Mannhold / Ninjadero
#
# Comments:
# Well, I was tired of outdated implementations,
# so I made my own outdated implementation!
# This is developed for personal use in mind.
# I don't take any responsibility. AT ALL.
#
#################################################

import json
import inspect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


ExtJson = (lambda obj:
                    obj.isoformat() if isinstance(obj, datetime) else None)


class ExtDirectlyException(Exception):
    def __init__(self, message):
        self.__value = message

    def __str__(self):
        return repr(self.__value)

class ExtDirectlyMethodException(Exception):
    def __init__(self, method):
        msg = 'Method \'{0}\' decorated, but does '.format(method.__name__) + \
              'not have \'request\' parameter set.'
        self.__value = msg

    def __str__(self):
        return repr(self.__value)

class DirectlyClass():
    """
    Alternative to class decorator. All we need is that tag.
    """
    is_ext = True
    # Hide 'missing init' warnings...
    def __init__(self): pass

class Ext():
    @staticmethod
    def use(request, direct_mods):
        """
        Takes RPC from request and searches a list or tuple direct_mods
        for ExtDirect classes and methods to take.
        """
        try:
            rpc = json.loads(request.body)
        except ValueError:
            # Probably not RPC... direct call in browser?
            # TODO: Figure out what to return in this case
            return HttpResponse(
                content=json.dumps(None),
                content_type='application/json')

        # In case we want to include multiple 
        # modules from different apps
        if type(direct_mods) not in [tuple, list]:
            direct_mods = [direct_mods]

        content = list()

        # We care if it's a RPC, otherwise *meh*
        # Extract usefull information
        if rpc['type'] == 'rpc':
            action = rpc['action']
            method = rpc['method']
            data = rpc['data']
            tid = rpc['tid']

            # Give that usefull information to something to use it
            method_return = Ext.getMethod(
                            direct_mods, action, method, data, request)
            # Build answer
            answer_rpc = dict(type='rpc', tid=tid,
                              action=action, method=method)
            if method_return is not None:
                answer_rpc['result'] = method_return

            content.append(answer_rpc)
        # Now send back that stuff... Or an empty list, 
        # if the request was not a RPC
        return HttpResponse(
                content=json.dumps(content, default=ExtJson),
                content_type='application/json')

    @staticmethod
    def getMethod(direct_mods, action, method, data, request):
        """
        Uses the extracted data, iterates through the modules and
        calls the correct method if found.
        """
        for mod in direct_mods:
            for name, obj in inspect.getmembers(mod):
                if inspect.isclass(obj):
                    if name == action:
                        for m_name, m_obj in inspect.getmembers(obj):
                            if inspect.isfunction(m_obj):
                                if m_name == method:
                                    # Method found, call someone to use it
                                    return Ext.useMethod(m_obj, data, request)
        # Worst case scenario, nothing found. Wrong API?
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
            # TODO: throw exception, user obviously screwed up
        elif len(data) > len(args) - 1:
            # Too many args, cut off the last ones and use it anyway...
            # TODO: Maybe exception?
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
            direct_mods = tuple(direct_mods)

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
                        if hasattr(obj, 'is_ext'):
                            classes[name] = list()
                            for m_name, m_obj in inspect.getmembers(obj):
                                if inspect.isfunction(m_obj):
                                    if hasattr(m_obj, 'is_ext'):
                                        method = dict()
                                        method['name'] = m_name
                                        method['len'] = len(inspect.getargspec(
                                                            m_obj)[0])-1
                                        classes[name].append(method)
        # At this point the provider dict is complete
        provider['actions'] = classes

        # This is what Sencha Architect expects. I deliver!
        if 'format' in request.REQUEST and request.REQUEST['format'] == 'json':
            js_content = 'Ext.require(\'Ext.direct.*\'); \
            Ext.namespace(\''+ namespace +'\');'+ namespace + '. \
            REMOTING_API = ' + json.dumps(provider, default=ExtJson) + ';'
        else:
            # Browser/regular .js
            js_content = 'Ext.direct.Manager.addProvider(' + \
            json.dumps(provider, default=ExtJson) + ');'

        return HttpResponse(js_content, content_type="application/javascript")

    @staticmethod
    def getApi(namespace='Directly', apis=[], url='/directly'):
        """
        Returns modified function, so we can use it in the urls config
        """
        return lambda request, *args: Ext.generateApi(
                                        namespace, apis, url, request)
    
    @staticmethod
    def rpc(apis=[]):
        """
        Used to bind in urls.
        Will basically return an anonymous csrf_exempt-decorated Ext.use
        """
        return csrf_exempt(
               lambda request, *args, **kwargs: Ext.use(request, apis))

    @staticmethod
    def method(method):
        """
        Wrapper for Ext-Methods, so only expose those in the API
        """
        if inspect.isfunction(method):
            args, vargs, kw, defs = inspect.getargspec(method)
            # We can not know if the user wants the request or not.
            # We'd have three options:
            # 1. ALWAYS fill first parameter with request, 
            #    no matter what the name is
            # 2. Check if request parameter is set and provide, 
            #    otherwise don't
            # 3. 'hardcode' request parameter requirement [x]
            if len(args) >= 1 and args[0] == 'request':
                method.is_ext = True
            else:
                raise ExtDirectlyMethodException(method)
        return method

    @staticmethod
    def action(cls):
        """
        Wrapper for Ext-Classes, so we only expose those in the API
        """
        if inspect.isclass(cls):
            cls.is_ext = True
        return cls
