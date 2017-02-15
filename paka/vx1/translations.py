import six
import markupsafe


_DATA_CACHE = {}


def translate(key, context, site, escape=True):
    cache_key = "_".join((site.network.slug, site.slug))
    data = _DATA_CACHE.get(cache_key)
    if data is None:
        _DATA_CACHE[cache_key] = data = dict(
            site.network.translations_data, **site.translations_data)
    value = data[key].format(**context).strip()
    if escape:
        value = markupsafe.escape(value)
    return six.text_type(value)
