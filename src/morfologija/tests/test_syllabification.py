import unittest

from ..syllabification import syllabificate


class SyllabificationTest(unittest.TestCase):
    def assertSyllabification(self, word):
        expected = word.split('-')
        word = word.replace('-', '')
        self.assertEqual(list(syllabificate(word)), expected)

    def test_(self):
        self.assertSyllabification('me-dus')
        self.assertSyllabification('sie-na')
        self.assertSyllabification('kal-nai')
        self.assertSyllabification('a-kis')
        self.assertSyllabification('skra-ba-las')
        self.assertSyllabification('per-kirs')
        self.assertSyllabification('var-gams')
        self.assertSyllabification('link-sta')
        self.assertSyllabification('gy-vy-bė')
        # All these words bellow requires dictionary with exceptional forms.
        #self.assertSyllabification('ke-tu-rias-de-šimt')
        #self.assertSyllabification('a-bi-tu-ri-en-tas')
        #self.assertSyllabification('in-du-iz-mas')
        #self.assertSyllabification('su-i-ro')
        #self.assertSyllabification('juod-že-mis')
