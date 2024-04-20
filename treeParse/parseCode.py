from tree_sitter import Language, Parser
import tree_sitter_python as tspython
from networkx import Graph  

# Relationship constants for easier access
RELATIONSHIPS = {
    "code": "has",  
    "callingFunction":"calls",
    "defineFunction":"defines",
    "repository":"contains",
}

#Function to extract all the functions defined and create seperate nodes for them
def extractFunctions(code,graph):
  #tree-sitter for python
  PY_LANGUAGE = Language(tspython.language(), "python")
  parser = Parser()
  parser.set_language(PY_LANGUAGE)
  #parse the code into an AST
  tree = parser.parse(bytes(code,"utf8"))

  #check if the node is a function definition, and then add the function name as a seperate node with the parameters as additional properties
  def addFunctions(node):
    if node.type=="function_definition":
      #extract function name
      functionName = node.children[1].text.decode("utf8")
      functionParams=node.child_by_field_name("parameters")
      params=list()
      #list all parameters
      for param in functionParams.children:
          if param.type not in("(",")",","):
            params.append(param.text.decode("utf8"))
      #add user-defined function as a seperate node to the graph
      graph.add_node(functionName, type="function", parameters=params)
    
    #recursively check through the entire code snippet for other function definitions
    for child in node.children:
      addFunctions(child)
  
  #start extracting user-defined functions from the level of root node's children
  addFunctions(tree.root_node)
  return graph

#Add the AST nodes on to the graph (which now has only user-defined functions as nodes) and create relationships with user-defined functions
def createGraph(code,graph,folder,file):
  #tree-sitter for python
  PY_LANGUAGE = Language(tspython.language(), "python")
  parser = Parser()
  parser.set_language(PY_LANGUAGE)
  tree = parser.parse(bytes(code,"utf8"))
  
  #Add all AST nodes and create relationships with functions wherever needed
  def addNode(node,parent=None):
    
    if parent:
      nodeType="generalNode"
      #create a node on the graph for every node on the AST
      graph.add_node(node, type=nodeType)
      #Add an edge to signify the code flow similar to the parent-child relationship in an AST
      graph.add_edge(parent, node, relation=RELATIONSHIPS.get("code"))

      #if the line is a function definition, create a relationship that signifies that this line defines a specific function (already present as a node)
      if node.type=="function_definition":
        functionName = node.children[1].text.decode("utf8")
        graph.add_edge(functionName, node, relation=RELATIONSHIPS.get("defineFunction"))

       #if the line is a function call, create a relationship that signifies that this line calls a specific function (already present as a node)
      if node.type=="call":
        functionName = node.child_by_field_name("function").text.decode("utf8")
        #the below check if to ensure that we create the "calls" relationship only for functions created by the user and not for built-in functions
        if graph.has_node(functionName):
          graph.add_edge(functionName, node, relation=RELATIONSHIPS.get("callingFunction"))

    #recursively check through the entire code snippet to cover AST nodes for the entire code
    for child in node.children:
      addNode(child, node)

  #create a node, relationship for the repo and file to provide additional context on the location of any code snippet
  graph.add_node(folder,type="repository")
  graph.add_node(file,type="file")
  graph.add_edge(folder, file, relation=RELATIONSHIPS.get("repository"))

  #start adding AST nodes on to the graph
  addNode(tree.root_node,file)
  return graph
