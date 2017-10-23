class Query(object):
    def __init__(self, nodes, kwargs, recurse=True):
        self.nodes = nodes
        self.kwargs = kwargs
        self.recurse = recurse

    def __iter__(self):
        for node in self.nodes:
            if node.match(**self.kwargs):
                yield node
            elif self.recurse:
                for child in node.query(**self.kwargs):
                    yield child

    def query(self, **kwargs):
        return Query(self, kwargs, recurse=False)

    def get(self, **kwargs):
        for node in self.query(**kwargs):
            return node


class Node(object):
    """Grammar specification node.

    Grammar specification is defined as tree of nodes. This tree have three
    levels identified with nodes, that have ``code`` property. Tree levels are
    these:

    1. Part of speech.

    2. Property of part of speech.

    3. Value of property of part of speech.

    Here is example of grammar specification tree:

    .. code-block:: yaml

       - code:   1
         label:  Noun
         nodes:
         - label: Noun specialness
           nodes:
           - code: 4
             label: Properness
             nodes:
             - code: 1
               label: Appellative
             - code: 2
               label: Name
           - code:  5
             label: Neigiamumas
             nodes:
             - code: 1
               label: Positive
             - code: 2
               label: Negative

    In this example can be converted to this pseudo code:

    .. code-block:: python

       class Noun:
           properness = [Appellative, Name]
           negativity = [Positive, Negative]

    Here we see, that *Noun specialness* is omitted because this node does not
    have ``code`` property and only used for classification.

    """

    def check_isnull(node, k, v):
        value = getattr(node, k, None)
        return (value is None) == v

    def check_isempty(node, k, v):
        value = getattr(node, k, None)
        return (not value) == v

    check = dict(
        isnull=check_isnull,
        isempty=check_isempty,
    )

    def __init__(self, node, parent=None):
        self.code = node.get('code')
        self.name = node.get('name')
        self.value = node.get('value')
        self.label = node.get('label')
        self.symbol = node.get('symbol')
        self.inflective = node.get('inflective')
        self.declension = node.get('declension')
        self.paradigm = node.get('paradigm')
        self.pardefs = node.get('pardefs', [])
        self.lemma = node.get('lemma', False)
        self.restrict = node.get('restrict', [])
        self.parent = parent
        self.nodes = []
        self._init_nodes(node.get('nodes', []))

    def _init_nodes(self, nodes):
        for node in nodes:
            self.nodes.append(Node(node, self))

    def match(self, **kwargs):
        for k, v in kwargs.items():
            if '__' in k:
                k, check = k.split('__')
                if not Node.check[check](self, k, v):
                    return False
            else:
                if getattr(self, k, None) != v:
                    return False
        return True

    def query(self, **kwargs):
        return Query(self.nodes, kwargs)

    def parents(self, **kwargs):
        parent = self.parent
        while parent is not None:
            if parent.match(**kwargs):
                yield parent
            parent = parent.parent

    def get(self, **kwargs):
        for node in self.query(**kwargs):
            return node
