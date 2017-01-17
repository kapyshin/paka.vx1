import os
import re
import datetime
import collections

from . import templates
from . import consts
from . import utils


DATESLUG_RE = re.compile(
    r"^(?P<date_string>\d\d\d\d-\d\d-\d\d)-(?P<slug>.+)$")


Network = collections.namedtuple(
    "Network",
    [
        "slug", "sites_slugs", "sites", "network_dir", "chunks_data",
        "translations_data", "logo_path"])
Site = collections.namedtuple(
    "Site",
    [
        "attrs", "slug", "notes", "series", "renderer",
        "network", "site_dir", "chunks_data", "tags", "logo_path",
        "earliest_year", "current_year", "translations_data"])
Note = collections.namedtuple(
    "Note",
    [
        "attrs", "body", "slug", "date", "tags_slugs", "series_slugs",
        "substatic_root", "substatic_suffixes"])
Tag = collections.namedtuple(
    "Tag", ["attrs", "description", "slug", "notes_slugs"])
Series = collections.namedtuple(
    "Series", ["attrs", "description", "slug", "notes_slugs"])


def prepare_sites(
        sites_dirs, networks_dir, internal_templates_dir,
        prepended_templates_dirs, appended_templates_dirs,
        current_date, error_callback):
    networks = _get_networks(networks_dir, error_callback=error_callback)
    # Make {site_slug: network.network_dir} mapping to make template
    # search path (to make renderer).
    _site_slug_to_network_dir = {
        site_slug: network.network_dir
        for network in networks
        for site_slug in network.sites_slugs}
    sites = []
    for site_dir in sites_dirs:
        site = _make_site(site_dir)
        internal_templates_dirs = [
            os.path.join(_site_slug_to_network_dir[site.slug], "templates"),
            os.path.join(site.site_dir, "templates"),
            internal_templates_dir]
        templatepath = templates.make_templatepath(
            prepended=prepended_templates_dirs,
            internal=internal_templates_dirs,
            appended=appended_templates_dirs)
        renderer = templates.make_renderer(
            templatepath, charset=consts.CHARSET)
        # This needs explanation. We did _make_site(site_dir) to create object
        # with slug and site_dir fields, which we used to make template search
        # path. Now all other fields need to be filled (notes, tags, etc.)
        sites.append(
                _get_site(
                    site, current_date=current_date, renderer=renderer,
                    error_callback=error_callback))
    return _set_up_networks(networks=networks, sites=sites)


def _get_networks(networks_dir, error_callback):
    def _get_network(network_dir, error_callback):
        network = Network(
            slug=os.path.basename(network_dir),
            sites_slugs=[], sites=[],
            network_dir=network_dir, chunks_data={}, translations_data={},
            logo_path=_make_logo_path(network_dir))
        network.sites_slugs.extend(
            utils.read_slugs(network_dir, "sites-slugs"))
        if len(network.sites_slugs) < 2:
            error_callback(
                "{!r} network has less than two sites!".format(network.slug))
        network.chunks_data.update(utils.read_chunks(network_dir))
        network.translations_data.update(utils.read_translations(network_dir))
        return network
    networks = []
    for network_dir in utils.subpaths(networks_dir):
        networks.append(
            _get_network(network_dir, error_callback=error_callback))
    return networks


def _make_site(site_dir):
    return Site(
        attrs={}, slug=os.path.basename(site_dir), notes=[], series={},
        renderer=None, network=None, site_dir=site_dir, chunks_data={},
        tags={}, logo_path=None, earliest_year=None, current_year=None,
        translations_data={})


def _get_site(site, current_date, renderer, error_callback):
    site = site._replace(renderer=renderer)
    # Read translations.
    site.translations_data.update(
        utils.read_translations(site.site_dir))
    # Read attrs.
    site = site._replace(attrs=utils.read_attrs(site.site_dir))
    utils.check_required_attrs(
        site.attrs, ("domain", "name", "date_format", "language"),
        entity_slug=site.slug,
        error_callback=error_callback)
    # Read tags.
    tags_dir = os.path.join(site.site_dir, "tags")
    for tag_dir in utils.subpaths(tags_dir):
        tag = _get_tag(
            tag_dir, renderer=renderer, error_callback=error_callback)
        site.tags[tag.slug] = tag
    # Read notes' series.
    all_series_dir = os.path.join(site.site_dir, "series")
    for series_dir in utils.subpaths(all_series_dir, ignore_not_exists=True):
        series = _get_series(
            series_dir, renderer=renderer, error_callback=error_callback)
        site.series[series.slug] = series
    # Read notes & populate site's notes list.
    notes_dir = os.path.join(site.site_dir, "notes")
    for note_dir in utils.subpaths(notes_dir):
        site.notes.append(
            _get_note(
                note_dir, tags=site.tags.values(),
                series=site.series.values(), renderer=renderer,
                error_callback=error_callback))
    # Set earliest year (based on publication dates of notes)
    # and current year (value passed).
    site = site._replace(
        earliest_year=min(note.date for note in site.notes).year,
        current_year=current_date.year)
    # Read chunks & populate site's chunks mapping.
    site.chunks_data.update(utils.read_chunks(site.site_dir))
    # Set logo path.
    site = site._replace(logo_path=_make_logo_path(site.site_dir))
    # Check for note slug duplication.
    dupes_counter = collections.Counter(note.slug for note in site.notes)
    for slug, count in dupes_counter.items():
        if count > 1:
            error_callback(
                "{!r} slug is used {} times in {!r} site!".format(
                    slug, count, site.slug))
    # Check notes do not reference non-existing tags.
    for note in site.notes:
        if not note.tags_slugs:
            error_callback(
                "{!r} note of {!r} site does not have tags!".format(
                    note.slug, site.slug))
        else:
            for slug in note.tags_slugs:
                if slug not in site.tags:
                    error_callback(
                        (
                            "{!r} tag is undefined but is used "
                            "by {!r} note of {!r} site!").format(
                                slug, note.slug, site.slug))
    # Check tags have at least one associated note.
    for slug, tag in site.tags.items():
        if not tag.notes_slugs:
            error_callback(
                (
                    "{!r} tag of {!r} site does not have "
                    "any notes associated!").format(
                        slug, site.slug))
    # Check series have at least one associated note.
    for slug, series in site.series.items():
        if not series.notes_slugs:
            error_callback(
                (
                    "{!r} series of {!r} site does not have "
                    "any notes associated!").format(
                        slug, site.slug))
    return site


def _get_note(note_dir, tags, series, renderer, error_callback):
    def _get_date_and_slug(note_dir):
        # '.../2015-08-08-some-slug' -> (date(), 'some-slug')
        dateslug = os.path.basename(note_dir)
        matchobj = DATESLUG_RE.match(dateslug)
        date_string = matchobj.group("date_string")
        date = datetime.datetime.strptime(date_string, "%Y-%m-%d").date()
        return date, matchobj.group("slug")
    date, slug = _get_date_and_slug(note_dir)
    attrs = utils.read_attrs(note_dir)
    utils.check_required_attrs(
        attrs, ("title", ),
        entity_slug=slug,
        error_callback=error_callback)
    try:
        body = renderer.render_text(utils.read_subfile(note_dir, "body"))
    except IOError:
        body = renderer.render_markdown(
            utils.read_subfile(note_dir, "body.md"))
    tags_slugs = {tag.slug for tag in tags if slug in tag.notes_slugs}
    series_slugs = {s.slug for s in series if slug in s.notes_slugs}
    substatic_root, substatic_suffixes = utils.get_substatic_data(note_dir)
    return Note(
        slug=slug, date=date, body=body, attrs=attrs, tags_slugs=tags_slugs,
        series_slugs=series_slugs, substatic_root=substatic_root,
        substatic_suffixes=substatic_suffixes)


def _get_tag(tag_dir, renderer, error_callback):
    slug = os.path.basename(tag_dir)
    attrs = utils.read_attrs(tag_dir)
    utils.check_required_attrs(
        attrs, ("name", ),
        entity_slug=slug,
        error_callback=error_callback)
    try:
        description = renderer.render_text(
            utils.read_subfile(tag_dir, "description"))
    except IOError:
        description = None
    notes_slugs = set(utils.read_slugs(tag_dir, "notes-slugs"))
    return Tag(
        attrs=attrs, description=description, slug=slug,
        notes_slugs=notes_slugs)


def _get_series(series_dir, renderer, error_callback):
    slug = os.path.basename(series_dir)
    attrs = utils.read_attrs(series_dir)
    utils.check_required_attrs(
        attrs, ("name", ),
        entity_slug=slug,
        error_callback=error_callback)
    try:
        description = renderer.render_text(
            utils.read_subfile(series_dir, "description"))
    except IOError:
        description = None
    notes_slugs = set(utils.read_slugs(series_dir, "notes-slugs"))
    return Series(
        attrs=attrs, description=description, slug=slug,
        notes_slugs=notes_slugs)


def _set_up_networks(networks, sites):
    slug_to_site = {site.slug: site for site in sites}
    site_slug_to_network = {}
    for unfilled_network in networks:
        slugs = unfilled_network.sites_slugs
        network = unfilled_network._replace(
            sites=[slug_to_site[slug] for slug in slugs])
        for slug in slugs:
            site_slug_to_network[slug] = network
    return list(
        site._replace(network=site_slug_to_network[site.slug])
        for site in sites)


def _make_logo_path(base_dir):
    return os.path.join(base_dir, "logo.xcf")
