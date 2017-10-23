import collections

from .utils import first
from .soundchanges import affrication
from .syllabification import syllabificate


class Lexeme(object):
    """Morphological database entry.

    lexeme
        A word form, mostly lemma form.

    lemma
        Word lemma form, None if lemma is same as lexeme.

    source
        Source from where information about this lexeme is taken.

    pos
        Part of speech node from grammar tree.

    properties
        Part of speech properties as nodes from grammar tree.

    names
        Dictionary of flattened property and value names for this lexeme.

    """

    CheckNumber = collections.namedtuple('CheckNumber', 'eq gt lt gte lte')
    CheckNumber_defaults = CheckNumber(eq=None, gt=None, lt=None, gte=None,
                                       lte=None)

    def __init__(self, grammar, paradigms, sources, line):
        fields = line.split()
        params = list(map(int, fields[4:]))
        self.lexeme, source, lemma, pos = fields[:4]
        self.paradigms = paradigms
        self.source = sources.get(code=int(source))
        self.lemma = None if lemma == '-' else lemma
        self.pos = grammar.get_pos_by_code(int(pos))
        assert self.pos is not None
        self.properties = []
        for field, value_code in zip(self.pos.fields.values(), params):
            value = field.get_value_by_code(value_code)
            if value is None:
                for value in field.values.values():
                    print('value.label: %s' % value.label)
                    print('value.code: %s' % value.code)
                    if value.code == value_code:
                        print('  returing...')
                raise Exception(
                    'Unknown value {val} for field {fld} ({label}) in {line}.'.
                    format(val=value_code, fld=field.code, line=line,
                           label=field.label)
                )
            self.properties.append(value)
        self.names = dict(self.get_names())
        self.symbols = dict(self.get_symbols())
        self.stem = self.get_stem()
        self.filters = self.get_filters()

    def get_names(self):
        for value in self.properties:
            if value.node.value is not None:
                key = first(value.node.parents(name__isnull=False)).name
                if isinstance(value.node.value, list):
                    val = value.node.value
                else:
                    val = [value.node.value]
                yield key, val
            elif value.node.name is not None:
                key = first(value.node.parents(name__isnull=False)).name
                val = value.node.name
                yield key, [val]

    def get_symbols(self):
        for value in self.properties:
            if value.node.symbol is not None:
                key = first(value.node.parents(name__isnull=False)).name
                val = value.node.symbol
                yield key, val

    def get_filters(self):
        filters = []
        for value in self.properties:
            if value.node.restrict:
                filters.append(('restrict', value.node.restrict))
        return filters

    def check_properties(self, properties):
        for k, v in properties.items():
            if k not in self.names:
                return False

            names = self.names[k]
            names = names if isinstance(names, list) else [names]
            if v not in names:
                return False
        return True

    def check_restrict(self, restrictions, form, symbols):
        """Return True if restriction is in effect."""
        for restriction in restrictions:
            for key, rsymbols in restriction.get('symbols', {}).items():
                rsymbols = rsymbols if isinstance(rsymbols, list) else [rsymbols]
                if key in symbols and symbols[key] not in rsymbols:
                    return True
        return False

    def check_filters(self, filters, value, form, symbols):
        """Returns True if filters matches."""
        for name, params in filters:
            if name == 'restrict' and self.check_restrict(params, form, symbols):
                return False
        return True

    def check_number(self, number, options):
        cn = self.CheckNumber_defaults._replace(**options)
        if cn.eq is not None and cn.eq != number:
            return False
        if cn.gt is not None and number <= cn.gt:
            return False
        if cn.lt is not None and number >= cn.lt:
            return False
        if cn.gte is not None and number < cn.gte:
            return False
        if cn.lte is not None and number > cn.lte:
            return False
        return True

    def get_pardefs(self, node):
        """Exctract paradigm definition keys from node ``pardefs`` property.

        Node ``pardefs`` property example:

        .. code-block:: yaml

           pardefs:
           - - key: Jon/as
               properties:
                 properness: name
             - key: vyr/as
           - - key: eln/ias
               endswith: ias
             - key: vėj/as
           - vyr/ai

        Each ``pardefs`` list item can be string or list. If it is string, then
        paradigm definition key is added immediately, if it is list, then first
        matching item is added.

        To know if item matches, these fields are used:

        properties
            Checks if filter for all part of speech properties matches given
            values. See ``get_names`` method to understand where values for
            filter is taken from.

        endswith
            Checks if lexeme ends with specified string.

        syllables
            Checks if lexeme has specified numbe of syllables.

        """
        for pardef in node.pardefs:
            if isinstance(pardef, list):
                for item in pardef:
                    if (
                        'properties' in item and
                        not self.check_properties(item['properties'])
                    ):
                        continue
                    if (
                        'endswith' in item and
                        not self.lexeme.endswith(item['endswith'])
                    ):
                        continue
                    if (
                        'syllables' in item and
                        not self.check_number(len(syllabificate(self.lexeme)),
                                              item['syllables'])
                    ):
                        continue
                    if (
                        'lemmas' in item and
                        (self.lemma or self.lexeme) not in item['lemmas']
                    ):
                        continue
                    yield item['key']
                    break
            else:
                yield pardef

    def prepare_forms(self, forms):
        for suffixes in forms:
            stem, suffixes = affrication(self.stem, suffixes)
            yield stem, suffixes

    def affixes(self, value, paradigm, kind):
        for forms, symbols in paradigm.affixes(kind):
            if self.check_filters(self.filters, value, forms, symbols):
                if paradigm.override_symbols:
                    symbols = dict(symbols, **self.symbols)
                forms = self.prepare_forms(forms)
                yield forms, symbols

    def get_stem(self):
        for value in self.properties:
            if not value.field.node.lemma: continue
            for pardef in self.get_pardefs(value.node):
                paradigm = self.paradigms.get(pardef)
                for forms, symbols in paradigm.affixes('suffixes'):
                    suffix = ''.join(forms[0])
                    stem = self.lexeme[:-len(suffix)]
                    return stem

        raise Exception('Can not find lemma for %s.' % self.pos.label)

    def genforms(self):
        for value in self.properties:
            for pardef in self.get_pardefs(value.node):
                paradigm = self.paradigms.get(pardef)
                for forms, symbols in self.affixes(value, paradigm, 'suffixes'):
                    lexeme = [
                        '%s/%s' % (stem, '/'.join(suffix))
                        for stem, suffix in forms
                    ]
                    yield lexeme, symbols
