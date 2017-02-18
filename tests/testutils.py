import os
import re
import shutil
import fnmatch
import tempfile
import unittest
import itertools
try:
    from functools import lru_cache
except ImportError:
    from repoze.lru import lru_cache


TEST_FILES_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "files")


class TestCase(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.temp_dirs = []

    def tearDown(self):
        self.cleanup_temp_dirs()

    def cleanup_temp_dirs(self):
        for temp_dir in self.temp_dirs:
            shutil.rmtree(temp_dir)
        self.temp_dirs = []

    def make_temp_dir(self):
        temp_dir = tempfile.mkdtemp()
        self.temp_dirs.append(temp_dir)
        return temp_dir

    # Directory & file comparison.
    @lru_cache(maxsize=128)
    def compile_ignores(self, ignores):
        if not ignores:
            return lambda s: False
        parts = map(fnmatch.translate, ignores)
        return re.compile("|".join(parts)).match

    def assert_text_files_equal(self, left, right):
        def read(path):
            with open(path, "rb") as file:
                return file.read().decode("utf-8")
        self.assertEqual(
            read(left), read(right),
            msg="{} != {}".format(left, right))

    def assert_dirs_equal(self, left, right, ignore_contents=None):
        left_members = tuple(sorted(os.listdir(left)))
        right_members = tuple(sorted(os.listdir(right)))
        self.assertEqual(left_members, right_members)

        for member in left_members:
            left_path = os.path.join(left, member)
            right_path = os.path.join(right, member)
            if os.path.isdir(left_path):
                self.assert_dirs_equal(
                    left_path, right_path, ignore_contents=ignore_contents)
            else:
                matcher = self.compile_ignores(tuple(ignore_contents or ()))
                if not matcher(member):
                    self.assert_text_files_equal(left_path, right_path)

    # Generator-specific.
    def generate(self, src, dest):
        from paka.vx1.generator import main

        nets_dir = os.path.join(src, "nets")
        common_dir = os.path.join(src, "common")

        build_dir = os.path.join(dest, "build")
        cache_dir = os.path.join(dest, "cache")

        overrides_argv = [
            "--site-attr-overrides",
            "93z_py={}".format(os.path.join(src, "93z_py_attr_overrides")),
            "--site-attr-overrides",
            "93z_dev={}".format(os.path.join(src, "93z_dev_attr_overrides"))]

        main(argv=[
            "--blognets-dir", nets_dir,
            "--slug-pattern", "*",
            "--template-dirs-prepend", common_dir,
            "--build-dir", build_dir,
            "--cache-dir", cache_dir,
            "--current-date", "2017-01-17"] + overrides_argv)
