import yaml
import os.path

from ..nodes import Node
from ..grammar import Grammar
from ..lexemes import Lexeme
from ..paradigms import ParadigmCollection


test_dir = os.path.dirname(__file__)
data_dir = os.path.join(test_dir, '..', '..', '..', 'data')
data_dir = os.path.abspath(data_dir)
data = lambda name: os.path.join(data_dir, name)

with open(data('grammar.yaml'), encoding='utf-8') as f:
    grammar = yaml.load(f)
grammar = Node(dict(nodes=grammar))
grammar = Grammar(grammar)

with open(data('sources.yaml'), encoding='utf-8') as f:
    sources = yaml.load(f)
sources = Node(dict(nodes=sources))

with open(data('paradigms.yaml'), encoding='utf-8') as f:
    paradigms = yaml.load(f)
paradigms = ParadigmCollection(paradigms)



def create_lexeme(word, pos, **kwargs):
    pos = grammar.poses[pos]
    numbers = [
        field.values[kwargs.get(name, field.get_default_value().name)].code
        for name, field in pos.fields.items()
    ]
    numbers = ' '.join(map(str, numbers))
    line = ('{word} 1 - {pos} {numbers}').format(word=word, pos=pos.code,
                                                 numbers=numbers)
    lexeme = Lexeme(grammar, paradigms, sources, line)
    return lexeme

def genlexemes(word, pos, **kwargs):
    assert isinstance(pos, str)
    lexemes = []
    lexeme = create_lexeme(word, pos, **kwargs)
    symorder = ('number', 'gender', 'case')
    for forms, symbols in lexeme.genforms():
        symbols = [symbols[key] for key in symorder]
        lexemes.append((forms, symbols))
    return lexemes
