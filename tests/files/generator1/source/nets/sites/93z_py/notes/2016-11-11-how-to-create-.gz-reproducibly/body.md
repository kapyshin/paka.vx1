Essentially, gzip file consists of “members”, each represented by following
diagram:

```
+---+---+--+---+---+---+---+---+---+--+     +=========================================+
|___|___|__|FLG|     MTIME     |___|OS| ... |...original file name, zero-terminated...|
+---+---+--+---+---+---+---+---+---+--+     +=========================================+
```

Member parts not relevant to our discussion are not named, shown or described, but,
if you want specifics, you can look at [GZIP file format specification version 4.3 (RFC 1952)](https://tools.ietf.org/html/rfc1952) and [`gzip` module implementation](https://hg.python.org/cpython/file/b8233c779ff7/Lib/gzip.py).

`FLG` is a flag byte that may indicate presence of original file name; as done in
Python’s [`gzip` module](https://docs.python.org/3.5/library/gzip.html) (more precisely,
in [`GzipFile._write_gzip_header`](https://hg.python.org/cpython/file/b8233c779ff7/Lib/gzip.py#l235)):

```
if fname:
    flags = FNAME
# ...
if fname:
    self.fileobj.write(fname + b'\000')
```

`MTIME` is “the most recent modification time of the original file being compressed”
and “if the compressed data did not come from a file, `MTIME` is set to the time at which
compression started”. In Python
optional `mtime` argument (POSIX timestamp) is taken and [set to `self._write_mtime`](https://hg.python.org/cpython/file/b8233c779ff7/Lib/gzip.py#l187)
in [constructor of `GzipFile`](https://hg.python.org/cpython/file/b8233c779ff7/Lib/gzip.py#l123).
Then `self._write_mtime` is [used in `_write_gzip_header`](https://hg.python.org/cpython/file/b8233c779ff7/Lib/gzip.py#l238) method:

```
mtime = self._write_mtime
if mtime is None:
    mtime = time.time()
```

Finally, `OS` indicates the type of file system, and in Python’s `gzip`
it is [set to 255](https://hg.python.org/cpython/file/b8233c779ff7/Lib/gzip.py#l243)—“Unknown”:

```
self.fileobj.write(b'\377')
```

If you are not sure why 255, `b'\377'` is `0xff`, which is indeed 255:

```
>>> b'\377'
b'\xff'
>>> 0xff
255
```

I guess “Unknown” value for `OS` is hardcoded in `gzip` library to ensure portability.

So, when you are making a gzip file, there are two result-influencing factors: original
`filename`s and `timestamp`s that are kept in members of file (type of filesystem—`OS`—is
set by Python’s `gzip` library, so no need to worry about it).


Implementation
--------------

Our goal is to build a script (`mkgz.py`) that creates gzip file containing file
pointed to by path passed as a command-line argument.

```
#!/usr/bin/env python3

import gzip
import shutil
import argparse


def gz(path, *, mtime, filename, dest):
    with open(path, "rb") as src_file, open(dest, "wb") as _dest_file:
        with gzip.GzipFile(
                fileobj=_dest_file, mode="w",
                filename=filename, mtime=mtime) as dest_file:
            shutil.copyfileobj(src_file, dest_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("--mtime", type=float, default=None)
    parser.add_argument("--filename", default=None)
    parser.add_argument("dest")
    args = parser.parse_args()
    gz(args.path, mtime=args.mtime, filename=args.filename, dest=args.dest)
```

So, having tar archive `out1.tar`, we could use `./mkgz.py out1.tar out1.tar.gz`
command to create gzip file `out1.tar.gz`, but it would contain timestamp and
filename (command to get such output is `file out1.tar.gz`):

```
out1.tar.gz: gzip compressed data, was "out1.tar", last modified: Fri Nov 11 00:00:07 2016, max compression
```

As you may have noticed, `mkgz.py` can accept `--mtime` and `--filename` command-line arguments:
they are passed to [`gzip.GzipFile`](https://docs.python.org/3.5/library/gzip.html#gzip.GzipFile)
constructor. Let’s use these arguments:

```
$ ./mkgz.py out2.tar out2.tar.gz --mtime 1.23 --filename ''
$ file out2.tar.gz
out2.tar.gz: gzip compressed data, last modified: Thu Jan  1 00:00:01 1970, max compression
```

As we can see above, timestamp (“last modified”) is set to one we passed as `--mtime 1.23`.
`filename` is set to empty string.

Let’s make two more gzip files where only filename will vary:

```
$ ./mkgz.py out3.tar out3.tar.gz --mtime 1.23
$ ./mkgz.py out3.tar out4.tar.gz --mtime 1.23 --filename ''
```

If you’ll compare outputs of `hd out3.tar.gz | sed 2q` and `hd out4.tar.gz | sed 2q`,
you’d see that `out3.tar.gz` indeed contains filename of `out3.tar` (while `out4.tar.gz`
does not):

```
00000000  1f 8b 08 08 01 00 00 00  02 ff 6f 75 74 33 2e 74  |..........out3.t|
00000010  61 72 00 ed 9b 41 6e c2  30 10 45 bd f6 29 72 83  |ar...An.0.E..)r.|
```

```
00000000  1f 8b 08 00 01 00 00 00  02 ff ed 9b 41 6e c2 30  |............An.0|
00000010  10 45 bd f6 29 72 83 7a  6c 8f 7d 9e 24 a6 2a 52  |.E..)r.zl.}.$.*R|
```

Now that we looked at [tar](/notes/how-to-create-.tar-reproducibly/) and gzip separately,
we can proceed and [combine them](/notes/how-to-create-.tar.gz-reproducibly/).
