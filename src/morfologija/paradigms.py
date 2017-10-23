from .utils import assign
from .utils import getnested


class Symbol(object):
    pass


class Paradigm(object):
    def __init__(self, paradigms, paradigm):
        self.paradigms = paradigms
        assign(self, paradigm, (
            ('key', None),
            ('symbols', []),
            ('type', None),
            ('label', ''),
            ('define', dict()),
            ('extends', []),
            ('kind', None),
            ('name', None),
            ('override-symbols', True),
        ))

    def normalize_forms(self, forms):
        forms = forms if isinstance(forms, list) else [forms]
        forms = [a if isinstance(a, list) else [a] for a in forms]
        return forms

    def replace(self, ext, kind, symkey, symbol, forms):
        repl = getnested(ext, ('replace', kind, symkey), {})
        if symbol in repl:
            if repl[symbol] is None:
                return None
            else:
                return self.normalize_forms(repl[symbol])
        return forms

    def prefix(self, ext, kind, symkey, symbol, affixes):
        """See: ParadigmPrefixMethodTests"""
        prefixes = getnested(ext, ('prefix', kind))
        if prefixes is None:
            return affixes
        if isinstance(prefixes, str):
            return [prefixes] + affixes
        if isinstance(prefixes, list):
            return prefixes + affixes
        prefix = getnested(prefixes, (symkey, symbol))
        if prefix is not None:
            return [prefix] + affixes
        return affixes

    def apply_extensios(self, extensions, kind, symkey, symbol, forms):
        for ext in extensions:
            forms = self.replace(ext, kind, symkey, symbol, forms)
            if forms is None: return None
            forms = [
                self.prefix(ext, kind, symkey, symbol, affix)
                for affix in forms
            ]
        return forms

    def definitions(self, kind, extensions=None):
        extensions = extensions or []
        affixes = self.define.get(kind, dict())
        for symkey, affixes in affixes.items():
            symbols = self.paradigms.get(symkey).symbols
            for symbol, forms in zip(symbols, affixes):
                forms = self.normalize_forms(forms)
                forms = self.apply_extensios(extensions, kind, symkey, symbol,
                                             forms)
                if forms is not None:
                    yield forms, dict(self.symbols, **{symkey: symbol})

    def extensions(self, kind, extensions=None):
        extensions = extensions or []
        for extension in self.extends:
            keys = extension['keys']
            keys = keys if isinstance(keys, list) else [keys]
            for key in keys:
                paradigm = self.paradigms.get(key)
                affixes = paradigm.affixes(kind, [extension] + extensions)
                for forms, symbols in affixes:
                    yield forms, symbols

    def affixes(self, kind, ext=None):
        for forms, symbols in self.definitions(kind, ext):
            yield forms, symbols

        for forms, symbols in self.extensions(kind, ext):
            yield forms, symbols




class ParadigmCollection(object):
    def __init__(self, paradigms):
        self.paradigms = dict()
        for paradigm in paradigms:
            key = paradigm.get('key')
            assert key is not None
            self.paradigms[key] = Paradigm(self, paradigm)

    def get(self, key):
        return self.paradigms[key]
