import collections

import mako.lookup
import mako.template
from paka import cmark
from paka.webstatic.htmlmin import htmlmin


_TemplatePath = collections.namedtuple(
    "_TemplatePath", ["prepended", "internal", "appended"])


def make_templatepath(prepended, internal, appended):
    return _TemplatePath(
        prepended=list(prepended),
        internal=list(internal),
        appended=list(appended))


def make_renderer(templatepath, charset):
    directories = []
    for part in templatepath:
        directories.extend(part)
    template_lookup = mako.lookup.TemplateLookup(
        directories=directories,
        input_encoding=charset,
        output_encoding=charset,
        default_filters=["decode.utf8"],
        filesystem_checks=False,
        strict_undefined=True)
    def render(template_name, **kwargs):
        template = template_lookup.get_template(template_name)
        return htmlmin(template.render(**kwargs).decode(charset))
    def _render_text(text, **kwargs):
        return htmlmin(
            mako.template.Template(
                text, lookup=template_lookup).render(**kwargs))
    def _render_markdown(text):
        return htmlmin(cmark.to_html(text))
    render.render_text = _render_text
    render.render_markdown = _render_markdown
    return render
