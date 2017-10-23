"""Morphology database tool.

Usage:
  morfologija <lexeme> [-d <path>]

Options:
  <lexeme>              A lexeme from morphology database.
  -h --help             Show this screen.
  -d --data-dir=<path>  Data directory [default: data].

"""

import yaml
import docopt
import os.path
import textwrap

from ..nodes import Node
from ..grammar import Grammar
from ..lexemes import Lexeme
from ..paradigms import ParadigmCollection

wrapper = textwrap.TextWrapper(subsequent_indent='       ')


def print_field(field_code, field_label, value_code, value_label):
    if value_label:
        value_label = '\n'.join(wrapper.wrap(value_label))

    print('{:2}: {}'.format(field_code, field_label))

    if value_code is None:
        print('    {}'.format(value_code, value_label))
    else:
        print('    {}: {}'.format(value_code, value_label))

    print()


def print_lexeme_details(f, query, grammar, paradigms, sources, data):
    for i, line in enumerate(f, 1):
        line = line.strip()
        if line.startswith(query + ' ') or \
            line.startswith(query + '('):
            try:
                lexeme = Lexeme(grammar, paradigms, sources, line)
            except:
                print('Error in line: {}'.format(line.strip()))
                print('      in {}:{}'.format(data('lexemes.txt'), i))
                raise

            print('Leksema: {}'.format(lexeme.lexeme))
            print('Vieta: {}:{}'.format(data('lexemes.txt'), i))
            print('Eilutė: {}'.format(line.strip()))
            print('Parametrai:\n{}'.format('\n'.join([
                '    {}: {}'.format(
                    k, (', '.join(v) if isinstance(v, list) else v)
                )
                for k, v in dict(lexeme.symbols, **lexeme.names).items()
            ])))
            print()

            print_field(1, 'Šaltinis', lexeme.source.code, lexeme.source.label)
            print_field(2, 'Lemma', None, lexeme.lemma)
            print_field(3, 'Kalbos dalis', lexeme.pos.code, lexeme.pos.label)

            for value in lexeme.properties:
                print_field(value.field.code, value.field.label,
                            value.code, value.label)

                for pardef in lexeme.get_pardefs(value.node):
                    print('    [{}]'.format(pardef))
                    paradigm = paradigms.get(pardef)
                    for forms, symbols in lexeme.affixes(value, paradigm, 'suffixes'):
                        symbols = ', '.join([
                            symbols[key]
                            for key in ('number', 'gender', 'case')
                        ])

                        word = ', '.join([
                            '%s/%s' % (stem, '/'.join(suffix))
                            for stem, suffix in forms
                        ])

                        print('    {}: {}'.format(symbols, word))
                    print()


def print_query_lexemes(f, query):
    key, val = map(int, query.split('='))
    for i, line in enumerate(f, 1):
        line = line.strip()
        fields = line.split()
        fields[3:] = list(map(int, fields[3:]))
        if len(fields) > key and fields[key] == val:
            print(line)


def main():
    args = docopt.docopt(__doc__)
    data_dir = args['--data-dir']
    data = lambda name: os.path.join(data_dir, name)

    with open(data('grammar.yaml'), encoding='utf-8') as f:
        grammar = yaml.load(f)
    grammar = Grammar(Node(dict(nodes=grammar)))

    with open(data('sources.yaml'), encoding='utf-8') as f:
        sources = yaml.load(f)
    sources = Node(dict(nodes=sources))

    with open(data('paradigms.yaml'), encoding='utf-8') as f:
        paradigms = yaml.load(f)
    paradigms = ParadigmCollection(paradigms)

    with open(data('lexemes.txt'), encoding='utf-8') as f:
        query = args['<lexeme>']
        if '=' in query:
            print_query_lexemes(f, query)
        else:
            print_lexeme_details(f, query, grammar, paradigms, sources, data)
