import unittest

from ..utils import assign
from ..utils import UnknownField


class TestClass(object): pass


class AssignTests(unittest.TestCase):
    def test_correct(self):
        obj = TestClass()
        data = dict(a=3, b=2, c=1)
        fields = (
            ('a', 1),
            ('b', None),
            ('x', 'z'),
        )
        assign(obj, data, fields, ignore=('c',))
        self.assertEqual(obj.a, 3)
        self.assertEqual(obj.b, 2)
        self.assertFalse(hasattr(obj, 'c'))
        self.assertEqual(obj.x, 'z')

    def test_exception(self):
        obj = TestClass()
        data = dict(a=3, b=2, c=1)
        fields = (
            ('a', 1),
            ('b', None),
        )
        self.assertRaises(UnknownField, assign, obj, data, fields)
