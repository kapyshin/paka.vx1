...at execution time, given that all you have is an instance of function
object:

```pycon3
>>> type(func)
<class 'function'>
```

Knowing where it is defined may save you some time during debugging session:
say, when you are not sure that function you are dealing with is imported from
“correct” location. Despite being easy, such sanity check may help.

Most obvious option is to use `co_filename` attribute of function’s code:

```pycon3
>>> func.__code__.co_filename
'/home/user/.../something.py'
```

This also may work with methods:

```pycon3
>>> class SomeClass:
...     def some_method(self):
...         pass
... 
>>> obj = SomeClass()
>>> obj.some_method.__code__.co_filename
'<stdin>'
>>> obj.some_method.__func__.__code__.co_filename
'<stdin>'
```

Usually it’s better to use `inspect.getsourcefile` (that uses `inspect.getfile`,
which uses something similar to above, but in more consistent way—for many different
types):

```pycon3
>>> import inspect
>>> inspect.getsourcefile(func)
'/home/user/.../something.py'
```

But if `func` is defined in CPython extension (that is shared library which uses C API),
`inspect.getsourcefile` will fail with `TypeError`:

```pycon3
>>> inspect.getsourcefile(func)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/user/.../lib/python3.4/inspect.py", line 571, in getsourcefile
    filename = getfile(object)
  File "/home/user/.../lib/python3.4/inspect.py", line 536, in getfile
    'function, traceback, frame, or code object'.format(object))
TypeError: <built-in function func> is not a module, class, method, function, traceback, frame, or code object
```

In such case it is still possible to get file path of `.so`:

```pycon3
>>> inspect.getfile(inspect.getmodule(func))
'/home/user/.../lib/python3.4/site-packages/something.cpython-34m.so'
```
