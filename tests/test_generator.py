import os

import testutils


class GeneratorTest(testutils.TestCase):

    def test_build(self):
        test_files_dir = os.path.join(testutils.TEST_FILES_DIR, "generator1")
        temp_dir = self.make_temp_dir()
        self.generate(
            src=os.path.join(test_files_dir, "source"), dest=temp_dir)
        self.assert_dirs_equal(
            os.path.join(temp_dir, "build"),
            os.path.join(test_files_dir, "build"),
            ignore_contents=["*.png", "*.ico", "*.atom", "nginx.conf"])
