import datetime

import pytz
from six.moves.urllib.parse import urljoin
from paka.feedgenerator import Atom1Feed

from . import translations
from . import utils


_DEFAULT_TIME = datetime.time(
    hour=0, minute=0, second=0, microsecond=0, tzinfo=pytz.utc)


def make_notes_feed(template_context):
    site = template_context["site"]
    translations_prefix = template_context["view_name"]
    default_context = {"site": site}
    if template_context["is_tag_view"]:
        default_context["tag"] = template_context["tag"]
    base_url = "http://{site.attrs[domain]}".format(site=site)
    def _mkurl(path):
        return urljoin(base_url, path)
    def _mktr(suffix, **extra_context):
        return translations.translate(
            "_".join((translations_prefix, suffix)),
            context=dict(default_context, **extra_context),
            site=site)
    try:
        subtitle = _mktr("subtitle")
    except KeyError:
        subtitle = None
    feed = Atom1Feed(
        title=_mktr("title"),
        subtitle=subtitle,
        link=_mkurl(template_context["link_path"]),
        language=site.attrs["language"],
        author_name=_mktr("author_name"),
        description=None,
        feed_url=_mkurl(template_context["url_path"]))
    for note, note_path in template_context["notes"]:
        note_url = _mkurl(note_path)
        # Notes have only date, so add time with UTC timezone.
        updateddate = datetime.datetime.combine(note.date, _DEFAULT_TIME)
        # We use slugs, as they are more stable than tag names.
        categories = [
            tag.slug
            for tag in utils.sort_tags(utils.get_tags(note, site=site))]
        feed.add_item(
            title=_mktr("item_title", note=note),
            link=note_url,
            description=note.body,
            unique_id=note_url,
            unique_id_is_permalink=True,
            updateddate=updateddate,
            categories=categories)
    return feed.writeString("utf-8")
