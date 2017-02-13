import collections

import mako.lookup
import mako.template
from paka import cmark
from paka.webstatic.htmlmin import htmlmin


_TemplatePath = collections.namedtuple(
    "_TemplatePath", ["prepended", "internal", "appended"])


def make_renderer(charset, prepended, internal, appended):
    templatepath = _TemplatePath(
        prepended=list(prepended), internal=list(internal),
        appended=list(appended))
    return _Renderer(charset, templatepath)


class _Renderer(object):

    def __init__(self, charset, templatepath):
        directories = []
        for part in templatepath:
            directories.extend(part)
        self._template_lookup = mako.lookup.TemplateLookup(
            directories=directories, input_encoding=charset,
            output_encoding=charset, default_filters=["decode.utf8"],
            filesystem_checks=False, strict_undefined=True)
        self._charset = charset

    def __call__(self, template_name, **kwargs):
        template = self._template_lookup.get_template(template_name)
        return htmlmin(template.render(**kwargs).decode(self._charset))

    def render_text(self, text, **kwargs):
        return htmlmin(
            mako.template.Template(
                text, lookup=self._template_lookup).render(**kwargs))

    def render_markdown(self, text):
        return htmlmin(cmark.to_html(text))
