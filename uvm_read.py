import re
import os

from uml_diagram import *\


directory = os.fsencode('uvm_files')

#dictionary of key : string and val : list of string
include_vals = {}
#dictionary of dictionary
classes_dict = {}
#dictionary of lists
classes_function = {}

for file in os.listdir(directory):
    filename = os.fsdecode(file)
    if re.search(r'\.sv',filename):
        # Inlcude files from the sv to form associations
        include_list = []
        class_extend = {}
        with open('uvm_files\\' + filename,'r') as lines:
            class_name_val = 'default'
            function_list = []
            tasks_list = []
            attr_list = []

            for line in lines:
                if(len(line.split())):
                    if(line.split()[0][0] != "/"): #neglect comments
                        #class start here
                        if (re.search(r'^class.*\ ', line)):
                            #get class instantiated
                            store_val = line.split()
                            class_name_val = store_val[1]
                            class_extend[store_val[1]] = store_val[3]

                        #attributes
                        if (class_name_val != "default") and (re.search(r'\ bit',line)):
                            line_split = line.split()
                            pos = line.find("bit")
                            #find the position of keyword bit and append rest
                            to_add = line[(pos+3):-1]
                            attr_list.append(to_add.lstrip())

                        #task
                        """ If the class_name_val is set to default then the declaration of the function is not inside a class : endclass"""
                        if ((class_name_val != "default") and (re.search(r'\ task',line))):
                            line_split = line.split()
                            val = ' '
                            pos = 0
                            #find the bracket position in the line
                            for i in range(len(line_split)):
                                if('(' in line_split[i]):
                                    val = line_split[i]
                                    pos = i
                                    break
                            val = val.split('(')
                            if(val[0] == ""): # name of the task if it isnt adjacent to the brackets
                                tasks_list.append(line_split[pos-1])
                            else:
                                tasks_list.append(val[0])

                        #function
                        if ((class_name_val != "default") and (re.search(r'\ function',line))):
                            line_split = line.split()
                            val = ''
                            pos = 0
                            #find the position of the bracket character in the line
                            for i in range(len(line_split)):
                                if ('(' in line_split[i]):
                                    val = line_split[i]
                                    pos = i
                                    break
                            val = val.split('(')
                            if (val[0] == ''): #name of the function is not adjacent to the '('
                                function_list.append(line_split[pos-1]) 
                            else:
                                function_list.append(val[0])

                        #endclass
                        if (re.search(r'endclass',line)):
                            final_list = [function_list, tasks_list,attr_list]
                            classes_function[class_name_val] = final_list
                            class_name_val = 'default'
                            function_list = []
                            tasks_list = []
                            attr_list = []

                        #includes
                        if (re.search(r'^\`include',line)):
                            #get only the include file name
                            store_val = line.split('\"')
                            include_list.append(store_val[1])
        include_vals[filename] = include_list
        classes_dict[filename] = class_extend

diagram_array = {}

all_classes_list = []


def find_class(class_name = ''):
    """returns the key and the position of the list in classes_dict for the class_name """
    for i in classes_dict:
        for j in range(len(classes_dict[i])):
            if (classes_dict[i][j] == class_name):
                return i,j

#list all the classes in the model
for i in classes_dict:
    for j in classes_dict[i]:
        all_classes_list.append(j)

#build_phase capture to see which class is including who (UVM feature)
for file in os.listdir(directory):
    filename = os.fsdecode(file)
    if(re.search(r'\.sv',filename)):
        #class name in classes_dict
        for c_name in classes_dict[filename]:
            #find build_phase in c_name
            valid_instances = []
            if("build_phase" in classes_function[c_name][0]):
                #its a bad way to do this but makes sense
                with open('uvm_files\\' + filename, 'r') as lines:
                    toggle = 0
                    c_name_toggle = 0
                    create_list = []
                    get_set_list = []
                    instance_dict = {}
                    for line in lines:
                        if(len(line.split())):
                            if(line.split()[0][0] not in ['/','`'] ):
                                if c_name_toggle and (line.split()[0] in all_classes_list):
                                    instance_dict[line.split()[0]] = line.split()[1]
                                if (re.search(' ' + c_name,line) or re.search(r'endclass',line)):
                                    c_name_toggle = not c_name_toggle
                                if (c_name_toggle and re.search(r' build_phase',line)):
                                    toggle = not toggle
                                if toggle and re.search(r'::create',line):
                                    create_list.append(line.split()[0])
                                if toggle and re.search(r'::get',line):
                                    get_set_list.append(line.split()[1].split(')')[0])
                    for ins_c_name in instance_dict:
                            ins_name = instance_dict[ins_c_name]
                            if (';' in ins_name):
                                ins_name = ins_name.split(';')[0]
                            if ins_name in create_list:
                                #put it in the class diagram for association
                                valid_instances.append(ins_c_name + ' as ' + ins_name)
            
            #add it to the classes_function
            classes_function[c_name].append(valid_instances)

uml_class_dict = {}
                             
#make class array of filename that can create multiple pdfs per file
master = graphviz.Graph(name= " big picture",node_attr={'shape' : 'record'})

for i in classes_dict:
    diag_classes_list = []
    for c_name in classes_dict[i]:
        #classes_function[c_name][0] -> function_list
        #classes_function[c_name][1] -> tasks_list
        #classes_function[c_name][2] -> attr_list
        uml_handle = uml_diagram_class(master_graph= master, class_name=c_name, class_attr = classes_function[c_name][2], class_methods = [classes_function[c_name][0], classes_function[c_name][1]], inst= classes_function[c_name][3])
        uml_class_dict[c_name] = uml_handle
        diag_classes_list.append(uml_handle)
    diagram_array[i] = diag_classes_list

#print(include_vals)
#print("--------------------------------------------------------------------------")

dict_key = {}
color_dict = ['lightblue', 'lightgrey', 'lightyellow', 'lightgreen',  'red', 'green']

def recur_draw(c_name,c,i):
    with c.subgraph(name = 'cluster_' + c_name) as dict_key[i]:
        insts = classes_function[c_name][3]
        dict_key[i].node(c_name + ' ' + str(i),uml_class_dict[c_name].ret_node(), color = 'white')
        dict_key[i].attr(style = "filled", color = color_dict[i-1])
        with dict_key[i].subgraph(name = 'cluster_' + c_name + '_ins') as dict_key[i+1]:
            for inst in insts:
                recur_draw(inst.split()[0],dict_key[i+1],i+2)

per_class = {}

#draw instances inside a subgraph
for i in classes_dict:
    for c_name in classes_dict[i]:
        per_class[c_name] = graphviz.Digraph(name = c_name,filename= 'uvm_output\\' + c_name + '.gv',node_attr= {'shape' : 'record'})
        if('uvm_' not in classes_dict[i][c_name]):
            base_class = classes_dict[i][c_name].split(';')[0]
            with per_class[c_name].subgraph(name= 'cluster_' + base_class) as c:
                c.node(base_class,uml_class_dict[base_class].ret_node())
                c.attr(style = 'filled', color = 'chocolate')
                with c.subgraph(name = 'cluster_' + base_class + '_ins') as d:
                    for get_instances in classes_function[base_class][3]:
                        recur_draw(get_instances.split()[0],d,0)
            per_class[c_name].node(base_class, uml_class_dict[base_class].ret_node())
        with per_class[c_name].subgraph(name= 'cluster_' + c_name) as c:
            c.node(c_name,uml_class_dict[c_name].ret_node())
            c.attr(style = 'filled', color = 'chocolate')
            with c.subgraph(name = 'cluster_' + c_name + '_ins') as d:
                for get_instances in classes_function[c_name][3]:
                    recur_draw(get_instances.split()[0],d,0)
        if('uvm_' not in classes_dict[i][c_name]):
            #set extends if it isnt a base class
            base_class = classes_dict[i][c_name].split(';')[0]
            per_class[c_name].edge(base_class,c_name,ltail = 'cluster_' + base_class,lhead = 'cluster_' + c_name, arrowhead = "vee", style = "dashed")

#for i in master.body:
#    if(i.split()[0] == 'subgraph' or i.split()[0] == '}'):
#        print(i)

for i in per_class:
    per_class[i].render() 