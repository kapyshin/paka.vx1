Some developers I know think that [Mako](http://makotemplates.org/)
templating library is “less secure” than, for example, Jinja2 (and,
therefore, “must not be used”). Actually, Mako is as “secure” as
you’ll configure it.

Though by default Mako does not HTML-escape rendered expressions, it
can be configured to do that. When you create lookup (an instance of
`mako.lookup.TemplateLookup`), you may pass arguments: list of
directories to search for templates, encoding of templates, etc.
Usually it looks like this:

```python3
import mako.lookup


lookup = mako.lookup.TemplateLookup(
    directories=[os.path.join(..., "templates")],
    input_encoding="utf-8",
    filesystem_checks=False,
    strict_undefined=True)
```

So, how to make lookup, as constructed above, escape rendered expressions?
In addition to aforementioned arguments, `TemplateLookup` accepts
`default_filters`—a list of filters to use on expressions by default:

```python3
import mako.lookup


lookup = mako.lookup.TemplateLookup(
    directories=[os.path.join(..., "templates")],
    input_encoding="utf-8",
    filesystem_checks=False,
    strict_undefined=True,
    default_filters=["h"])
```

For example, `pyramid_mako` uses `default_filters=["h"]` by default,
so if you’re user of Pyramid framework you may have one less thing to worry about.

Why not `default_filters=["str", "h"]`? It may seem to work, but not for
objects with `__html__` method: these will be treated as text that needs escaping,
not HTML that should be rendered as-is. Default filters are applied from left
to right, so `${form.somefield()}` will be transformed, roughly speaking, into
`h(str(form.somefield()))`—which is, basically, `h(form.somefield().__str__())`.
As you can clearly see, `form.somefield().__html__` will not be called if
`default_filters` are defined as `["str", "h"]`.
