import yaml
import unittest
import collections

from ..nodes import Node
from ..grammar import Grammar
from ..lexemes import Lexeme
from ..paradigms import ParadigmCollection

RES = dict(
    paradigms = """\
- key: case
  symbols:
  - nom
  - gen
  - dat
  - acc
  - ins
  - loc
  - voc

- key: gerv/ės
  symbols:
    gender: f
    number: pl
  define:
    suffixes:
      case:
      - ės
      - ių
      - ėms
      - es
      - ėmis
      - ėse

- key: dėd/ės
  symbols:
    gender: f
    number: pl
  extends:
  - keys: gerv/ės
    replace:
      suffixes:
        case:
          gen: žių

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

- key: mart/i
  extends:
  - keys: jūr/a
    replace:
      suffixes:
        case:
          nom: i

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

- key: eln/ias
  symbols:
    gender: m
    number: sg
  define:
    suffixes:
      case:
      - ias
      - io
      - iui
      - ią
      - iu
      - yje
      - [i, y]

- key: vyr/as
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
      - [e, ai]

- key: Jon/as
  extends:
  - keys: vyr/as
    replace:
      suffixes:
        case:
          voc: ai

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

""",

    grammar = """\
nodes:
- code: 1
  nodes:
  - code: 4
    name: declension
    lemma: true
    nodes:
    - code: 1
      pardefs:
      - - key: Jon/as
          properties:
            properness: name
        - key: vyr/as
      - vyr/ai
    - code: 2
      pardefs:
      - - key: eln/ias
          endswith: ias
        - key: vėj/as
      - vyr/ai
    - code: 3
      pardefs:
      - dėd/ės
    - code: 4
      pardefs:
      - - key: mart/i
          endswith: i
        - key: jūr/a
  - code: 5
    name: properness
    nodes:
    - code: 1
    - code: 2
      name: name
  - code: 6
    name: gender
    nodes:
    - code: 1
      symbol: m
    - code: 2
      symbol: f
  - code: 7
    name: number
    nodes:
    - code: 1
      name: singular, plurar
    - code: 2
      name: plural
      restrict:
      - symbols:
          number: pl
""",
)

Property = collections.namedtuple('Property', 'default, values')

PROPERTIES = [
    ('pos', Property(
        default='noun',
        values={'noun': 1},
    )),
    ('declension', Property(
        default=1,
        values={1: 1, 2: 2, 3: 3, 4: 4},
    )),
    ('properness', Property(
        default=None,
        values={None: 1, 'name': 2},
    )),
    ('gender', Property(
        default='masculine',
        values={'masculine': 1, 'feminine': 2},
    )),
    ('number', Property(
        default='singular, plurar',
        values={'singular, plurar': 1, 'plural': 2},
    )),
]


class NodeTests(unittest.TestCase):
    def setUp(self):
        grammar = yaml.load(RES['grammar'])
        self.grammar = Grammar(Node(grammar))
        self.source = Node(dict(nodes=[dict(code=1, label='')]))
        paradigms = yaml.load(RES['paradigms'])
        self.paradigms = ParadigmCollection(paradigms)

    def lexeme(self, word, **kwargs):
        numbers = [
            prop.values[kwargs.get(name, prop.default)]
            for name, prop in PROPERTIES
        ]
        numbers = ' '.join(map(str, numbers))
        line = ('{word} 1 - {numbers}').format(word=word, numbers=numbers)
        lexeme = Lexeme(self.grammar, self.paradigms, self.source, line)
        return lexeme

    def pardefs(self, word, **kwargs):
        lexeme = self.lexeme(word, **kwargs)
        value = lexeme.properties[0]
        return list(lexeme.get_pardefs(value.node))

    def lexemes(self, word, **kwargs):
        lexemes = []
        lexeme = self.lexeme(word, **kwargs)
        symorder = ('number', 'gender', 'case')
        for node in lexeme.properties:
            for pardef in lexeme.get_pardefs(node):
                paradigm = self.paradigms.get(pardef)
                for forms, symbols in lexeme.affixes(paradigm, 'suffixes'):
                    symbols = [symbols[key] for key in symorder]
                    _lexeme = [
                        '%s/%s' % (stem, '/'.join(suffix))
                        for stem, suffix in forms
                    ]
                    lexemes.append((_lexeme, symbols))
        return lexemes

    def test_pardefs_properties(self):
        self.assertEqual(self.pardefs('vyras'), ['vyr/as',  'vyr/ai'])
        self.assertEqual(self.pardefs('Jonas', properness='name'), ['Jon/as',  'vyr/ai'])

    def test_pardefs_endswith(self):
        self.assertEqual(self.pardefs('vėjas',  declension=2), ['vėj/as',  'vyr/ai'])
        self.assertEqual(self.pardefs('elnias', declension=2), ['eln/ias', 'vyr/ai'])

    def test_symbols(self):
        paradigm = self.paradigms.get('dėd/ės')
        lexeme = self.lexeme('dėdė', gender='masculine')
        suffixes = [
            (forms, dict(symbols, **lexeme.symbols))
            for forms, symbols in paradigm.affixes('suffixes')
        ]
        self.assertEqual(suffixes, [
            ([['ės'  ]], {'case': 'nom', 'gender': 'm', 'number': 'pl'}),
            ([['žių' ]], {'case': 'gen', 'gender': 'm', 'number': 'pl'}),
            ([['ėms' ]], {'case': 'dat', 'gender': 'm', 'number': 'pl'}),
            ([['es'  ]], {'case': 'acc', 'gender': 'm', 'number': 'pl'}),
            ([['ėmis']], {'case': 'ins', 'gender': 'm', 'number': 'pl'}),
            ([['ėse' ]], {'case': 'loc', 'gender': 'm', 'number': 'pl'}),
        ])

    def test_check_restrict(self):
        lexeme = self.lexeme('word')
        restrictions = [{'symbols': {'number': 'pl'}}]

        # Restrictio is not in effect
        self.assertFalse(
            lexeme.check_restrict(restrictions, 'word', {'number': 'pl'}))

        # Restriction is in effect
        self.assertTrue(
            lexeme.check_restrict(restrictions, 'word', {'number': 'sg'}))

    def test_check_number(self):
        lexeme = self.lexeme('word')

        # eq
        self.assertFalse(lexeme.check_number(42, dict(eq=41)))
        self.assertTrue (lexeme.check_number(42, dict(eq=42)))

        # gt
        self.assertFalse(lexeme.check_number(42, dict(gt=43)))
        self.assertFalse(lexeme.check_number(42, dict(gt=42)))
        self.assertTrue (lexeme.check_number(42, dict(gt=41)))

        # lt
        self.assertFalse(lexeme.check_number(42, dict(lt=41)))
        self.assertFalse(lexeme.check_number(42, dict(lt=42)))
        self.assertTrue (lexeme.check_number(42, dict(lt=43)))

        # gte
        self.assertFalse(lexeme.check_number(42, dict(gte=43)))
        self.assertTrue (lexeme.check_number(42, dict(gte=42)))
        self.assertTrue (lexeme.check_number(42, dict(gte=41)))

        # lte
        self.assertFalse(lexeme.check_number(42, dict(lte=41)))
        self.assertTrue (lexeme.check_number(42, dict(lte=42)))
        self.assertTrue (lexeme.check_number(42, dict(lte=43)))

        # Multiple options
        self.assertTrue(lexeme.check_number(42, dict(lte=42, eq=42)))
        self.assertFalse(lexeme.check_number(42, dict(lte=42, eq=40)))
