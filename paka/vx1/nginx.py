import os
import collections

from . import errorpages
from . import utils


_TEXT_CONTENT_TYPES = (
    "text/javascript",
    "application/javascript",
    "text/css",
    "application/atom+xml")
# ^ "text/html" is missing because it is added by nginx by default.
_BINARY_CONTENT_TYPES = ("image/x-icon", )
GZIPPED_CONTENT_TYPES = " ".join(
    (_TEXT_CONTENT_TYPES + _BINARY_CONTENT_TYPES))
CHARSET_CONTENT_TYPES = " ".join((_TEXT_CONTENT_TYPES))


Directive = collections.namedtuple(
    "Directive", ["name", "arg", "children", "level"])


def _get_servers(specs):
    def _end_slash(path):
        if not path.endswith("/"):
            return "".join((path, "/"))
        return path
    def mk(name, arg="", children=(), level=1):
        def _set_level(children, current_level):
            for ch in children:
                yield ch._replace(
                    level=current_level + 1,
                    children=list(_set_level(ch.children, current_level + 1)))
        children = list(_set_level(children, level))
        return Directive(name=name, arg=arg, children=children, level=level)
    for spec in sorted(specs, key=lambda spec: spec.site.slug):
        domain = spec.site.attrs["domain"]
        yield (
            mk("listen", "80"),
            mk("server_name", "www.{}".format(domain)),
            mk("return", "301 $scheme://{}$request_uri".format(domain)))
        yield (
            mk("listen", "80"),
            mk("server_name", domain),
            mk("root", spec.site_build_dir),
            mk("client_header_buffer_size", "1k"),
            mk("large_client_header_buffers", "4 8k"),
            mk("client_max_body_size", "1M"),
            mk("gzip", "on"),
            mk("gzip_disable", "msie6"),
            mk("gzip_types", GZIPPED_CONTENT_TYPES),
            mk("gzip_vary", "on"),
            mk("gzip_comp_level", "6"),
            mk("charset", "utf-8"),
            mk("source_charset", "utf-8"),
            mk("charset_types", CHARSET_CONTENT_TYPES),
            mk("error_log", "/var/log/nginx/error.log crit"),
            mk("access_log", "off"),
            mk(
                "location", "/", (
                    mk("root", spec.pages_build_dir),
                    mk("index", "index.html index.atom"),
                    mk("expires", "1d"),
                    mk("break"))),
            mk(
                "location", "/s/", (
                    mk("alias", _end_slash(spec.static_build_dir)),
                    mk("expires", "1d"),
                    mk("break"))),
        ) + tuple(
            mk(
                "error_page",
                "{} {}".format(code, errorpages.make_url_path(code)))
            for code in errorpages.CODES)


def _get_lines(directive):
    wsp = directive.level * "    "
    tmpl_prefix = "{wsp}{d.name}"
    if directive.arg:
        tmpl_prefix += " {d.arg}"
    if directive.children:
        yield (tmpl_prefix + " {{").format(d=directive, wsp=wsp)
        for child in directive.children:
            for line in _get_lines(child):
                yield line
        yield "{wsp}}}".format(wsp=wsp)
    else:
        yield (tmpl_prefix + ";").format(d=directive, wsp=wsp)


def build_nginx_config(specs, build_dir):
    nginx_config_path = os.path.join(build_dir, "etc", "nginx.conf")
    try:
        os.makedirs(os.path.dirname(nginx_config_path))
    except OSError:
        pass
    lines = []
    for server in _get_servers(specs):
        lines.append("server {")
        for directive in server:
            lines.extend(_get_lines(directive))
        lines.append("}\n")
    utils.write_file(nginx_config_path, "\n".join(lines))
