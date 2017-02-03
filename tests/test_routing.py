import unittest


class Errback(object):

    def __init__(self):
        self._message = None
        self.was_called = False

    def __call__(self, message):
        self._message = message
        self.was_called = True

    @property
    def called_with(self):
        if not self.was_called:
            raise AttributeError("errback was not called")
        return self._message


class ErrbackTest(unittest.TestCase):

    def get_called_with(self, errback):
        return errback.called_with

    def test_not_called(self):
        errback = Errback()
        self.assertFalse(errback.was_called)
        with self.assertRaises(AttributeError):
            self.get_called_with(errback)

    def test_called(self):
        value = object()
        errback = Errback()
        errback(value)
        self.assertTrue(errback.was_called)
        self.assertIs(self.get_called_with(errback), value)


class MapTest(unittest.TestCase):

    def setUp(self):
        from paka.vx1 import routing

        self.routing = routing

    def make_map(self):
        errback = Errback()
        return self.routing.Map(error_callback=errback), errback

    def add_html_route(self, routes_map, url_path_tmpl, view_name, **kwargs):
        defaults = {
            "url_path_tmpl": url_path_tmpl,
            "view_name": view_name,
            "template_name": "{}.html".format(view_name),
            "fmt": self.routing.Fmt.html}
        return routes_map.add_route(**dict(defaults, **kwargs))

    def add_parents_chain(self, routes_map):
        home_route = self.add_html_route(
            routes_map, "/", view_name="home", parent_view_name=None)
        cat_route = self.add_html_route(
            routes_map, "/{cat_name}/", view_name="category",
            parent_view_name="home")
        obj_route = self.add_html_route(
            routes_map, "/{cat_name}/{obj_name}/", view_name="object",
            parent_view_name="category")
        return home_route, cat_route, obj_route

    def test_find_non_existing_route(self):
        routes_map, errback = self.make_map()
        self.assertIsNone(routes_map.find_route_by_view_name("no-such"))
        self.assertFalse(errback.was_called)

    def test_no_slash_at_start_of_url_path(self):
        routes_map, errback = self.make_map()
        self.add_html_route(
            routes_map, "", view_name="home", parent_view_name=None)
        self.add_html_route(
            routes_map, "other/", view_name="other", parent_view_name=None)
        routes_map.check_routes()
        self.assertTrue(errback.was_called)
        self.assertEqual(
            errback.called_with,
            "'home' route does not start with slash!")

    def test_non_existing_parent(self):
        routes_map, errback = self.make_map()
        self.add_html_route(
            routes_map, "/", view_name="home", parent_view_name="some_home")
        self.add_html_route(
            routes_map, "/other/", view_name="other",
            parent_view_name="some_other")
        routes_map.check_routes()
        self.assertTrue(errback.was_called)
        self.assertEqual(
            errback.called_with,
            "'home' route has non-existing parent ('some_home')!")

    def test_untouched_routes(self):
        routes_map, errback = self.make_map()
        self.add_html_route(
            routes_map, "/", view_name="home", parent_view_name=None)
        self.add_html_route(
            routes_map, "/other/", view_name="other", parent_view_name=None)
        routes_map.check_routes()
        self.assertFalse(errback.was_called)
        routes_map.check_for_untouched_routes()
        self.assertTrue(errback.was_called)
        self.assertEqual(
            errback.called_with,
            "'home' route is not touched!")

    def test_lineage_with_parent_none(self):
        routes_map, errback = self.make_map()
        route = self.add_html_route(
            routes_map, "/", view_name="home", parent_view_name=None)
        routes_map.check_routes()
        self.assertFalse(errback.was_called)
        self.assertEqual(tuple(routes_map.get_lineage(route)), (route, ))
        self.assertFalse(errback.was_called)

    def test_lineage_with_parent_none_at_all(self):
        routes_map, errback = self.make_map()
        route = self.add_html_route(
            routes_map, "/", view_name="home",
            parent_view_name=self.routing.NONE_AT_ALL)
        routes_map.check_routes()
        self.assertFalse(errback.was_called)
        self.assertEqual(tuple(routes_map.get_lineage(route)), ())
        self.assertFalse(errback.was_called)

    def test_lineage_with_parents_chain(self):
        routes_map, errback = self.make_map()
        home_route, cat_route, obj_route = self.add_parents_chain(routes_map)
        routes_map.check_routes()
        self.assertFalse(errback.was_called)
        self.assertEqual(
            tuple(routes_map.get_lineage(home_route)),
            (home_route, ))
        self.assertEqual(
            tuple(routes_map.get_lineage(cat_route)),
            (home_route, cat_route))
        self.assertEqual(
            tuple(routes_map.get_lineage(obj_route)),
            (home_route, cat_route, obj_route))
        self.assertFalse(errback.was_called)

    def test_lineage_with_parents_chain_and_find(self):
        routes_map, errback = self.make_map()
        self.add_parents_chain(routes_map)
        routes_map.check_routes()
        self.assertFalse(errback.was_called)
        home_route = routes_map.find_route_by_view_name("home")
        self.assertEqual(
            tuple(routes_map.get_lineage(home_route)),
            (home_route, ))
        obj_route = routes_map.find_route_by_view_name("object")
        cat_route = routes_map.find_route_by_view_name("category")
        self.assertEqual(
            tuple(routes_map.get_lineage(obj_route)),
            (home_route, cat_route, obj_route))
        self.assertEqual(
            tuple(routes_map.get_lineage(cat_route)),
            (home_route, cat_route))
        self.assertFalse(errback.was_called)
