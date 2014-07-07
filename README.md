# Directly

ExtDirect Django module

---

One of many ExtDirect Python implementations for Django.
Create your functions and generate an API to use in your ExtJS powered Django projects.

This is an early version, not everything is well tested, and there's no events.<br/>
This is developed for personal use in mind.
If something is missing, it's probably because I didn't need it yet, or didn't bother implementing. Some stuff might not work as expected from an ExtDirect backend. Please keep that in mind, when using this module.

### Developed and tested with:
* Python 2.7.6
* Django 1.6.5
* ExtJS 4.2

---

## Using Directly
#### Create your python backend
Create a file in your app directory and name it something easy, for example `direct.py`.<br/>
Write your classes and methods in here.<br/>
You can create multiple files and split up your code.

#### Decorate your classes and methods
Import the Directly module at the top.<br/>
`from Directly import Ext`

Decorate your classes with `Ext.action` and methods with `Ext.method`.<br/>
It's action instead of class, because that's what ExtJS calls them, so it's less confusing.<br/>
Also, `class` is a reserved word in python, which I'd like to keep! ;)

Alternatively, inherit your class from `Directly.DirectlyClass`.

Here's an example with 1 API method and 2 private methods:
```python
# file: django_project/app/directly.py

from Directly import Ext
@Ext.action
class UserManagement():
    @staticmethod
    @Ext.method
    def logged_in(request):
        return request.user.is_authenticated()
    
    @staticmethod
    def not_included_in_api():
        pass
    
class AlsoNotIncluded():
    @staticmethod
    def calculate(x, y):
        return x + y
```

##### Important:
* Classes and methods not decorated with `Ext.action` or `Ext.method` are ignored in the API.
* All API methods need to be decorated with `@staticmethod`, otherwise they'll also be ignored!
* First argument of API methods needs to be `request`. This is where you get the request object.<br/>
Directly will throw an exception if `request` is not the first argument, or not present at all.<br/>

#### Generating API
To generate the API out of all this mess, add a new url to your main or app `urls.py`

```python
file: django_project/app/urls.py

from Directly import Ext
from app import direct
urlpatterns = patterns('',
    ...
    url(r'^api.js', Ext.getApi(namespace='ExtNamespace', apis=[direct], url='/something')),
)
```

Import Directly and all API files you created. In our case, it's only one: `direct.py`.<br/>
Create a regex to whatever you want your js file to be called, usually `api.js`<br/>
Forward the request to `Ext.getApi()`

Arguments:

* namespace: ExtJS Namespace, default = 'Directly'
* apis: one or a list/tuple of modules to include in that .js file. 
Please do not provide classes here.
* url: The URL the API will send the requests to. 
We need to catch and process them in the next step.


#### Processing procedure calls
Add another line to your urls, forwarding the url you entered in the API generation:

```python
file: django_project/app/urls.py

from Directly import Ext
from app import direct
urlpatterns = patterns('',
    ...
    url(r'^api.js', Ext.getApi(namespace='ExtNamespace', apis=[direct], url='/something')),
    
    url(r'^something', Ext.rpc(apis=[direct])),
)
```
Redirect it to `Ext.rpc()` with the API files you want to use for this particular URL.<br/>
You can add mupltiple redirects if you made more than one API, but you'll figure it out.

As with `getApi()`, the `apis` argument can be a list, tuple, or single module.


---

That's it.<br/>
The views file is not used here.

All calls are automatically csrf_exempt decorated. So if you want to use the token, you might need to tweak around a little bit.
