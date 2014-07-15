# Directly

[Apply Directly to the Django][1].

---

## About
Directly is a simplified ExtDirect implementation for Django apps.
My goal with this project was to make ExtDirect as easy as possible to use with Django, while including only the most needed features of the specification (in my opinion).

While there are already many awesome implementations on Github, most of them require the developer to read a wiki or analyze the demo project to understand how it works and why.

The idea is fairly simple.

* Write a function in python
* Call it in JavaScript as if it was a JavaScript function

This module is aimed for *simple* Django apps, or developers new to Django/ExtJS


### Developed and tested with:
* Python 2.7.6
* Django 1.6.5
* ExtJS 4.2


### Files to edit
I want to stay out of your views and settings, so all Directly needs is your **urls.py**.

If you're new to ExtDirect and/or Django, read below. Otherwise scroll to the bottom of this file for a short summary.

---

## Using Directly in 4 steps

#### ======= 1 =======
Create a python file in your app folder and call it something that makes sense.
I'll just call it **users.py** for this example. This file will hold methods to log a user in and out, and get his username.
ExtDirect separates *methods* by putting them in *actions*.
Sounds like classes and methods, so that's exactly what we're going to do with our new module.
```python
# file: django_project/app/users.py

class UserAuth():
    @staticmethod
    def log_in(request, username, password):
        status = complicated_process(username, password)
        return status
    
    @staticmethod
    def log_out(request):
        return more_code(request.user)

class UserStuff():
    @staticmethod
    def get_username(request):
        return request.user.username

```
All methods need the `@staticmethod` decoration, since we're not really using the classes to create objects, but just to separate things a little bit.
Also, you get the `HttpRequest` like you do in your *views*, so your methods need at least one parameter, which will be the request.
Just imagine the functions `complicated_process()` and `more_code()` actually exist and do log the user in and out.

---
#### ======= 2 =======
Import **Directly** to your *users.py*
All you really need is in the Ext class:
`from Directly import Ext`

Decorate your classes with `Ext.cls` and methods with `Ext.method`.
This way, only the methods you want to be exposed to ExtJS will be exposed.
Here's the code from above with decorations.
```python
# file: django_project/app/users.py

from Directly import Ext

@Ext.cls
class UserAuth():
    @staticmethod
    @Ext.method
    def log_in(request, username, password):
        status = complicated_process(username, password)
        return status
    
    @staticmethod
    @Ext.method
    def log_out(request):
        return more_code(request.user)

@Ext.cls
class UserStuff():
    @staticmethod
    @Ext.method
    def get_username(request):
        return request.user.username

```
Please note that `@Ext.method` goes *below* `@staticmethod`.

---
#### ======= 3 =======
To use your code in the browser, you need to add a new URL to your *urls.py*.
Pick a name and redirect it to Ext.getAPI():

```python
# file: django_project/app/urls.py

from Directly import Ext
from app import users

urlpatterns = patterns('',
    # ... Other patterns
    url(r'^userAPI.js', Ext.getApi(namespace='SuperApp', apis=[users], url='/user')),
)
```
The `namespace` is the name at which you can call your actions.
Import your module(s) and add them to the `apis` parameter. It can be either one, or a list/tuple.
All function calls will be redirected to the url in the `url` parameter.

Import the js in your html template. It doesn't have to be a .js, but it makes more sense.
```html
...
<head>
    <script type="text/javascript" src="userAPI.js"></script>
</head>
...
```
---
#### ======= 4 =======
You can already use your functions, but they will go nowhere, because Django doesn't know how to deal with a request to */user*.

Add another line to the *urls.py* and redirect the url you've chosen above to `Ext.rpc()`.

```python
# file: django_project/app/urls.py

from Directly import Ext
from app import users

urlpatterns = patterns('',
    # ... Other patterns
    url(r'^userAPI.js', Ext.getApi(namespace='SuperApp', apis=[users], url='/user')),
    
    url(r'^user', Ext.rpc(apis=[users])),
)
```
The only argument here is, again, a single module or a list/tuple of your ExtDirect modules.

---
That's it.

Now, to log in with this example in ExtJS, you can use the API like it's a JS function.
For more information on where to replace your Ajax-calls with ExtDirect, check the [sencha examples][2].
```javascript
// Some JS or chrome-console
SuperApp.UserAuth.log_in('admin', 'password123', function(val) {
    if(val === true) {
        console.log("Yay!");
    }
})
```
---

## What else?

All calls are automatically csrf_exempt decorated. So if you want to use the token, you might need to tweak around a little bit.

---

## Short summary for experienced people

### Use decorators:
```python
from Directly import Ext

@Ext.cls
class A():
    @staticmethod
    @Ext.method
    def b(request):
        return None
```

### Use urls
```python
    url(r'^api.js', Ext.getApi(namespace='ExtNamespace', apis=[module], url='/direct/something')),
    url(r'^direct/something', Ext.rpc(apis=[module])),
```

Dun.

  [1]: http://en.wikipedia.org/wiki/HeadOn "(It's a joke)"
  [2]: http://docs.sencha.com/extjs/4.2.2/#!/example/direct/direct.html
