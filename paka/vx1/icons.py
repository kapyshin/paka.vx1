import os
import shutil
import hashlib
import subprocess


def build_icons(specs, error_callback, cache_dir):
    try:
        os.makedirs(cache_dir)
    except OSError:
        pass
    for spec in specs:
        in_path = _get_existing_logo_file_path(
            spec.site, error_callback=error_callback)
        in_path_hash = _hash_file_contents(in_path, algorithm="sha1")
        cached_path = os.path.join(cache_dir, in_path_hash)
        if not os.path.exists(cached_path):
            os.mkdir(cached_path)
            for cmd in _make_cmds(in_path, cached_path):
                _call(cmd, error_callback=error_callback)
        for icon_file_name in os.listdir(cached_path):
            shutil.copy(
                os.path.join(cached_path, icon_file_name),
                spec.pages_build_dir)


def _get_existing_logo_file_path(site, error_callback):
    paths = (site.logo_path, site.network.logo_path)
    for path in paths:
        if os.path.isfile(path):
            return path
    error_callback(
        "logo file does not exist for {!r} site!".format(
            site.slug))


# Copied from storage/storage_library/checksumming.py.
def _iter_file_chunks(file_path, chunk_size=64 * 1024 * 1024):
    with open(file_path, "rb") as file:
        chunk = file.read(chunk_size)
        while chunk:
            yield chunk
            chunk = file.read(chunk_size)


# Copied from storage/storage_library/checksumming.py.
def _hash_file_contents(file_path, algorithm):
    h = hashlib.new(algorithm)
    for chunk in _iter_file_chunks(file_path):
        h.update(chunk)
    return h.hexdigest()


# Adapted from skel/priv/dolib/api.py.
def _call(args, error_callback):
    return_code = subprocess.call(args)
    if return_code:
        error_callback(
            "Subprocess error.\n{}".format(" ".join(args)))


# Adapted from skel/priv/plugins/static-for-web.py.
def _make_cmds(in_image_path, out_dir):
    def cmd(args, out_file_name, command="convert", unsharp=True):
        r = [command, in_image_path, "-layers", "merge"]
        r.extend(args)
        if unsharp:
            r.extend(["-unsharp", "0x1"])
        r.append(os.path.join(out_dir, out_file_name))
        return r
    # As icons are square, store just one side.
    apple_touch_icon_side_sizes = {
        57, 60, 72, 76, 114, 120, 144, 152, 180, 192}
    favicon_side_sizes = {16, 32, 48, 64}
    # 1. Icons for iOS and Android.
    for side_size in sorted(apple_touch_icon_side_sizes):
        s = "{side_size}x{side_size}".format(side_size=side_size)
        for basename_suffix in {"", "-precomposed"}:
            filename = "apple-touch-icon-{}{}.png".format(s, basename_suffix)
            yield cmd(["-resize", s], filename, unsharp=True)
    yield cmd(["-resize", "180x180"], "apple-touch-icon.png", unsharp=True)
    yield cmd(
        ["-resize", "180x180"], "apple-touch-icon-precomposed.png",
        unsharp=True)
    # 2. Favicon.
    size_args = []
    for side_size in sorted(favicon_side_sizes):
        s = "{side_size}x{side_size}".format(side_size=side_size)
        size_args.extend(["(", "-clone", "0", "-resize", s, ")"])
    args = (
        ["-border", "0"] +
        size_args +
        ["-delete", "0", "-alpha", "off", "-colors", "256"])
    yield cmd(args, "favicon.ico", unsharp=True)
