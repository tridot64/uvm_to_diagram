import graphviz

dot = graphviz.Digraph('structs', filename='structs.gv', node_attr={'shape' : 'record'}, comment='The Round Table')
#dot = graphviz.Graph(comment='Round Table')

dot.node ('A',r'{class|methods|variables}')
dot.node ('B','Lancelot the brave')
dot.node ('L','Bedevere the Wise')
dot.edges(['AB', 'AL', 'BL'])
dot.view()