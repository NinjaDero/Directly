# Directly

[Apply Directly to the Django][1].

---

## About
Directly is a simplified ExtDirect implementation for Django apps using an ExtDirect frontend.
My goal with this project was to make ExtDirect as easy as possible to use with Django, with the least amount of editing required.

The idea is fairly simple, so let's keep this module simple!

* Write a function in python
* Call it in JavaScript as if it was a JavaScript function

If you're new to Django/ExtJS development and want to get into ExtDirect as fast as possible, this might be perfect for you.


### Developed and tested with:
* Python 2.7.6
* Django 1.6.5
* ExtJS 4.2


### Files to edit
ExtDirect is supposed to be an interface between your server and your ExtJS app.
That's why I want to stay out of views or settings. All redirecting is done through the **urls.py**.
Obviously you'd need to write your python functions to call and the ExtJS part that calls them. But other than that, there is no special treatment for your existing Django project required.

If you're new to ExtDirect and/or Django, read below. Otherwise scroll to the bottom of this file for a short summary.

---

## Using Directly in 4 steps

#### ======= 1: Create your backend functions =======
Create a new python file in your app folder to write your functions into.
In this example I will be creating a collections of functions to log the user in, out and retrieve their username.
I'll just call it **users.py**.

In Directly we separate our namespaces by classes.
The **UserAuth** class will be the one to call if I need to log in or out.
The **UserStuff** class will be responsible for additional goodies, like getting the user's username.
```python
# file: django_project/app/users.py

class UserAuth():
    @staticmethod
    def log_in(request, username, password):
        status = login(username, password)
        return status
    
    @staticmethod
    def log_out(request):
        return logout(request.user)

class UserStuff():
    @staticmethod
    def get_username(request):
        return request.user.username

```
All methods need the `@staticmethod` decoration, since they're standalone functions. We will not be using the classes in the 'traditional' way.
Also, you get the `HttpRequest` like you usually do in your *views*, so your methods need at least one parameter, which will be the request, conveniently, also called `request`.
Just imagine the functions `login()` and `logout()` actually exist and do log the user in and out.

---
#### ======= 2: Decorate your methods to expose them =======
Import **Directly** to your *users.py*
All you really need is in the Ext class:
`from Directly import Ext`

Decorate your classes with `Ext.cls` and methods with `Ext.method`.
This way, only the methods you want to be exposed to ExtJS will be exposed.
All classes and methods without decoration will be ignored when creating the API, so you won't be able to access them from ExtJS.
Here's the code from above with decorations.
```python
# file: django_project/app/users.py

from Directly import Ext

@Ext.cls
class UserAuth():
    @staticmethod
    @Ext.method
    def log_in(request, username, password):
        status = login(username, password)
        return status
    
    @staticmethod
    @Ext.method
    def log_out(request):
        return logout(request.user)

@Ext.cls
class UserStuff():
    @staticmethod
    @Ext.method
    def get_username(request):
        return request.user.username

```
Please note that `@Ext.method` goes *below* `@staticmethod`.

---
#### ======= 3: Get the API =======
In your main *urls.py*, redirect whatever you want to be the access point to your API to `Ext.getApi()`.
```python
# file: django_project/app/urls.py

from Directly import Ext
from app import users

urlpatterns = patterns('',
    # ... Other patterns
    url(r'^userAPI.js', Ext.getApi(namespace='SuperApp', apis=[users], url='/user')),
)
```
The API will now be accessible at `yourdomain/userAPI.js`.
It doesn't have to be a `.js` extension, since it's not really a file behind it, but it seems to make more sense. ;)
Arguments:
`namespace`: The name at which you can call your classes. Defaults to `Directly`
`apis`: Your module(s) (files), cointainung your classes. It can be either a single one, or a list/tuple of modules.
`url`: The url where all ExtDirect calls using your API will be sent to.

Import the js in your html template.
```html
...
<head>
    <script type="text/javascript" src="userAPI.js"></script>
</head>
...
```
---
#### ======= 4: Catch your calls =======
You can already use your functions, but they will throw a 404 error, because Django doesn't know how to deal with a request to the provided `url`.

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
Arguments:
`apis`: Again, a list of modules with your classes. It doesn't have to be the same as the ones in Ext.getApi, so you can split your API and process different methods on different URLs.

---
That's it.

Now, to log in with this example in ExtJS, you can use the API like it's a JS function.
You need Ext.direct.* imported manually, if you're working with Architect.
For more information on where to replace your Ajax-calls with ExtDirect, check the [sencha examples][2].

Use them like `Namespace.Class.method(*arguments*, callback_function)`.
```javascript
// Some JS or chrome-console
SuperApp.UserAuth.log_in('admin', 'password123', function(val) {
    if(val === true) {
        console.log("You are now logged in!");
    }
});
SuperApp.UserStuff.get_username(function(val) {
    console.log("Logged in as " + val);
});
```
---

## What else?

`Ext.rpc` currently takes two optional arguments:
`debug`: True/False/Function - Prints every RPC object to console if True, or calls a function providing the RPC object as an argument. Defaults to *False*.
`exempt`: True/False - Does not decorate with [csrf_exempt][3] if False. You need to handle it yourself if you want to use it. Defaults to *True* for simplicity.

---

### Short summary for experienced users
(or if you can't be bothered reading 180 readme-lines...)

##### Write Classes with static methods and decorate them using `Ext.cls` and `Ext.method` to expose them to the API:
```python
# file: project/app/direct.py
from Directly import Ext

@Ext.cls
class A():
    @staticmethod
    @Ext.method
    def b(request):
        return True
```
At least one argument is required for the request.

##### Forward a request to the api to `Ext.getApi`, include it in your template and handle the url by forwarding it to `Ext.rpc`. Both need a list of modules with your python classes.
```python
# file: project/app/urls.py
from Directly import Ext
from app import direct
    # ...
    url(r'^api.js', Ext.getApi(namespace='ExtNamespace', apis=[direct], url='/direct/something')),
    url(r'^direct/something', Ext.rpc(apis=[direct])),
```

##### Use it
```javascript
// console
ExtNamespace.A.b(function(ret) {
    console.log(ret);
});
```

Dun.

  [1]: http://en.wikipedia.org/wiki/HeadOn "(It's a joke)"
  [2]: http://docs.sencha.com/extjs/4.2.2/#!/example/direct/direct.html
  [3]: https://docs.djangoproject.com/en/1.6/ref/contrib/csrf/
