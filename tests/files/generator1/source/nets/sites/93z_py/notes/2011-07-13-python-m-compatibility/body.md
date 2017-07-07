As we all know, `python -m name` (see
[interface options](http://docs.python.org/2.7/using/cmdline.html#using-on-interface-options))
can run module named `name` that is present in
[`PYTHONPATH`](http://docs.python.org/2.7/using/cmdline.html#envvar-PYTHONPATH). Also it
can run package, if there is `__main__` module inside of that package (actually, it will run that module).

Running module with `python -m` in Python ≥ 2.4 is okay. But beware of running **packages** this way
in Python 2.4, 2.5 and 2.6.
