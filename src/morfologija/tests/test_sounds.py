import unittest

from ..sounds import split_sounds


class SplitSoundsTests(unittest.TestCase):
    def assertSplitSounds(self, sounds):
        word = ''.join(sounds)
        self.assertEqual(list(split_sounds(word)), sounds)

    def test_split_sounds(self):
        self.assertSplitSounds(['dž', 'i', 'n', 'a', 's'])
        self.assertSplitSounds(['j', 'u', 'o', 'dž', 'e', 'm', 'i', 's'])
