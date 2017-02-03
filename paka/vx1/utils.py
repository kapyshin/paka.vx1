import os

import markupsafe


CHARSET = "utf-8"


def write_file(path, contents):
    with open(path, "wb") as file:
        file.write(contents.encode(CHARSET))


def read_file(path):
    """Read file and return its contents as str."""
    with open(path, "rb") as file:
        binary_contents = file.read()
    return binary_contents.decode(CHARSET)


def read_subfile(base_dir, subfile_name):
    """Read file located in dir and return its contents as str."""
    return read_file(os.path.join(base_dir, subfile_name))


def subpaths(base_dir, ignore_not_exists=False):
    """Generate paths for all things in dir. Like os.path.join + listdir."""
    try:
        names = os.listdir(base_dir)
    except (IOError, OSError) as e:
        if ignore_not_exists:
            return
        raise e
    for name in names:
        yield os.path.join(base_dir, name)


def subpaths_rec(base_dir):
    for dirpath, dirnames, filenames in os.walk(base_dir, followlinks=False):
        for filename in filenames:
            yield os.path.join(dirpath, filename)


def read_kv(path):
    sep = " " * 2
    def _parse_pair(line):
        key_spec, value = line.split(sep, 1)
        key_bits = key_spec.split(":", 1)
        if len(key_bits) == 1:
            return (key_spec, value)
        key, type_ = key_bits
        assert type_ == "html"  # for now, only HTML for explicit type
        return (key, markupsafe.Markup(value))
    def _read(path):
        lines = read_file(path).strip().splitlines()
        for line in lines:
            line = line.strip()
            if line:
                yield _parse_pair(line)
    return dict(_read(path))


def read_attrs(base_dir):
    return read_kv(os.path.join(base_dir, "attrs"))


def read_translations(base_dir):
    try:
        return read_kv(os.path.join(base_dir, "translations"))
    except IOError:
        return {}


def read_kv_dir(base_dir):
    """Construct mapping {file name: file contents} from dir with files."""
    data = {}
    for file_name in os.listdir(base_dir):
        data[file_name] = read_subfile(base_dir, file_name)
    return data


def read_chunks(base_dir):
    chunks_data = {}
    # Read long chunks.
    long_chunks_dir = os.path.join(base_dir, "long_chunks")
    chunks_data.update(read_kv_dir(long_chunks_dir))
    # Read short chunks.
    short_chunks_file = os.path.join(base_dir, "short_chunks")
    chunks_data.update(read_kv(short_chunks_file))
    return chunks_data


def read_slugs(base_dir, subfile_name):
    def _read(base_dir, subfile_name):
        lines = read_subfile(base_dir, subfile_name).strip().splitlines()
        for line in lines:
            line = line.strip()
            if line:
                yield line
    return list(_read(base_dir, subfile_name))


def check_required_attrs(attrs, attr_names, entity_slug, error_callback):
    for name in attr_names:
        if name not in attrs:
            error_callback(
                "{!r} attr is not present for {!r}".format(
                    name, entity_slug))


def get_tags(note, site):
    for tag_slug, tag in site.tags.items():
        if tag_slug in note.tags_slugs:
            yield tag


tag_sorting_key = lambda tag: casefold(tag.attrs["name"])


def sort_tags(tags):
    return sorted(tags, key=tag_sorting_key)


def sort_notes(notes):
    return sorted(notes, key=lambda note: note.date, reverse=True)


def get_substatic_data(obj_dir):
    root = os.path.join(obj_dir, "substatic")
    if os.path.isdir(root):
        suffixes = [
            os.path.relpath(subpath, start=root)
            for subpath in subpaths_rec(root)]
        return root, suffixes
    return None, []


def casefold(s):
    if hasattr(s, "casefold"):
        return s.casefold()
    return s.lower()  # pragma: no cover
