import os
import shutil
import collections

from paka import breadcrumbs

from . import translations
from . import errorpages
from . import routing
from . import consts
from . import features
from . import utils


REQUIRED_CHUNK_NAMES = [
    "primary_about",
    "footer_copyrights",
]
for code in errorpages.CODES:
    REQUIRED_CHUNK_NAMES.extend(
        [
            "error_page_{}_content".format(code)])


_PageSpec = collections.namedtuple(
    "_PageSpec", ["dest_path", "src_path", "contents"])


def prepare_build_dir(build_dir):
    try:
        shutil.rmtree(build_dir, ignore_errors=False)
    except (OSError, IOError):
        pass
    os.makedirs(build_dir)


def _make_chunks(site, context, required_chunk_names, error_callback):
    def _make_chunk_renderer(chunk_template, context):
        def _render_chunk():
            return site.renderer.render_text(chunk_template, **context)
        return _render_chunk
    chunks_data = dict(site.network.chunks_data, **site.chunks_data)
    chunks = {}
    for chunk_name, chunk_template in chunks_data.items():
        chunks[chunk_name] = _make_chunk_renderer(chunk_template, context)
    for chunk_name in required_chunk_names:
        if chunk_name not in chunks:
            error_callback(
                "{!r} chunk does not exist for {} site!".format(
                    chunk_name, site.slug))
    return chunks



def _sorted_series(tags):
    return sorted(tags, key=lambda tag: tag.attrs["name"])


def _make_breadcrumbs(current_route, context, site):
    routes_map = context["routes_map"]
    lineage = routes_map.get_lineage(current_route)
    if not lineage:
        return
    def _make_crumb(route):
        view_name = route.view_name
        mk_key = lambda suff: "breadcrumbs_{}_{}".format(view_name, suff)
        label = translations.translate(
            mk_key("label"), context=context, site=site)
        try:
            heading = translations.translate(
                mk_key("heading"), context=context, site=site)
        except KeyError:
            heading = None
        return breadcrumbs.Crumb(
            label=label, heading=heading,
            url_path=routes_map.format_url_path(
                route.view_name, context=context),
            extra={"view_name": view_name})
    return breadcrumbs.Bread.from_crumbs(map(_make_crumb, lineage))


def _make_page_spec_factory(
        routes_map, site, pages_build_dir, required_chunk_names,
        extra_template_context, error_callback):
    def _make_fs_path(url_path, fmt):
        segments = [] if url_path == "/" else url_path.lstrip("/").split("/")
        if fmt is not routing.Fmt.direct:
            segments.append("index.{}".format(fmt.value))
        return os.path.join(pages_build_dir, *segments)
    def _make_page_spec(view_name, context, substatic=False):
        route = routes_map.find_route_by_view_name(view_name, touch=True)
        url_path = routes_map.format_url_path(
            route.view_name, context=context)
        if substatic:
            obj = context["substatic_object"]
            suffixes = obj.substatic_suffixes
            src_root = obj.substatic_root
            dest_root = _make_fs_path(url_path, fmt=routing.Fmt.direct)
            return (
                _PageSpec(
                    src_path=os.path.join(src_root, suffix),
                    dest_path=os.path.join(dest_root, suffix),
                    contents=None)
                for suffix in suffixes)
        else:
            # Add always-present (in templates) items.
            context = dict(
                context, view_name=view_name, url_path=url_path, site=site,
                routes_map=routes_map, **extra_template_context)
            # This statement is separate from above, because we want to avoid
            # having chunks and breadcrumbs present in context for them.
            context.update(
                breadcrumbs=_make_breadcrumbs(
                    route, context=context, site=site),
                chunks=_make_chunks(
                    site, context=context,
                    required_chunk_names=required_chunk_names,
                    error_callback=error_callback))
            # Now make page spec.
            contents = site.renderer(route.template_name, **context)
            path = _make_fs_path(url_path, fmt=route.fmt)
            return _PageSpec(dest_path=path, contents=contents, src_path=None)
    return _make_page_spec


def _make_extra_template_context(site):
    recent_notes = utils.sort_notes(site.notes)[:10]
    popular_tags_sorting_key = lambda tag: (
        -len(tag.notes_slugs), utils.tag_sorting_key(tag))
    popular_tags = sorted(
        site.tags.values(), key=popular_tags_sorting_key)[:10]
    return {
        consts.RECENT_NOTES_TEMPLATE_CONTEXT_KEY: recent_notes,
        consts.POPULAR_TAGS_TEMPLATE_CONTEXT_KEY: popular_tags}


def _make_note_pairs_for_feed(notes, routes_map):
    for note in notes:
        note_path = routes_map.format_url_path(
            "one_note", context={"note": note})
        yield (note, note_path)


def _generate_pages_specs(
        site, pages_build_dir, required_chunk_names, feature_checker,
        error_callback):
    routes_map = routing.Map(error_callback=error_callback)
    routing.add_routes(routes_map, feature_checker=feature_checker)
    routes_map.check_routes()
    mk = _make_page_spec_factory(
        routes_map=routes_map, site=site,
        pages_build_dir=pages_build_dir,
        required_chunk_names=required_chunk_names,
        extra_template_context=_make_extra_template_context(site),
        error_callback=error_callback)
    for tag in site.tags.values():
        notes = utils.sort_notes(
            note for note in site.notes if tag.slug in note.tags_slugs)
        yield mk(
            view_name="recent_tag_notes_feed",
            context={
                "tag": tag,
                "is_tag_view": True,
                "notes": _make_note_pairs_for_feed(
                    notes[:10], routes_map=routes_map),
                "link_path": routes_map.format_url_path(
                    "one_tag", context={"tag": tag})})
        yield mk(
            view_name="one_tag",
            context={"tag": tag, "notes": notes})
    yield mk(
        view_name="all_tags",
        context={"tags": utils.sort_tags(site.tags.values())})
    for note in site.notes:
        tags = [site.tags[slug] for slug in note.tags_slugs]
        series = [site.series[slug] for slug in note.series_slugs]
        series_to_notes = {
            s.slug: utils.sort_notes([
                note for note in site.notes if s.slug in note.series_slugs])
            for s in series}
        context = {
            "note": note,
            "tags": utils.sort_tags(tags),
            "series": _sorted_series(series),
            "series_to_notes": series_to_notes}
        view_name = "one_note"
        yield mk(view_name=view_name, context=context)
        for spec in mk(
                view_name=view_name,
                context=dict(context, substatic_object=note),
                substatic=True):
            yield spec
    yield mk(
        view_name="recent_notes_feed",
        context={
            "notes": _make_note_pairs_for_feed(
                utils.sort_notes(site.notes)[:10], routes_map=routes_map),
            "is_tag_view": False,
            "link_path": routes_map.format_url_path("all_notes", context={})})
    yield mk(
        view_name="all_notes",
        context={"notes": utils.sort_notes(site.notes)})
    if feature_checker(features.Feature.about):
        yield mk(view_name="about", context={})
    yield mk(view_name="home", context={})
    yield mk(view_name="robots_txt", context={})
    for code in errorpages.CODES:
        view_name = errorpages.make_view_name(code)
        yield mk(view_name=view_name, context={"code": code})
    routes_map.check_for_untouched_routes()


def build_site_by_spec(site_spec, feature_checker, error_callback):
    for page_spec in _generate_pages_specs(
            site=site_spec.site,
            pages_build_dir=site_spec.pages_build_dir,
            required_chunk_names=REQUIRED_CHUNK_NAMES,
            feature_checker=feature_checker,
            error_callback=error_callback):
        src_path = page_spec.src_path
        dest_path = page_spec.dest_path
        contents = page_spec.contents
        assert contents is not None or src_path
        try:
            os.makedirs(os.path.dirname(dest_path))
        except OSError:
            pass
        if contents is not None:
            utils.write_file(dest_path, contents)
        else:
            shutil.copyfile(src_path, dest_path)
