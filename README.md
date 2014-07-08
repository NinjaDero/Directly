# Directly

ExtDirect Django module

---

One of many ExtDirect Python implementations for Django.
Create your functions and generate an API to use in your ExtJS powered Django projects.

This project is still WIP.
Regular RPC are working fine so far, so if that's all you need, Directly might be interesting for you.

This is developed for personal use in mind. Please remember that, when using this module.

### Developed and tested with:
* Python 2.7.6
* Django 1.6.5
* ExtJS 4.2

---

## Files to edit
All you need to work with Directly, besides your classes and methods, is a minimum of <u>two</u> lines in your `urls.py`.
But let's start with the classes:

---

## Using Directly
#### Create your python backend
Create a file in your app directory and name it something easy, for example `direct.py`.
Write your classes and methods in here.
You can create multiple files and split up your code.

#### Decorate your classes and methods
Import the Directly module at the top.<br/>
`from Directly import Ext`

Decorate your classes with `Ext.cls` and methods with `Ext.method`.
Alternatively, inherit your class from `Directly.DirectlyClass`.

Here's an example with 2 API methods and a private (helper) method, that'll not be exported to the API:
```python
# file: django_project/app/directly.py

from Directly import Ext

@Ext.cls
class UserManagement():
    @staticmethod
    @Ext.method
    def logged_in(request):
        return request.user.is_authenticated()
    
    @staticmethod
    @Ext.method
    def add(request, num1, num2):
        return add_those(num1, num2)
        
    # Notice the missing decorator?
    @staticmethod
    def add_those(n1, n2):
        return n1 + n2

```

##### Important:
* Classes not decorated with `Ext.cls` completely ignored in the API.
* All API methods need to be decorated with `@staticmethod` and `Ext.method`, otherwise they'll also be ignored!
* First argument of API methods needs to be `request`. This is where you get the request object.
Directly will throw an exception if a method is decorated, but `request` is not the first argument, or not present at all.<br/>

#### Generating API
To generate the API out of all this mess, add a new url to your main or app `urls.py`

```python
# file: django_project/app/urls.py

from Directly import Ext
# The classes we created above
from apps import direct

urlpatterns = patterns('',
    ... # Other patterns
    url(r'^api.js', Ext.getApi(namespace='ExtNamespace', apis=[direct], url='/something')),
)
```

Import Directly and all API modules you created. In our case, it's only one: `direct.py`.<br/>
Create a regex to whatever you want your API to be delivered at. Usually it's something like `api.js`, but you can create multiple if you wish.
Don't forget to bind it to your html.
```html
...
<head>
    <script type="text/javascript" src="api.js"></script>
</head>
...
```
Forward the request to `Ext.getApi()`

Arguments:

* namespace: ExtJS Namespace, default = 'Directly'
* apis: one or a list/tuple of modules to include in that API call. 
Please do not provide single classes/methods here, I need modules.
* url: The URL the API will send the requests to. 
We need to catch and process them in the next step.


#### Processing procedure calls
Add another line to your urls, forwarding the url you entered in the API generation:

```python
# file: django_project/app/urls.py

from Directly import Ext
from apps import direct

urlpatterns = patterns('',
    ...
    # Line from above
    url(r'^api.js', Ext.getApi(namespace='ExtNamespace', apis=[direct], url='/something')),
    
    # Notice the regex and the url above!
    url(r'^something', Ext.rpc(apis=[direct])),
)
```
Redirect it to `Ext.rpc()` with the API modules you want to use for this particular URL.
You can add mupltiple redirects if you made more than one API, but you'll figure it out when you need it.

As with `getApi()`, the `apis` argument can be a list, tuple, or single module.


---

That's it.<br/>

All calls are automatically csrf_exempt decorated. So if you want to use the token, you might need to tweak around a little bit.
