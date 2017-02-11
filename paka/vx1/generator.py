from __future__ import print_function

import os
import sys
import locale
import fnmatch
import datetime
import argparse
import collections

from paka.vx1.preparation import prepare_sites
from paka.vx1.building import prepare_build_dir, build_site_by_spec
from paka.vx1.static import build_static
from paka.vx1.icons import build_icons
from paka.vx1.nginx import build_nginx_config
from paka.vx1.features import make_feature_checker
from paka.vx1.utils import subpaths


INTERNAL_TEMPLATES_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "templates"))


SiteBuildSpec = collections.namedtuple(
    "SiteBuildSpec",
    ["site", "site_build_dir", "pages_build_dir", "static_build_dir"])


def _set_build_dir(spec, build_dir):
    site_build_dir = os.path.join(build_dir, "sites", spec.site.slug)
    return spec._replace(
        site_build_dir=site_build_dir,
        pages_build_dir=os.path.join(site_build_dir, "pages"),
        static_build_dir=os.path.join(site_build_dir, "s"))


def set_build_dir(specs, build_dir):
    return list(_set_build_dir(spec, build_dir=build_dir) for spec in specs)


def make_sites_specs(sites, build_dir):
    def mk(site):
        return SiteBuildSpec(
            site=site, site_build_dir=None, pages_build_dir=None,
            static_build_dir=None)
    return set_build_dir((mk(site) for site in sites), build_dir=build_dir)


def error_callback(text):
    print("[ERROR] {}".format(text), file=sys.stderr)
    sys.exit(1)


def main(argv=sys.argv[1:]):
    locale.setlocale(locale.LC_ALL, "C")
    parser = argparse.ArgumentParser(prog="paka.vx1")
    parser.add_argument(
        "--blognets-dir", help="dir containing input data (sites and networks)",
        required=True)
    parser.add_argument(
        "--build-dir", help="dir that will contain output data",
        required=True)
    parser.add_argument(
        "--build-dir-future-path",
        help=(
            "path at which build dir will be on prod "
            "(to generate correct config for nginx)"))
    parser.add_argument(
        "--template-dirs-prepend", nargs="*",
        help=(
            "paths to dirs with templates to prepend to template search path"))
    parser.add_argument(
        "--template-dirs-append", nargs="*",
        help=(
            "paths to dirs with templates to append to template search path"))
    parser.add_argument(
        "--slug-pattern", required=True, default="*",
        help="Unix shell-style pattern for slugs of sites to build")
    parser.add_argument("--cache-dir", required=True, help="dir for cache")
    parser.add_argument(
        "--current-date", help="date (in %%Y-%%m-%%d format) to use as current")
    parser.add_argument(
        "--features", nargs="*", default=[],
        help="names of build features to turn on")
    parser.add_argument(
        "--site-attr-overrides", nargs="*",
        help="site_slug=path_to_attrs_file_with_pairs_to_update")
    args = parser.parse_args(argv)

    if args.current_date:
        current_date = datetime.datetime.strptime(
            args.current_date, "%Y-%m-%d").date()
    else:
        current_date = datetime.date.today()

    blognets_dir = os.path.abspath(args.blognets_dir)
    networks_dir = os.path.join(blognets_dir, "networks")
    sites_dir = os.path.join(blognets_dir, "sites")

    template_dirs_prepended = [
        os.path.abspath(path)
        for path in (args.template_dirs_prepend or ())]
    template_dirs_appended = [
        os.path.abspath(path)
        for path in (args.template_dirs_append or ())]

    build_dir = os.path.abspath(args.build_dir)
    build_dir_future_path = os.path.abspath(
        args.build_dir_future_path or build_dir)
    cache_dir = os.path.abspath(args.cache_dir)

    feature_checker = make_feature_checker(
        args.features, error_callback=error_callback)

    sites = prepare_sites(
        sites_dirs=subpaths(sites_dir),
        networks_dir=networks_dir,
        internal_templates_dir=INTERNAL_TEMPLATES_DIR,
        prepended_templates_dirs=template_dirs_prepended,
        appended_templates_dirs=template_dirs_appended,
        current_date=current_date, error_callback=error_callback,
        attr_overrides=args.site_attr_overrides or ())
    # Determine which sites to build.
    slug_to_site = {site.slug: site for site in sites}
    sites = [
        slug_to_site[slug]
        for slug in fnmatch.filter(slug_to_site, args.slug_pattern)]
    # Build sites.
    prepare_build_dir(build_dir)
    specs = make_sites_specs(sites, build_dir=build_dir)
    for spec in specs:
        build_site_by_spec(
            spec, feature_checker=feature_checker,
            error_callback=error_callback)
    # Build static (CSS, JS).
    build_static(specs)
    # Build favicon, etc.
    build_icons(
        specs, error_callback=error_callback,
        cache_dir=os.path.join(cache_dir, "icons"))
    # Build nginx config.
    specs = set_build_dir(specs, build_dir=build_dir_future_path)
    build_nginx_config(specs, build_dir=build_dir)
