Given that in [`tarfile`](https://docs.python.org/3.5/library/tarfile.html)
default for `format` argument of `tarfile.TarFile` is [`GNU_FORMAT`](https://hg.python.org/cpython/file/b8233c779ff7/Lib/tarfile.py#l106), I will use GNU `tar`, not [POSIX](http://pubs.opengroup.org/onlinepubs/9699919799/utilities/pax.html),
but in aspects I care about for this note they are very similar.

Tar archive is comprised of sequence of “file entries”. Each entry consists of header (metadata)
and contents (data). Header contains `mtime` field, that represents file modification time
at the time of archivation. In Python’s `tarfile` archive entries are represented by instances
of [`tarfile.TarInfo`](https://hg.python.org/cpython/file/b8233c779ff7/Lib/tarfile.py#l720),
and `mtime` field of file entry header is represented by public field of `tarfile.TarInfo` instance.
This is all specifics you need to know about tar archive format,
but if you want non-simplified description, consult, for example, the [relevant section](https://www.gnu.org/software/tar/manual/html_node/Standard.html) of GNU `tar` manual.

So, when you are making a tar archive, there are 2 ways in which you can influence end result:

 * add files in particular order;
 * set added files’ modification time (`mtime`).

If (for your goals) you consider two identical files with differing `mtime` different, you
don’t have to worry about it (but still you may want to add files in order). Otherwise,
you’ll have to set it to some fixed value to make it irrelevant.

I am talking about realistic scenario, so it should be possible to add not just regular files,
but also directories (recursively). Given that in such case we still care about file order,
I will not use [`TarFile.add`](https://docs.python.org/3.5/library/tarfile.html#tarfile.TarFile.add):
it [uses](https://hg.python.org/cpython/file/b8233c779ff7/Lib/tarfile.py#l1950)
the [`os.listdir`](https://docs.python.org/3.5/library/os.html#os.listdir), that returns a list
of dir entries in arbitrary order—and `TarFile.add` does not sort it nor allow us to do that:

```
for f in os.listdir(name):
    self.add(...)
```

Instead for for recursing into dirs I’ll use [`os.walk`](https://docs.python.org/3.5/library/os.html#os.walk).
Though it uses [`os.scandir`](https://docs.python.org/3.5/library/os.html#os.scandir) internally (`os.listdir`
in CPython < 3.5), which does not guarantee any ordering too, it is [possible](https://docs.python.org/3.5/library/os.html#os.walk)
to affect `walk` so it does its work in particular order:

> When `topdown` is `True`, the caller can modify the `dirnames` list in-place
> (perhaps using `del` or slice assignment), and `walk()` will only recurse into
> the subdirectories whose names remain in `dirnames`; this can be used to prune the search,
> **impose a specific order of visiting**, or even to inform `walk()` about directories the
> caller creates or renames before it resumes `walk()` again.
> Modifying `dirnames` when `topdown` is `False` has no effect on the behavior of the walk,
> because in bottom-up mode the directories in `dirnames` are generated before `dirpath`
> itself is generated.

Thus, code that always traverses all dirs and files in `top_dir` is same order
will look like this:

```
for dirpath, dirnames, filenames in os.walk(top_dir, topdown=True):
    dirnames.sort()
    # ...
    for filename in sorted(filenames):
        # ...
```

To add file entries (that is, regular files, dirs, etc.) into archive I’ll use
[`TarFile.addfile`](https://docs.python.org/3.5/library/tarfile.html#tarfile.TarFile.addfile) instead of
`TarFile.add`. Therefore, in general, `tarfile`-related code will look like this:

```
with tarfile.open(name="out.tar", mode="w") as archive:
    for path, arcname in ...:
        tinfo = archive.gettarinfo(path, arcname=arcname)
        tinfo.mtime = 123123.1
        if tinfo.isreg():
            with open(path, "rb") as file:
                archive.addfile(tinfo, fileobj=file)
        else:
            archive.addfile(tinfo)
```

Before getting to actual implementation, let’s discuss one more concept: arcnames.
Arcname is name of file in archive, and it can, actually, be path: that is, it can
be `control.txt` as well as `somedir/1.txt` or `/home/user/some/file`. For our purposes,
having absolute file paths in archive is undesirable, so we have to “modify” them in a
way that ensures arcnames do not include parents of “top dirs” we intend to add into
archive.


Implementation
--------------

The goal is to build a script (`mktar.py`) that creates tar archive containing files
and directories: paths are passed as command-line arguments.

```
#!/usr/bin/env python3

import os
import tarfile
import argparse


def tar(top_paths, *, mtime, dest, reltop, verbose):
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
    with tarfile.open(name=dest, mode="w") as archive:
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
    parser.add_argument("--verbose", action="store_true", default=False)
    parser.add_argument("dest")
    args = parser.parse_args()
    tar(
        args.paths, mtime=args.mtime, dest=args.dest, reltop=args.reltop,
        verbose=args.verbose)
```

So, for example, to create archive `out.tar` with `mtime` pre-set to `123`,
you’d use `./mktar.py dir1/ file1 dir2/ file2 out.tar --mtime 123`. If, say,
`dir{1,2}` and `file{1,2}` are in `reproducible_tar/`, and you want it to
be “root” inside an archive, you could use `--reltop ../` to modify “relative
top dir” (`reltop`), so arcnames will be built like this
(command is `./mktar.py dir1/ file1 dir2/ file2 out.tar --mtime 123 --reltop ../ --verbose`
and is run from inside `reproducible_tar/`):

```
dir1/ -> reproducible_tar/dir1
dir1/1 -> reproducible_tar/dir1/1
dir1/1/a -> reproducible_tar/dir1/1/a
dir1/1/b -> reproducible_tar/dir1/1/b
dir1/1/c -> reproducible_tar/dir1/1/c
dir1/1/d -> reproducible_tar/dir1/1/d
dir1/2 -> reproducible_tar/dir1/2
dir1/2/aa -> reproducible_tar/dir1/2/aa
dir1/2/bb -> reproducible_tar/dir1/2/bb
dir1/2/cc -> reproducible_tar/dir1/2/cc
dir1/2/dd -> reproducible_tar/dir1/2/dd
dir1/3 -> reproducible_tar/dir1/3
dir1/3/aaa -> reproducible_tar/dir1/3/aaa
dir1/3/bbb -> reproducible_tar/dir1/3/bbb
dir1/3/ccc -> reproducible_tar/dir1/3/ccc
dir1/3/ddd -> reproducible_tar/dir1/3/ddd
dir2/ -> reproducible_tar/dir2
file1 -> reproducible_tar/file1
file2 -> reproducible_tar/file2
```

Now we have working implementation of reproducible tar building, and we can
[look at gzip](/notes/how-to-create-.gz-reproducibly/).
