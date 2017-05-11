Though I recommend you to read [`.tar`](/notes/how-to-create-.tar-reproducibly/)
and [`.gz`](/notes/how-to-create-.gz-reproducibly/) notes, where internals and
features of these file formats and relevant modules from CPython standard library
are discussed, you are free to skip them it you are in rush and need just code,
because here we’ll do just that: code :)

Yes, here we are to make a script (`mktgz.py`) that’ll take paths to files
and dirs and make `.tar.gz`—compressed archive.

```python3
#!/usr/bin/env python3

import os
import gzip
import tarfile
import argparse


def tgz(top_paths, *, mtime, dest, reltop, filename, verbose):
    relpath = lambda p: os.path.relpath(p, start=reltop)
    def _get_to_add():
        for top_path in sorted(top_paths):
            if os.path.isdir(top_path):
                for dirpath, dirnames, filenames in os.walk(
                        top_path, topdown=True):
                    dirnames.sort()
                    yield (dirpath, relpath(dirpath))
                    for filename in sorted(filenames):
                        filepath = os.path.join(dirpath, filename)
                        yield (filepath, relpath(filepath))
            else:
                yield (top_path, relpath(top_path))
    with open(dest, "wb") as _dest_file:
        with gzip.GzipFile(
                fileobj=_dest_file, mode="w",
                filename=filename, mtime=mtime) as dest_file:
            with tarfile.open(fileobj=dest_file, mode="w") as archive:
                for path, arcname in _get_to_add():
                    if verbose:
                        print(path, "->", arcname)
                    tinfo = archive.gettarinfo(path, arcname=arcname)
                    if mtime is not None:
                        tinfo.mtime = mtime
                    if tinfo.isreg():
                        with open(path, "rb") as file:
                            archive.addfile(tinfo, fileobj=file)
                    else:
                        archive.addfile(tinfo)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--reltop", default=os.getcwd())
    parser.add_argument("--mtime", type=float, default=None)
    parser.add_argument("--filename", default=None)
    parser.add_argument("--verbose", action="store_true", default=False)
    parser.add_argument("dest")
    args = parser.parse_args()
    tgz(
        args.paths, mtime=args.mtime, dest=args.dest, reltop=args.reltop,
        filename=args.filename, verbose=args.verbose)
```

Few quick notes about code. First, same `mtime` value is used for both “tar”
and “gzip” parts of code. Second, [`gzip.GzipFile`](https://docs.python.org/3.5/library/gzip.html#gzip.GzipFile)
is used instead of [`gzip.open`](https://docs.python.org/3.5/library/gzip.html#gzip.open)
because the latter does not accept `filename` and `mtime` arguments.
Oh, and if you are puzzled about `reltop`, please read the [note about tar](/notes/how-to-create-.tar-reproducibly/),
`reltop`’s purpose is explained there.


Example usage:

```console
$ ./mktgz.py dir1/ file2 dir2/ file1 out.tar.gz --mtime 0 --filename '' --verbose
dir1/ -> dir1
dir1/1 -> dir1/1
dir1/1/a -> dir1/1/a
dir1/1/b -> dir1/1/b
dir1/1/c -> dir1/1/c
dir1/1/d -> dir1/1/d
dir1/2 -> dir1/2
dir1/2/aa -> dir1/2/aa
dir1/2/bb -> dir1/2/bb
dir1/2/cc -> dir1/2/cc
dir1/2/dd -> dir1/2/dd
dir1/3 -> dir1/3
dir1/3/aaa -> dir1/3/aaa
dir1/3/bbb -> dir1/3/bbb
dir1/3/ccc -> dir1/3/ccc
dir1/3/ddd -> dir1/3/ddd
dir2/ -> dir2
file1 -> file1
file2 -> file2
```

As we expect, `out.tar.gz` is a gzip file:

```console
$ file out.tar.gz
out.tar.gz: gzip compressed data, max compression
```

And `tar` also works with `out.tar.gz` as expected:

```console
$ tar tvf out.tar.gz
drwxrwxr-x u/u             0 1970-01-01 03:00 dir1/
drwxrwxr-x u/u             0 1970-01-01 03:00 dir1/1/
-rw-rw-r-- u/u             5 1970-01-01 03:00 dir1/1/a
-rw-rw-r-- u/u             5 1970-01-01 03:00 dir1/1/b
-rw-rw-r-- u/u             5 1970-01-01 03:00 dir1/1/c
-rw-rw-r-- u/u             5 1970-01-01 03:00 dir1/1/d
drwxrwxr-x u/u             0 1970-01-01 03:00 dir1/2/
-rw-rw-r-- u/u             5 1970-01-01 03:00 dir1/2/aa
-rw-rw-r-- u/u             5 1970-01-01 03:00 dir1/2/bb
-rw-rw-r-- u/u             5 1970-01-01 03:00 dir1/2/cc
-rw-rw-r-- u/u             5 1970-01-01 03:00 dir1/2/dd
drwxrwxr-x u/u             0 1970-01-01 03:00 dir1/3/
-rw-rw-r-- u/u             5 1970-01-01 03:00 dir1/3/aaa
-rw-rw-r-- u/u             5 1970-01-01 03:00 dir1/3/bbb
-rw-rw-r-- u/u             5 1970-01-01 03:00 dir1/3/ccc
-rw-rw-r-- u/u             7 1970-01-01 03:00 dir1/3/ddd
drwxrwxr-x u/u             0 1970-01-01 03:00 dir2/
-rw-rw-r-- u/u            10 1970-01-01 03:00 file1
-rw-rw-r-- u/u            17 1970-01-01 03:00 file2
```
