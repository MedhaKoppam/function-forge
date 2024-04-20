import os
from networkx import Graph

from parseCode import *

#Directory which has code repo
folderPath="Tic-Tac-Toe-AI"
#Extracting name of files in the repo
fileNames = os.listdir(f"codeRepositories/{folderPath}")
#creating networkx graph instance
graph=Graph()

#First, creating seperate nodes for functions defined in the code. This is done in the beginning so that all definitions and calls in any file can be linked to these nodes as the rest of the repo is parsed. This also by default ensures that only user created functions can be modified
for file in fileNames:
    filePath=f"codeRepositories/{folderPath}/{file}"
    with open(filePath, "r") as f:
        code = f.read()
    graph=extractFunctions(code,graph)

#Then, all other nodes from AST are added to the grapg, and the required edges are created for function calls and definitions to the function nodes added in the above step
for file in fileNames:
    filePath=f"codeRepositories/{folderPath}/{file}"
    with open(filePath, "r") as f:
        code = f.read()
    graph=createGraph(code,graph,folderPath,file)

#Uncomment the below code if you wish to see the nodes and relationships created during this parseing process
# print("Function Nodes:")
# for node in graph.nodes(data=True):
#     if node[1]["type"]=="function":
#         print(node[0])

# print("\nRelationships:")
# for callee, caller, data in graph.edges(data=True):
#     print(f"{caller} - {data['relation']} - {callee}\n")