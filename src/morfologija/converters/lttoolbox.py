import sys
import yaml

from ..lexemes import Lexeme
from ..grammar import Node
from ..utils   import first


class Converter(object):
    def __init__(self, lmdb, mdb, paradigms):
        self.lmdb_file = lmdb_file
        self.lmdb = lmdb
        self.mdb = mdb
        self.paradigms = paradigms

    def build_symbols(self):
        for node in self.mdb.fields:
            symbol = node.get('symbol')
            if symbol is not None:
                yield '<sdef n=%-10s c="%s"/>' % (
                    '"%s"' % node['symbol'], node['label']
                )
            else:
                yield '<!-- sdef n=%-10s c="%s"/ -->' % (
                    '"%s"' % '', node['label']
                )

        for paradigm in self.paradigms:
            if paradigm['type'] == 'symbol':
                yield '<sdef n=%-10s c="%s"/>' % (
                    '"%s"' % paradigm['key'], paradigm['label']
                )

    def get_field_values(self, node, params):
        fields = []
        for node in node.fields:
            if 'code' in node:
                code = node['code']
                n = code - 4
                assert n < len(params), ('%s not in params: %r' % (n, params))
                value_node = self.get_node_by_field(
                    node.get('fields', []), 'code', params[n]
                )
                assert value_node is not None, (
                    '%s not in %r' % (params[n], node))
                fields.append((node, value_node))
            else:
                fields.extend(self.get_field_values(node, params))
        return fields

    def build_paradigms(self):
        paradigms = {
            p['key']: p for p in self.paradigms if 'key' in p
        }
        import pprint; pprint.pprint(paradigms)

        for i, line in enumerate(self.lmdb):
            line = line.strip()
            #if line.endswith('1 1 1 1 3 1 1 0 0 2 0 0 0 0 1 1 0 0 0 0'):
            if line.startswith('Adomas '):
                print(line)
                lexeme = Lexeme(self.mdb, line)

                pardefs = []
                for node in lexeme.properties:
                    pardefs.extend(lexeme.get_pardefs(node))

                print(list(pardefs))

                for node in lexeme.nodes:
                    parent = first(node.parents(code__isnull=False))
                    print('{:2}: {}'.format(parent.code, parent.label))
                    print('    {}: {}'.format(node.code, node.label[:72]))
                    print()

                #for node in self.mdb.

                yield '<pardef />'

                # <pardef n="BASE__bais/ingas">
                #   <e><p><l>ingas</l><r><s n="m"/><s n="sg"/><s n="nom"/></r></p></e>
                # </pardef>

                break

    def build_dix(self):
        yield '<?xml version="1.0" encoding="UTF-8"?>'
        yield '<dictionary>'

        yield '  <alphabet>AĄBCČDEĘĖFGHIĮYJKLMNOPRSŠTUŲŪVZŽaąbcčdeęėfghiįyjklmnoprsštuųūvzž</alphabet>'

        yield '  <sdefs>'
        #for line in self.build_symbols():
        #    yield '    ' + line
        yield '  </sdefs>'

        yield '  <pardefs>'
        for line in self.build_paradigms():
            yield '    ' + line
        yield '  </pardefs>'

        yield '  <section id="main" type="standard">'

        #for line in gen_entries(lmdb, '    '):
        #    yield line

        yield '  </section>'

        yield '</dictionary>'
