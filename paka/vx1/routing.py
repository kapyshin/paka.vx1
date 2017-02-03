import enum
import collections

from . import errorpages
from . import features


NONE_AT_ALL = object()


_Route = collections.namedtuple(
    "_Route", [
        "url_path_tmpl", "view_name", "template_name", "fmt",
        "touch_marker", "parent_view_name"])
Fmt = enum.Enum("Fmt", {"html": "html", "atom": "atom", "direct": None})


class Map(object):

    def __init__(self, error_callback):
        self._error_callback = error_callback
        self._routes = []

    def add_route(
            self, url_path_tmpl, view_name, template_name, fmt,
            parent_view_name):
        route = _Route(
            url_path_tmpl=url_path_tmpl, view_name=view_name,
            template_name=template_name, fmt=fmt, touch_marker=[],
            parent_view_name=parent_view_name)
        self._routes.append(route)
        return route

    def find_route_by_view_name(self, view_name, touch=False):
        for route in self._routes:
            if route.view_name == view_name:
                if touch and not route.touch_marker:
                    route.touch_marker.append(1)
                return route

    def check_routes(self):
        for route in self._routes:
            if not route.url_path_tmpl.startswith("/"):
                return self._error_callback(
                    "{!r} route does not start with slash!".format(
                        route.view_name))
            # Check parent exists.
            parent_view_name = route.parent_view_name
            if parent_view_name:
                if parent_view_name is NONE_AT_ALL:
                    continue
                found = self.find_route_by_view_name(parent_view_name)
                if not found:
                    return self._error_callback(
                        "{!r} route has non-existing parent ({!r})!".format(
                            route.view_name, parent_view_name))

    def check_for_untouched_routes(self):
        for route in self._routes:
            if len(route.touch_marker) < 1:
                return self._error_callback(
                    "{!r} route is not touched!".format(route.view_name))

    def format_url_path(self, view_name, context=None):
        route = self.find_route_by_view_name(view_name)
        return route.url_path_tmpl.format(**(context or {}))

    def get_lineage(self, route):
        parent_view_name = route.parent_view_name

        # Lineage concept is not applicable.
        if parent_view_name is NONE_AT_ALL:
            return []

        # Route has no parent.
        if not parent_view_name:
            return [route]

        # There is at least one parent.
        collected = []
        while parent_view_name:
            collected.append(route)
            parent_view_name = route.parent_view_name
            route = self.find_route_by_view_name(parent_view_name)
        return reversed(collected)


def add_routes(routes_map, feature_checker):
    routes_map.add_route(
        "/tags/{tag.slug}/feed/", view_name="recent_tag_notes_feed",
        template_name="notes_feed.mako", fmt=Fmt.atom,
        parent_view_name=NONE_AT_ALL)
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
        parent_view_name=NONE_AT_ALL)
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
        parent_view_name=NONE_AT_ALL)
    for code in errorpages.CODES:
        view_name = errorpages.make_view_name(code)
        template_name = "{}.html".format(view_name)
        routes_map.add_route(
            errorpages.make_url_path(code), view_name=view_name,
            template_name=template_name, fmt=Fmt.html, parent_view_name=None)
