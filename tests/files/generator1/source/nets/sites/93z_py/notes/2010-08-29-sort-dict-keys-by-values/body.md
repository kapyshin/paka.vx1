Can we actually sort a Python’s dict? No, but we can sort a list that
contains its keys and values.

A simplest way to do this is to use a `sort` method:

```pycon
>>> d = {'c': 100, 'a': 0, 'b': 10}
>>> items = d.items()
>>> items.sort(lambda x, y: cmp(x[1], y[1]))
>>> items
[('a', 0), ('b', 10), ('c', 100)]
```

We can use a `key` argument to make function call a bit shorter:

```pycon
>>> items = d.items()
>>> items.sort(key=lambda i: i[1])
>>> items
[('a', 0), ('b', 10), ('c', 100)]
```

Also we can use a [`sorted`](http://docs.python.org/2.7/library/functions.html#sorted)
built-in:

```pycon
>>> sorted(d.iteritems(), key=lambda i: i[1])
[('a', 0), ('b', 10), ('c', 100)]
```

But what if we care about speed?
[According to Gregg Lind](http://writeonly.wordpress.com/2008/08/30/sorting-dictionaries-by-value-in-python-improved/),
the fastest solution uses
[`operator.itemgetter`](http://docs.python.org/2.7/library/operator.html#operator.itemgetter)
(that is suggested in [PEP 265](http://www.python.org/dev/peps/pep-0265/)
named “Sorting Dictionaries by Value”) instead of lambda function:

```pycon
>>> from operator import itemgetter
>>> sorted(d.iteritems(), key=itemgetter(1))
[('a', 0), ('b', 10), ('c', 100)]
```

This version is 10x faster than first three.
