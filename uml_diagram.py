import graphviz

class uml_diagram_class:
    name = 'default'
    attr = []
    methods = []
    masterGraph = None
    instances = []
    to_disp = ''
    
    def __init__(self, master_graph, class_name = 'default', class_attr = [], class_methods= [], inst = []) -> None:
        self.name = class_name
        self.attr = class_attr
        self.methods = class_methods
        self.instances = inst
        self.masterGraph = master_graph

    def ret_node (self):
        self.draw_class()
        return self.to_disp

    def draw_class(self):
        to_disp = r'{' + 'CLASS: ' +self.name
        attr_str = 'ATTRIBUTES:'+r'\n'
        methods_str = 'METHODS:'+r'\n'
        inst_str = 'INSTANCES:'+r'\n'
        for i in self.attr:
            attr_str = attr_str + i + r'\n'
        for i in self.methods:
            for j in i:
                methods_str = methods_str + j + '()' + r'\n'
        for i in self.instances:
            inst_str = inst_str + i + r'\n'
        to_disp = to_disp + r'|' + inst_str + r'|' + attr_str + r'|' + methods_str + r'}'
        self.to_disp = to_disp