Recently I’ve been working towards making builds of this blog reproducible.
My goal was to allow use of regular `diff` for spotting differences between
resulting files.

But there was a problem. [Atom 1.0](https://tools.ietf.org/html/rfc4287)
feeds (e.g., [/notes/feed/](/notes/feed/), [/tags/django/feed/](/tags/django/feed/))
are generated with my fork of `django.utils.feedgenerator`.
Both original and fork use `xml.sax.saxutils.XMLGenerator`
(implementation of
[`ContentHandler`](https://docs.python.org/3.4/library/xml.sax.handler.html#xml.sax.handler.ContentHandler)
interface) subclass called
`SimplerXMLGenerator` for XML generation, and both pass elements’
attributes into
[`startElement`](https://docs.python.org/3.4/library/xml.sax.handler.html#xml.sax.handler.ContentHandler.startElement)
and
[`startElementNS`](https://docs.python.org/3.4/library/xml.sax.handler.html#xml.sax.handler.ContentHandler.startElementNS)
as regular `dict`s. This caused random ordering of XML elements’ attributes
in resulting feeds: textually feeds were changing, while semantically
they were not. Despite being inconvenient for my use case (when use of
specialized tools for XML comparison is undesirable), such behavior is,
according to [specification](https://www.w3.org/TR/2008/REC-xml-20081126/#sec-starttags),
valid:

> Note that the order of attribute specifications in a start-tag or
> empty-element tag is not significant.

So I decided to take advantage of that. Both `startElement` and `startElementNS`
methods assume that `attrs` argument is an object that behaves like mapping
(see lines
[170](https://hg.python.org/cpython/file/dfc57c66a670/Lib/xml/sax/saxutils.py#l170)
and
[195](https://hg.python.org/cpython/file/dfc57c66a670/Lib/xml/sax/saxutils.py#l195)
of `Lib/xml/sax/saxutils.py`).
[`OrderedDict`](https://docs.python.org/3.4/library/collections.html#collections.OrderedDict)
is a mapping (like `dict` is), therefore it is possible to provide `attrs` (attributes
of XML element) as an instance of `OrderedDict` to preserve order of attributes.
Least intrusive change—it’s a fork, after all—is to override two mentioned methods
and sort `attrs` there (`_order_attrs`) before passing to implementation of superclass
(`XMLGenerator`):

```python3
import operator
import collections
from xml.sax.saxutils import XMLGenerator


_order_attrs_key = operator.itemgetter(0)


def _order_attrs(attrs):
    return collections.OrderedDict(
        sorted(attrs.items(), key=_order_attrs_key))


class SimplerXMLGenerator(XMLGenerator):

    def startElement(self, name, attrs):
        return super().startElement(name, _order_attrs(attrs))

    def startElementNS(self, name, qname, attrs):
        return super().startElementNS(name, qname, _order_attrs(attrs))

    # ...here goes the rest (already present in feedgenerator)
```

That’s what I did. Now my blog engine does not randomly reorder attributes in feeds,
and the latter are still perfectly valid XML :).
