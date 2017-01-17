import enum
import collections

from . import errorpages
from . import features


_NONE_AT_ALL = object()


_RoutesMap = collections.namedtuple(
    "_RoutesMap",
    [
        "add_route", "find_route_by_view_name", "check_routes",
        "check_for_untouched_routes", "format_url_path", "get_lineage"])
_Route = collections.namedtuple(
    "_Route", [
        "url_path_tmpl", "view_name", "template_name", "fmt",
        "touch_marker", "parent_view_name"])
Fmt = enum.Enum("Fmt", {"html": "html", "atom": "atom", "direct": None})


def make_routes_map(error_callback):
    routes = []
    def _add_route(
            url_path_tmpl, view_name, template_name, fmt,
            parent_view_name):
        route = _Route(
            url_path_tmpl=url_path_tmpl, view_name=view_name,
            template_name=template_name, fmt=fmt, touch_marker=[],
            parent_view_name=parent_view_name)
        routes.append(route)
    def _find_route_by_view_name(view_name, touch=False):
        for route in routes:
            if route.view_name == view_name:
                if touch and not route.touch_marker:
                    route.touch_marker.append(1)
                return route
    def _check_routes():
        for route in routes:
            if not route.url_path_tmpl.startswith("/"):
                error_callback(
                    "{!r} route does not start with slash!".format(
                        route.view_name))
            # Check parent exists.
            parent_view_name = route.parent_view_name
            if parent_view_name:
                if parent_view_name is _NONE_AT_ALL:
                    continue
                found = _find_route_by_view_name(parent_view_name)
                if not found:
                    error_callback(
                        "{!r} route has non-existing parent ({!r})!".format(
                            route.view_name, parent_view_name))
    def _check_for_untouched_routes():
        for route in routes:
            if len(route.touch_marker) < 1:
                error_callback(
                    "{!r} route is not touched!".format(route.view_name))
    def _format_url_path(view_name, context=None):
        route = _find_route_by_view_name(view_name)
        return route.url_path_tmpl.format(**(context or {}))
    def _get_lineage(route):
        if route.parent_view_name is _NONE_AT_ALL:
            return []
        collected = []
        current_route = route
        while current_route:
            collected.append(current_route)
            parent_view_name = current_route.parent_view_name
            if not parent_view_name:
                break
            current_route = _find_route_by_view_name(parent_view_name)
        return reversed(collected)
    return _RoutesMap(
        add_route=_add_route,
        find_route_by_view_name=_find_route_by_view_name,
        check_routes=_check_routes,
        check_for_untouched_routes=_check_for_untouched_routes,
        format_url_path=_format_url_path,
        get_lineage=_get_lineage)


def add_routes(routes_map, feature_checker):
    routes_map.add_route(
        "/tags/{tag.slug}/feed/", view_name="recent_tag_notes_feed",
        template_name="notes_feed.mako", fmt=Fmt.atom,
        parent_view_name=_NONE_AT_ALL)
    routes_map.add_route(
        "/tags/{tag.slug}/", view_name="one_tag",
        template_name="one_tag.html", fmt=Fmt.html,
        parent_view_name="all_tags")
    routes_map.add_route(
        "/tags/", view_name="all_tags",
        template_name="all_tags.html", fmt=Fmt.html, parent_view_name="home")
    routes_map.add_route(
        "/notes/{note.slug}/", view_name="one_note",
        template_name="one_note.html", fmt=Fmt.html, parent_view_name="all_notes")
    routes_map.add_route(
        "/notes/feed/", view_name="recent_notes_feed",
        template_name="notes_feed.mako", fmt=Fmt.atom,
        parent_view_name=_NONE_AT_ALL)
    routes_map.add_route(
        "/notes/", view_name="all_notes",
        template_name="all_notes.html", fmt=Fmt.html, parent_view_name="home")
    if feature_checker(features.Feature.about):
        routes_map.add_route(
            "/about/", view_name="about",
            template_name="about.html", fmt=Fmt.html, parent_view_name="home")
    routes_map.add_route(
        "/", view_name="home",
        template_name="home.html", fmt=Fmt.html, parent_view_name=None)
    routes_map.add_route(
        "/robots.txt", view_name="robots_txt",
        template_name="robots.txt", fmt=Fmt.direct,
        parent_view_name=_NONE_AT_ALL)
    for code in errorpages.CODES:
        view_name = errorpages.make_view_name(code)
        template_name = "{}.html".format(view_name)
        routes_map.add_route(
            errorpages.make_url_path(code), view_name=view_name,
            template_name=template_name, fmt=Fmt.html, parent_view_name=None)
