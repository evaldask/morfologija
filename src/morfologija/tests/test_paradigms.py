import yaml
import unittest

from ..paradigms import Paradigm
from ..paradigms import ParadigmCollection

RES = dict(
    paradigms = """\
- type: symbols
  key: case
  label: Linksniai
  symbols:
  - nom
  - gen
  - dat
  - acc
  - ins
  - loc
  - voc

- type: suffixes
  key: vyr/as
  symbols:
   gender: m
   number: sg
  define:
    suffixes:
      case:
      - as
      - o
      - ui
      - ą
      - u
      - e
      - e

- type: suffixes
  key: Jon/as
  extends:
  - keys: vyr/as
    replace:
      suffixes:
        case:
          voc: ai

- key: brol/is
  symbols:
    gender: m
    number: sg
  define:
    suffixes:
      case:
      - is
      - io
      - iui
      - į
      - iu
      - yje
      - i

- key: brol/el/is
  extends:
  - keys:
    - brol/is
    prefix:
      suffixes: el

- key: vėj/as
  symbols:
    gender: m
    number: sg
  define:
    suffixes:
      case:
      - as
      - o
      - ui
      - ą
      - u
      - [uje, yje]
      - i

- key: jūr/a
  symbols:
    gender: f
    number: sg
  define:
    suffixes:
      case:
      - a
      - os
      - ai
      - ą
      - a
      - oje
      - a
    optional-prefixes:
      suffixes: i



- key: vyr/ai
  symbols:
    gender: m
    number: pl
  define:
    suffixes:
      case:
      - ai
      - ų
      - ams
      - us
      - ais
      - uose

- key: eln/i/ai
  extends:
  - keys: vyr/ai
    prefix:
      suffixes: i

- key: vežim/aičiai
  override-symbols: false
  extends:
  - keys: eln/i/ai
    prefix:
      suffixes: ait


""",
)


class NodeTests(unittest.TestCase):
    def setUp(self):
        paradigms = yaml.load(RES['paradigms'])
        self.paradigms = ParadigmCollection(paradigms)

    def test_define(self):
        paradigm = self.paradigms.get('vyr/as')
        suffixes = list(paradigm.affixes('suffixes'))
        self.assertEqual(suffixes, [
            ([['as']], {'case': 'nom', 'gender': 'm', 'number': 'sg'}),
            ([['o' ]], {'case': 'gen', 'gender': 'm', 'number': 'sg'}),
            ([['ui']], {'case': 'dat', 'gender': 'm', 'number': 'sg'}),
            ([['ą' ]], {'case': 'acc', 'gender': 'm', 'number': 'sg'}),
            ([['u' ]], {'case': 'ins', 'gender': 'm', 'number': 'sg'}),
            ([['e' ]], {'case': 'loc', 'gender': 'm', 'number': 'sg'}),
            ([['e' ]], {'case': 'voc', 'gender': 'm', 'number': 'sg'}),
        ])

    def test_define_prefix(self):
        paradigm = self.paradigms.get('jūr/a')
        suffixes = list(paradigm.affixes('suffixes'))
        suffixes = [sfx[0][0] for sfx, symbols in suffixes]
        self.assertEqual(suffixes, [
            'a', 'os', 'ai', 'ą', 'a', 'oje', 'a',
        ])

    def test_replace(self):
        paradigm = self.paradigms.get('Jon/as')
        suffixes = list(paradigm.affixes('suffixes'))
        self.assertEqual(suffixes, [
            ([['as']], {'case': 'nom', 'gender': 'm', 'number': 'sg'}),
            ([['o' ]], {'case': 'gen', 'gender': 'm', 'number': 'sg'}),
            ([['ui']], {'case': 'dat', 'gender': 'm', 'number': 'sg'}),
            ([['ą' ]], {'case': 'acc', 'gender': 'm', 'number': 'sg'}),
            ([['u' ]], {'case': 'ins', 'gender': 'm', 'number': 'sg'}),
            ([['e' ]], {'case': 'loc', 'gender': 'm', 'number': 'sg'}),
            ([['ai']], {'case': 'voc', 'gender': 'm', 'number': 'sg'}),
        ])

    def test_prefix(self):
        paradigm = self.paradigms.get('brol/el/is')
        suffixes = list(paradigm.affixes('suffixes'))
        self.assertEqual(suffixes, [
            ([['el', 'is' ]], {'case': 'nom', 'gender': 'm', 'number': 'sg'}),
            ([['el', 'io' ]], {'case': 'gen', 'gender': 'm', 'number': 'sg'}),
            ([['el', 'iui']], {'case': 'dat', 'gender': 'm', 'number': 'sg'}),
            ([['el', 'į'  ]], {'case': 'acc', 'gender': 'm', 'number': 'sg'}),
            ([['el', 'iu' ]], {'case': 'ins', 'gender': 'm', 'number': 'sg'}),
            ([['el', 'yje']], {'case': 'loc', 'gender': 'm', 'number': 'sg'}),
            ([['el', 'i'  ]], {'case': 'voc', 'gender': 'm', 'number': 'sg'}),
        ])

    def test_multiple_forms(self):
        paradigm = self.paradigms.get('vėj/as')
        suffixes = list(paradigm.affixes('suffixes'))
        self.assertEqual(suffixes, [
            ([['as' ]], {'case': 'nom', 'gender': 'm', 'number': 'sg'}),
            ([['o'  ]], {'case': 'gen', 'gender': 'm', 'number': 'sg'}),
            ([['ui' ]], {'case': 'dat', 'gender': 'm', 'number': 'sg'}),
            ([['ą'  ]], {'case': 'acc', 'gender': 'm', 'number': 'sg'}),
            ([['u'  ]], {'case': 'ins', 'gender': 'm', 'number': 'sg'}),
            ([['uje'],
              ['yje']], {'case': 'loc', 'gender': 'm', 'number': 'sg'}),
            ([['i'  ]], {'case': 'voc', 'gender': 'm', 'number': 'sg'}),
        ])

    def test_multiple_extends(self):
        paradigm = self.paradigms.get('vežim/aičiai')
        suffixes = list(paradigm.affixes('suffixes'))
        self.assertEqual(suffixes, [
            ([['ait', 'i', 'ai'  ]], {'case': 'nom', 'gender': 'm', 'number': 'pl'}),
            ([['ait', 'i', 'ų'   ]], {'case': 'gen', 'gender': 'm', 'number': 'pl'}),
            ([['ait', 'i', 'ams' ]], {'case': 'dat', 'gender': 'm', 'number': 'pl'}),
            ([['ait', 'i', 'us'  ]], {'case': 'acc', 'gender': 'm', 'number': 'pl'}),
            ([['ait', 'i', 'ais' ]], {'case': 'ins', 'gender': 'm', 'number': 'pl'}),
            ([['ait', 'i', 'uose']], {'case': 'loc', 'gender': 'm', 'number': 'pl'}),
        ])


class ParadigmPrefixMethodTests(unittest.TestCase):
    """
    Pradigm.prefx method can be called using two ways:

    1. Specifying one prefix for all difined affixes:

           prefix:
             suffixes: el

    2. Specifying particular affixes to prefix:

           prefix:
             suffixes:
               case:
                 nom: el

    """
    def test_no_prefix(self):
        paradigm = Paradigm(None, {})
        ext = dict()
        kind = 'suffixes'
        symkey = 'case'
        symbol = 'nom'
        affix = ['is']

        self.assertEqual(
            paradigm.prefix(ext, kind, symkey, symbol, affix), ['is'])

    def test_prefix_1(self):
        paradigm = Paradigm(None, {})
        ext = dict(prefix=dict(suffixes='el'))
        kind = 'suffixes'
        symkey = 'case'
        symbol = 'nom'
        affix = ['is']

        self.assertEqual(
            paradigm.prefix(ext, kind, symkey, symbol, affix), ['el', 'is'])

    def test_prefix_2(self):
        paradigm = Paradigm(None, {})
        ext = dict(prefix=dict(suffixes=dict(case=dict(nom='el'))))
        kind = 'suffixes'
        symkey = 'case'
        symbol = 'nom'
        affix = ['ai']

        # Everything matches, add prefix
        self.assertEqual(
            paradigm.prefix(ext, kind, symkey, symbol, affix), ['el', 'ai'])

        # Symbol doesnot match, do not add prefix
        symbol = 'gen'
        self.assertEqual(
            paradigm.prefix(ext, kind, symkey, symbol, affix), ['ai'])


class ParadigmExtendsTests(unittest.TestCase):
    def test_extends_prefix(self):
        paradigms = yaml.load('''\
        - key: case
          symbols:
          - nom

        - key: akm/as
          define:
            suffixes:
              case:
              - as

        - key: akm/uk/as
          extends:
          - keys: akm/as
            prefix:
              suffixes: uk

        - key: akm/en/uk/as
          extends:
          - keys: akm/uk/as
            prefix:
              suffixes: en
        ''')
        paradigms = ParadigmCollection(paradigms)
        paradigm = paradigms.get('akm/en/uk/as')
        suffixes = list(paradigm.affixes('suffixes'))
        self.assertEqual(suffixes, [([['en', 'uk', 'as']], {'case': 'nom'})])
