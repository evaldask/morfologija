import collections


class GrammarExecption(Exception): pass


class Value(object):
    def __init__(self, field, name, node):
        self.field = field
        self.name = name
        self.node = node
        self.code = node.code
        self.label = node.label


class Field(object):
    def __init__(self, pos, name, node):
        self.pos = pos
        self.name = name
        self.node = node
        self.code = node.code
        self.label = node.label
        self.values = collections.OrderedDict()

    def get_default_value(self):
        for key, val in self.values.items():
            return val

    def get_value_by_code(self, code):
        for value in self.values.values():
            if value.code == code:
                return value


class POS(object):
    def __init__(self, name, node):
        self.name = name
        self.node = node
        self.code = node.code
        self.label = node.label
        self.fields = collections.OrderedDict()


class Grammar(object):
    def __init__(self, node):
        self.node = node
        self.poses = collections.OrderedDict()
        self.init_poses()

    def init_poses(self):
        for value in self.node.query(nodes__isempty=True):
            named_nodes = self.get_named_nodes(value)
            if len(named_nodes) != 3:
                raise GrammarExecption(
                    'Eeach tree node must have exactly three named nodes, '
                    'but this [%s] node has only %d.' % (
                        ' - '.join(self.get_path_labels(value)),
                        len(named_nodes),
                    )
                )

            (pos_name,   pos), \
            (field_name, field), \
            (value_name, value) = named_nodes

            if pos_name not in self.poses:
                self.poses[pos_name] = POS(pos_name, pos)
            pos = self.poses[pos_name]

            if field_name not in pos.fields:
                pos.fields[field_name] = Field(pos, field_name, field)
            field = pos.fields[field_name]

            if value_name not in field.values:
                field.values[value_name] = Value(field, value_name, value)

    def get_named_nodes(self, node):
        names = []
        nodes = reversed([node] + list(node.parents())[:-1])
        for node in nodes:
            if node.name:
                names.append((node.name, node))
            elif node.symbol:
                names.append((node.symbol, node))
            elif node.code is not None:
                names.append((node.code, node))
        return names

    def get_path_labels(self, node):
        labels = []
        nodes = reversed([node] + list(node.parents())[:-1])
        for node in nodes:
            if node.label:
                labels.append(node.label)
            elif node.name:
                labels.append(node.name)
            elif node.symbol:
                labels.append(node.symbol)
            elif node.code:
                labels.append(node.code)
            else:
                labels.append('(unknown)')
        return labels

    def get_pos_by_code(self, code):
        for pos in self.poses.values():
            if pos.code == code:
                return pos
