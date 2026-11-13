# FIT3155 Assignment 2 Question 1
# Student Name: Sanjevan Rajasegar 

"""
References:
    This implementation is based on the suffix tree and Ukkonen's algorithm concepts taught in the FIT3155 lecture material,
    including the phase-extension structure, Rule 1, Rule 2, Rule 3, suffix links, and space-efficient edge representation logic

    Additional external references used to support understanding:
        - GeeksforGeeks, "Ukkonen's Suffix Tree Construction", Parts 1-6:
          https://www.geeksforgeeks.org/dsa/ukkonens-suffix-tree-construction-part-1/
          https://www.geeksforgeeks.org/dsa/ukkonens-suffix-tree-construction-part-2/
          https://www.geeksforgeeks.org/dsa/ukkonens-suffix-tree-construction-part-3/

        - Stack Overflow, "Ukkonen's suffix tree algorithm in plain English":
          https://stackoverflow.com/questions/9452701/ukkonens-suffix-tree-algorithm-in-plain-english

        - DFS Algorithm: https://www.geeksforgeeks.org/dsa/depth-first-search-or-dfs-for-a-graph/
"""

import sys

def read_file(file_path: str) -> str:
    """
    This code is responsible for reading an input file and converting it into a single line 
    needed for computation of Boyer Moores which receives inputs: str and pat which are single strings 

    Input: file_path, a string denoting a file path 
    Output: str, a string denoting the file content computed as a single string  
    """  
    f = open(file_path, 'r')
    singleLine = f.read().strip() # removes \t, \n etc.
    f.close()

    return singleLine 

def write_output(LCP_array: list[int], file_path: str) -> str:
    """
    This code is responsible for writing to the output file as specified in the format provided in the 
    FIT3155 specifications

    Input: matches, a list of integers denoting the number of matches based on the pattern matching
    Output: str, a string denoting the file content computed as a single string/character  
    """  
    f = open(file_path, "w")

    for value in LCP_array:
        f.write(str(value) + "\n")

    f.close()

def write_runlog(runlog: list[str], file_path: str) -> str:
    """
    This code is responsible for writing to the runlog file as specified in the format provided in the 
    FIT3155 specifications

    Input: runlog, a list of strings where each string is formatted as: "<j> <k+1> <p>" representing the 
    current iteration's alignment index, mismatch position and shift value p 
    Output: str, a string denoting the file content computed as a single string  
    """  
    f = open(file_path, "w")

    for line in runlog:
        f.write(line)

    f.close()

def add_runlog_line(runlog: list[str], line: str) -> None:
    """
    Adds one formatted line to the runlog
    """
    runlog.append(line + "\n")

# SUFFIX TREE CONSTRUCTION #

class Node:
    """
    Class Description: This class represents a Node object to construct a suffix tree which will be used for Ukkonnen's algorithm. Each node 
    stores a fixed length array of |alphabet| (ie. 256) to stores outgoing edges based on the ASCII value of the first character on each edge. 

    Approach Description: A node object doesn't store the substring it represents, rather it is used to denote the edges that branch out from it 
    using indexing (thus meeting Implementation Trick 1: Space-efficient representation of edge-labels/substrings). In doing so the children 
    array ensures constant time operations when checking for the existence of an outgoing edge 
    """
    def __init__(self):
        self.children = [None] * 256 # contains all possible ASCII characters a node can have as children 
        self.parent = None # the parent of a corresponding node, obviously the root node will have no parent 
        self.node_number = None # for debugging purposes, each node wil contain a unique number 
        self.root_node_boolean = False # for debugging purposes, a boolean will be assigned to denote the root node and will occupy a string "Root" rather than an integer node number 
        self.captured_suffix_index = None # the current suffic index that is captured by the node
        self.suffix_link = None # the suffix link of a node, which will be used in Ukkonnen's to speed up the insertion process 

class Edge:
    """
    Class Description: This class represents a Edge object to construct a suffix tree which will be used for Ukkonnen's algorithm. Each edge 
    is not stored as a seperate stirng but rather using indexed labels which point to the start and end of a substring inside the input text

    Approach Description: Storing edge labels meets Implementation Trick 1: Space-efficient representation of edge-labels/substrings, and the 
    parent and child node references allow for easier understanding during traversal for both debugging and implementation of Ukkonnen's 

    Additionally as development continued the end_index was changed from an storing an integer to storing a one-size array to support the implementation 
    trick: rapid leaf extension. The reasoning for this was to ensure updates for the end value per phase can ensure all leaf edges are updated in one-go
    thus removing the need for the explicit suffix extension found in Rule 1
    """
    def __init__(self, start_index, universal_end_index, parent_node, child_node):
        self.start_index = start_index # the start index corresponding to a substring an edge represents 
        
        # this implementation recognises the global end implementation trick for rapid leaf extensions, which stores a universal_end_index\
        # such that updates for many edges can happen in one go. this is stored as a 1-index based array so that updates can occur in constant time 
        # through index operations 
        self.end_index = universal_end_index
        
        self.parent_node = parent_node # the parent node of this edge 
        self.child_node = child_node # the child node this edge connects to 

def extract_edge_length(edge: Edge) -> int:
    """
    Function Description: This function is returns the length of the characters represented in a given string based on 1-based indexing 

    Approach Description: The length of two edges are taken by subtracting the start and end indexes and +1 to account for 1-based indexing 
    and inclusivity of the end index 

    Input: edge, an Edge object 

    Output: int, an integer denoting the length of a given edge 

    Time Complexity Analysis: O(1) as this is a constant time operation 

    Space Complexity Analysis: O(1) as there are no additional data structures used in this function 
    """
    # as all end_indexes for edges are universal the length is stored in a 1 index array [] so access this in constant time and calculate the new length 
    edge_length = edge.end_index[0] - edge.start_index + 1
    return edge_length 

def label_edge(text: str, edge: Edge) -> str:
    """
    Function Description: This function returns the substring for a given edge using list slicing 

    Approach Description: In order to capture the substring of the text in a given edge in the Suffix Tree, simply slice the text to extract its 
    corresponding substring using the start and end indexes of the edge 

    Input:
        - str, the input text 
        - edge, an Edge object 
    
    Output: edge_label, the substring represented by the specific edge 

    Time Complexity Analysis: O(k) where k is the length of the substring to be represented by the edge due to the need of slicing operations

    Space Complexity Analysis: O(1) as the substring is not stored as a seperate string but rather a reference to the original text
    """
    # as all end_indexes for edges are universal the length is stored in a 1 index array [] so access this in constant time and extract the label
    edge_label = text[edge.start_index : edge.end_index[0] + 1] # the +1 ensures the end index is included 
    return edge_label 

def extract_outgoing_edge_from_node(current_character: str, node: Node) -> Edge:
    """
    Function Description: This function returns the outgoing edge of a corresponding Node using the current_character being analysed to check if an Edge exists 
    in children array using this current_character's ASCII value 

    Approach Description: Since each node stores outgoing edges in a fixed-size ASCII array, the ASCII value of the given character is used as the index into this 
    array

    Input:
        - current_character, the current character being inserted into the Suffix Tree
        - node, a Node object representing the current node being analysed 
    
    Output: edge_object, an Edge object denoting the outgoing edge for that given character in the Suffix Tree (if it exists, otherwise returning None)

    Time Complexity Analysis: O(1) as indexing is achieved in constant time 

    Space Complexity Analysis: O(1) as there are no additional data structures used in this function 
    """
    edge_object = node.children[ord(current_character)]
    return edge_object

def set_outgoing_edge_from_node(current_character: str, node: Node, edge: Edge) -> None:
    """
    Function Description: This function sets an outgoing edge in a Node's children array 

    Approach Description: The Edge is stored at the ASCII index and is thus processed in the same way within a given Node 

    Input:
        - current_character, the current character being inserted into the Suffix Tree
        - node, a Node object representing the current node being analysed 
        - edge, a Edge object being stored in a Node 
    
    Output: None, rather updates are made to a Node object 

    Time Complexity Analysis: O(1) as indexing is achieved in constant time 

    Space Complexity Analysis: O(1) as there are no additional data structures used in this function 
    """
    node.children[ord(current_character)] = edge 

def add_new_node(node_number: int, parent_node = None, root_node_boolean = False) -> Node:
    """
    Function Description: This function creates and initialises a new Node object

    Approach Description: This helper function is used so that node creation is kept consistent throughout the suffix tree
    construction process

    Input:
        - node_number, the unique number assigned to the node for debugging
        - parent_node, the parent node of the created node
        - root_node_boolean, a boolean used to indicate whether the created node is the root node

    Output: Node, the newly created Node object

    Time Complexity Analysis: O(1), because the children array has fixed size |alphabet| (ie. 256)

    Space Complexity Analysis: O(1) as there are no additional data structures used in this function 
    """
    new_node = Node() # create a new Node object 
    
    # these parameters are passed in manually so the Node object accepts these values as passed through during the function call
    new_node.node_number = node_number
    new_node.parent = parent_node
    new_node.root_node_boolean = root_node_boolean
    
    return new_node 

def add_new_edge(start_index: int, end_index: int, parent_node: Node, child_node: Node) -> Edge:
    """
    Function Description: This function creates and initialises a new Edge object

    Approach Description: This helper function is used so that edge creation is kept consistent throughout the Suffix Tree
    construction process

    Input:
        - start_index, the start index of the edge label
        - end_index, the end index of the edge label
        - parent_node, the Node object this edge starts from
        - child_node, the Node object this edge points to

    Output: Edge, the newly created Edge object

    Time Complexity Analysis: O(1), because only a fixed number of references and integer values are assigned

    Space Complexity Analysis: O(1) as there are no additional data structures used in this function 
    """
    # create a new Edge object, ensuring to link the child node to the parent node due to this edge being created to connect the two
    new_edge = Edge(start_index, end_index, parent_node, child_node)
    child_node.parent = parent_node

    return new_edge

# UKKONNEN EXTENSION RULES #

# after the rapid leaf extension implementation trick, rule 1 becomes redundant as all edges pointing to leaf nodes share a universal_end_index reference
# (global end in the lectures), so updating universal_end_index[0] which is a 1-sized array updates all edges at once  
def rule_1_suffix_extension(leaf_edge: Edge, current_phase_index: int) -> None:
    """
    Function Description: This function applies the Rule 1 suffix extension by extending an existing leaf edge 

    Approach Description: This helper function si applied for the Rule 1 suffix extension rule, which occurs when a lead node already exists on a path, and thus
    no new node needs to be created. As such, the edge leading into this specific leaf node is updated to reflect that leaf node's edge being updated to include
    the new character being inserted into the Suffix Tree

    Input:
        - leaf_edge, the existing Edge object that points to a specific leaf node in the Suffix Tree
        - current_phase_index, the current phase being used to insert the character into the Suffix Tree

    Output: None, as the leaf edge is extended implicitly through universal_end_index

    Time Complexity Analysis: O(1), because the corresponding leaf node's edge end_index is updated to denote a new character being inserted into the Suffix Tree

    Space Complexity Analysis: O(1), as there are no additional data structures used in this function 
    """
    return

# rule 2 functions now support rapid leaf extension by updating the universal_end_index, while fixed internal edges still use their own 1-sized array
def rule_2_regular_suffix_extension(text: str, current_node: Node, current_edge: Edge, edge_index: int, current_index: int, current_phase_index: int, suffix_start_index: int, next_node_number: int, universal_end_index: list, runlog: list[str]) -> (int, Node):
    """
    Function Description: This function applies the Rule 2 regular suffix extension by splitting an existing edge, creating a new internal node and hanging a 
    new leaf node from that internal node

    Approach Description: This helper function is applied for the Rule 2 regular suffix extension rule, which occurs when the path str[j ... i] in implicitSTi does 
    not end at a leaf, but rather ends in the middle of an existing edge. As such, the next character on the existing edge doesn't match the character for the current
    suffix extension. Thus, the existing edge needs to be split based on a common prefix and mismatch point 

    Because rapid leaf extension is used, leaf edges store their end index as the shared universal_end_index reference. This allows all leaf edges to grow
    automatically when universal_end_index[0] is updated at the start of each phase.

    Input:
        - text, the original input string
        - current_node, the Node object where the edge being split begins 
        - current_edge, the Edge object being split
        - edge_index, the index in the text at which the mismatch point occurs 
        - current_index, the current index in the text where the mismatch has occurred during the suffix extension 
        - current_phase_index, the current phase index during which the current character is being inserted
        - suffix_start_index, the starting index of the suffix being inserted into the Suffix Tree
        - next_node_number, the next available node number to be used for the new leaf node (and for debugging)
        - universal_end_index, a shared one sized array used to store the end index for newly created leaf edges so they can grow automatically in later phases
        - runlog, a list of strings used to store the formatted construction runlog lines for Ukkonnen runtime 

    Output: 
        - int, an integer denoting the next available node number 
        - new_internal_node, a Node object representing the new leaf node created to accomodate the suffix extension based on Rule 2 Regular

    Time Complexity Analysis: O(1), because this function creates a fixed number of nodes and edges, and performs a fixed number of array indexing operations which is
    achieved in constant time

    Space Complexity Analysis: O(1), as there are no additional data structures used in this function 
    """
    # referencing variables: #
    # store the old child node references using the inputs passed into the function before modifications are made 
    old_child_node = current_edge.child_node

    # save the original end index and its current integer value before splitting due to edge cases. if the current edge  connects a leaf node, it's old_edge_index can 
    # be referencing a universal_end_index, as such the old remainder edge must keep this reference too to ensure growth in later phases 
    old_edge_end_index_referencer = current_edge.end_index
    old_edge_end_index = current_edge.end_index[0]

    # 1. create a new internal node which represents the split point #
    new_internal_node = add_new_node(next_node_number, current_node, False)
    next_node_number += 1

    # shorten the existing edge so that it only represents the matched portion (aka. common prefix) this edge now points to the new internal node instead of the previous child node
    current_edge.end_index = [edge_index - 1]
    current_edge.child_node = new_internal_node
    new_internal_node.parent = current_node

    # 2. create a mew edge for old remainder of the original edge #
    # storing the old_edge_end_index_referencer instead of the specific integer value because of the case that if this 
    # original edge was connecting a leaf node its remainder must keep storing universal_end_index
    old_common_prefix_edge = add_new_edge(edge_index, old_edge_end_index_referencer, new_internal_node, old_child_node)

    # store the old remainder edge under the new internal node using the first character of the old remainder
    set_outgoing_edge_from_node(text[edge_index], new_internal_node, old_common_prefix_edge)

    # 3. create a new leaf node to denote the new suffix being inserted
    new_leaf_node = add_new_node(next_node_number, new_internal_node, False)
    new_leaf_node.captured_suffix_index = suffix_start_index
    next_node_number += 1

    # create the new leaf edge for the new mismatching branch of the suffix being inserted using universal_end_index to share a shared end point so future updates can extend this edge 
    # implicitly in one-go 
    new_leaf_edge = add_new_edge(current_index, universal_end_index, new_internal_node, new_leaf_node)

    # store the new leaf edge under the new internal node using the first character of the new branch
    set_outgoing_edge_from_node(text[current_index], new_internal_node, new_leaf_edge)

    # runlog #
    add_runlog_line(runlog, "        Node " + str(new_internal_node.node_number) + " created: Internal node!")
    add_runlog_line(runlog, "        Node " + str(new_leaf_node.node_number) + " created: Leaf node!")

    return next_node_number, new_internal_node

# rule 2 functions now support rapid leaf extension by updating the universal_end_index, while fixed internal edges still use their own 1-sized array
def rule_2_alternate_suffix_extension(text: str, current_node: Node, edge_start_index: int, current_phase_index: int, suffix_start_index: int, next_node_number: int, universal_end_index: list, runlog: list[str]) -> int:
    """
    Function Description: This function applies the Rule 2 alternate suffix extension by creating a new leaf edge from an existing internal node 

    Approach Description: This helper function is applied for the Rule 2 regular suffix extension rule, which occurs when the path str[j ... i] in implicitSTi does not end
    at a leaf, and the next required character is separated from the existing path by an already existing internal node. As such, no new internal node needs to be created
    and instead a new leaf node is created and attached to the existing internal node 

    Because rapid leaf extension is used, the new leaf edge stores its end index as the shared universal_end_index reference. This allows the leaf edge to grow 
    automatically when universal_end_index[0] is updated at the start of each phase later

    Input:
        - text, the original input string
        - current_node, the Node object where the edge being split begins 
        - edge_start_index, the starting index of the new edge label
        - current_phase_index, the current phase index during which the current character is being inserted
        - suffix_start_index, the starting index of the suffix being inserted into the Suffix Tree
        - next_node_number, the next available node number to be used for the new leaf node (and for debugging)
        - universal_end_index, a shared one sized array used to store the end index for newly created leaf edges so they can grow automatically in later phases
        - runlog, a list of strings used to store the formatted construction runlog lines for Ukkonnen runtime 

    Output: int, an integer denoting the next available node number 

    Time Complexity Analysis: O(1), because this function creates a fixed number of nodes and edges, and performs a one array indexing operation which is
    achieved in constant time

    Space Complexity Analysis: O(1), as there are no additional data structures used in this function 
    """
    # 1. create a new leaf node to denote the new suffix being inserted 
    new_leaf_node = add_new_node(next_node_number, current_node, False)
    new_leaf_node.captured_suffix_index = suffix_start_index
    next_node_number += 1

    # 2. create a new leaf edge from the current node to the new leaf node # 
    # use universal_end_index to create a shared end point so future updates can extend this edge implicitly in one-go 
    leaf_edge = add_new_edge(edge_start_index, universal_end_index, current_node, new_leaf_node)

    # store this new connecting leaf edge in the current_node's children array 
    set_outgoing_edge_from_node(text[edge_start_index], current_node, leaf_edge)

    # runlog # 
    add_runlog_line(runlog, "        Node " + str(new_leaf_node.node_number) + " created: Leaf node!")

    return next_node_number

def rule_3_suffix_extension() -> None:
    """
    Function Description: This function applies Rule 3 suffix extentsion rule by continuing the iteration 

    Approach Description: This helper function is applied for the Rule 3 regular suffix extension rule, which occurs when when the current_character already exists in the 
    Suffix Tree, in which no structural changes are needed further 

    Input: None, as this function print's a statement 

    Output: None, instead a print statement is outputted

    Time Complexity Analysis: O(1), as the print statement executes in constant time 

    Space Complexity Analysis: O(1), as there are no additional data structures used in this function 
    """
    return

# HELPER FUNCTIONS FOR IMPLEMENTATION TRICKS # 

def skip_count_implementation_checker(current_edge: Edge, remaining_suffix_to_insert: int) -> bool:
    """
    Function Description: This function determines whether the traversal over a specific path meets the conditions of the skip count implementation trick described in the 
    FIT3155 lecture content 

    Approach Description: This helper function is applied for the Implementation Trick 2: Skip Count Traversal, in which edge lengths less than the remaining suffix needed
    to be inserted can be skipped to avoid character by character traversal along an edge. If the remaining suffix length is greater than or equal to the current edge length
    then traversal may be able to skip to the edge's child  

    Input: 
        - current_edge, the Edge object currently being traversed
        - remaining_suffix_to_insert, the number of characters left in the current suffix extension

    Output: bool, a boolean denoting whether this current_edge can be skipped as the remaining suffix can consume/skip this entire edge 

    Time Complexity Analysis: O(1), as this function merely compares two integer values 

    Space Complexity Analysis: O(1), as there are no additional data structures used in this function 
    """
    skip_count_boolean = remaining_suffix_to_insert > extract_edge_length(current_edge)
    return skip_count_boolean

# UKKONNENS ALGORITHM # 

def UkkonensAlgorithm(text: str, runlog: list[str]) -> Node:
    """
    Function Description: Constructs and returns a suffix tree for a given input text using Ukkonne's algorithm based on the FIT3155 lecture content, and simultaneously 
    recording a runlog file for the construction

    Approach Description: The algorithm builds a suffix tree incrementally, one phase at a time. In phase i, the tree is extended to include the next character within the 
    input text. Each phase processes the required suffix extensions and applies one of Ukkonnen's suffix extension rules: 
        - Rule 1 is handled implicitly through rapid leaf extension, as all leaf edges share the same universal_end_index reference
        - Rule 2 alternate creates a new leaf edge from an existing node when no matching outgoing edge exists
        - Rule 2 regular splits an existing edge, creates a new internal node, and creates a new leaf edge when a mismatch occurs inside an edge
        - Rule 3 detects that the current suffix already exists in the tree and triggers the phase showstopper optimisation

    To improve efficiency, the implementation uses indexed edge labels instead of storing substrings directly, a fixed-size alphabet array for outgoing edges, skip/count traversal, 
    suffix links between internal nodes, active node tracking, and remainder reuse. During construction, important events such as phase starts, extension rules, active node state, 
    remainder ranges, node creation, and resolved suffix links are appended to the runlog list

    Input:
        - text, the input string used to construct the suffix tree
        - runlog, a list of strings used to store the formatted construction runlog lines for Ukkonnen runtime 

    Output:
        - Node, the root node which contains the fully constructed suffix tree

    Time Complexity Analysis: O(n), where n is the length of the input text due to the presence of implementation tricks which optimises the construction of the algorithm to achieve 
    linear constraints through rapid leaf extension, skip/count traversal, suffix links, active node tracking and the phase showstopper rule

    Space Complexity Analysis: O(n), as the suffix tree stores a linear number of nodes and edges which is denoted by the text and bounded by the |alphabet| (ie. 256)
    """
    text_length = len(text)

    # prepare for the construction of the ImplicitST by initialising the root node #
    root_node = add_new_node(1, None, True)
    root_node.suffix_link = root_node # based on the lectures the root node's suffix link always points to itself
    
    add_runlog_line(runlog, "Root Node 1")
    add_runlog_line(runlog, "")

    # nodes after the root start from the number 2
    next_node_number = 2

    # prepare suffix link logic by initialising active nodes and remainder start/end indexes #
    active_node = root_node # active node = represents the node where the next explicit extension should begin, by default it starts at the root and will later be updated using suffix links
    remainder_start_index = None
    remainder_end_index = None

    # prepare for implementation tricks to increase the efficiency of the algorithm #
    universal_end_index = [-1] # keep track of leaf edges together in a 1-sized array so they can all be updated in one-go
    last_j = 0 # to stop repeated Rule 1 extensions by keeping track of the last suffix extension that creates a leaf edge
    
    # THIS IS BASED ON THE PSEUDOCODE PROVIDED IN THE FIT3155 LECTURE CONTENT #
    # For i from 0 to n − 1
    for i in range(0, text_length):
        # Begin PHASE i + 1 - this phase is responsible for extending the current implicit suffix tree using the next character in the text
        last_created_node = None # aid suffix links by keeping track of the last created node, when another internal node is created or an extension reaches an existing internal node this can be changed
        
        # prepare for the implementation trick: phase showstopper by setting a boolean 
        phase_showstopper_implementation_boolean = False

        # at the start of each phase update universal_end_index[0], because all leaf edges share this reference, this helps extends every leaf edge by one character in one-go
        universal_end_index[0] = i

        # runlog # 
        add_runlog_line(runlog, "Phase " + str(i + 1) + " starts from Extn " + str(last_j + 1))

        # start extensions from index 1 to i + 1( in 0-based this is i + 2) and continue processing extensions that are not already handled by rapid leaf extension cases
        # start from last_j + 1 because earlier extensions already end at leaf edges and are handled implicitly through the update of universal_end_index[0]
        for j in range(last_j + 1, i + 2):

            # based on the implementation trick of Phase Showstopper, if extensions in this phase encounter rule 3 the algorithm can move directly to the next phase
            if phase_showstopper_implementation_boolean:
                break

            # Begin SUFFIX EXTENSION j to now consider suffix extension rules
            suffix_start_index = j - 1 # converts this to 0-based indexing 

            # RESOLVE SUFFIX LINKS #
            # if rule 2 regular in the previous extension created an internal node, the active_node stores this and thus its suffix link can be followed in the next 
            # extension such that the remainder can be reused, this condition exists when the remainder start end end indexes aren't None
            if remainder_start_index is not None and remainder_end_index is not None:
                current_node = active_node.suffix_link

                # if no suffix link exists traversal starts from the root node as normal
                if current_node is None:
                    current_node = root_node 

                # move to the extension's remainder by dropping a character since extension j + 1 starts one character after extension j 
                remainder_start_index = remainder_start_index + 1

                # if a remainder substring is still to be inserted, traversal starts from that given remainder
                if remainder_start_index <= remainder_end_index:
                    current_index = remainder_start_index
                
                # if no remainder exists traversal starts from the root node and the active node behaviour is reset
                else:
                    current_node = root_node
                    current_index = suffix_start_index
                    remainder_start_index = None
                    remainder_end_index = None 
            
            # start this extension from the current active node qw rule 2 regular hasn't been encountered in this phase 
            else:
                current_node = root_node # initially the root node but updates iteratively
                current_index = suffix_start_index # represents how far traversal has progressed as edges are analysed 

            # traverse the suffix tree to find the end of the path denoted by txt[j ... i]
            while current_index <= i:
                # check whether the current node has an outgoing edge to start the suffix extension rules
                current_character = text[current_index]
                existing_outgoing_edge = extract_outgoing_edge_from_node(current_character, current_node) 

                # Rule 2 alternate: If no outgoing edge exists from the current node for the inserted character, then the path needs to be separated from an existing path from this 
                # current node
                if existing_outgoing_edge is None:
                    add_runlog_line(runlog, "    Extn " + str(j) + " applies Rule 2 (alternate)")
                    add_runlog_line(runlog, "    Active Node = Node " + str(current_node.node_number) + " (suffix link to Node " + str(current_node.suffix_link.node_number) + "); Remainder = EMPTY")
                    
                    # pass the current universal_end_index so the new leaf edge created can share a global end and implicitly grow in one go in later phases 
                    next_node_number = rule_2_alternate_suffix_extension(text, current_node, current_index, i, suffix_start_index, next_node_number, universal_end_index, runlog)

                    # if a previous rule 2 regular has been applied an internal node has already been created
                    # since rule 2 alternate applies for the current node, it needs to be updated so that it becomes the new suffix link to the previously created internal node 
                    if last_created_node is not None:
                        last_created_node.suffix_link = current_node
                        add_runlog_line(runlog, "        Linking Node " + str(last_created_node.node_number) + " to Node " + str(current_node.node_number))

                        # as this suffix link has since been resolved, the next extension can start from this current node instead of restarting from the root 
                        # and clear the last_created_node reference to avoid linking the same internal node again 
                        active_node = current_node
                        last_created_node = None 
                    
                    # Rule 2 creates a leaf edge so this extension can be skipped in later phases as universal_end_index will be extended in one-go
                    last_j = j

                    # rule 2 alternate finishes this extension from an existing node, so there is no remainder to reuse
                    remainder_start_index = None
                    remainder_end_index = None
                    active_node = root_node
                    break

                # MOVE ON
                # an outgoing edge exists, so the current suffix needs to be compared against the characters in that edge 
                current_edge = existing_outgoing_edge
                edge_index = current_edge.start_index

                # this is the point where the skip count implementation trick becomes useful so we can skip already matched occurrences
                # the remaining_suffix_to_insert stores the number of characters still left to match in the current suffix extension
                # essentially if remaining_suffix_to_insert is long enough to consume the whole edge, we can skip this entire edge  
                current_edge_length = extract_edge_length(current_edge)
                remaining_suffix_to_insert = i - current_index + 1 # current_index to i denotes how many characters are left, +1 is used for inclusivity 
                skip_count_checked_edge = skip_count_implementation_checker(current_edge, remaining_suffix_to_insert)

                # if the boolean to indicate a skip count is True go to the next child node and continue to the next extension
                if skip_count_checked_edge and current_edge.child_node.captured_suffix_index is None:
                    current_index += current_edge_length
                    current_node = current_edge.child_node
                    continue

                # Walk along the edge while:
                #   - there are still characters left on the edge, and
                #   - there are still characters left in the current suffix extension
                #   - OR until a mismatch is found along this path
                while edge_index <= current_edge.end_index[0] and current_index <= i:
                    if text[edge_index] != text[current_index]:  # check for mismatch, if it is found break out of this loop early
                        break
                    
                    edge_index += 1
                    current_index += 1

                # Exat boundary edge case: occurs when traversal for the suffix ends exactly at the end of current_edge (ie. current_edge.child_node), rather than ending in 
                # the middle of an edge this therefore applies for Rule 1 or Rule 3 which needs to be checked on varying constraints
                if edge_index > current_edge.end_index[0] and current_index > i:
                    # if the reached child node is a leaf, then the suffix path ends at a leaf
                    if current_edge.child_node.captured_suffix_index is not None:
                        rule_1_suffix_extension(current_edge, i)
                        # Rule 1 has already been handled by universal_end_index[0] = i so this suffix extension can now be skipped in later phases
                        last_j = j
                        active_node = root_node

                    else:
                        add_runlog_line(runlog, "    Extn " + str(j) + " applies Rule 3")
                        
                        # for rule 3 the current suffix already exists in the tree, hence the remainder is the part of the suffix before the current phase character
                        # but if the suffix only contains the current phase character, then there is no earlier part to store, so the remainder is EMPTY.
                        if suffix_start_index <= i - 1:
                            remainder_start_index = suffix_start_index
                            remainder_end_index = i - 1
                            add_runlog_line(runlog, "    Active Node = Node " + str(current_node.node_number) + " (suffix link to Node " + str(current_node.suffix_link.node_number) + "); Remainder = S[" + str(remainder_start_index + 1) + "..." + str(remainder_end_index + 1)+ "]")
                        else:
                            remainder_start_index = None
                            remainder_end_index = None
                            add_runlog_line(runlog, "    Active Node = Node " + str(current_node.node_number) + " (suffix link to Node " + str(current_node.suffix_link.node_number) + "); Remainder = EMPTY")
                        
                        rule_3_suffix_extension()

                        # if a previous rule 2 regular has been applied an internal node has already been created
                        # since rule 2 alternate applies for the current node, it needs to be updated so that it becomes the new suffix link to the previously created internal node 
                        if last_created_node is not None:
                            last_created_node.suffix_link = current_node
                            add_runlog_line(runlog, "        Linking Node " + str(last_created_node.node_number) + " to Node " + str(current_node.node_number))

                            # as this suffix link has since been resolved, the next extension can start from this current node instead of restarting from the root 
                            # and clear the last_created_node reference to avoid linking the same internal node again 
                            active_node = current_node
                            last_created_node = None 

                        phase_showstopper_implementation_boolean = True # once a rule 3 is encountered we can skip to the next extension straight away

                        # as rule 3 ends the current phase don't carry this remainder into another extension
                        remainder_start_index = None
                        remainder_end_index = None
                        active_node = root_node
                    break


                # Rule 2 regular: If both edge_index and current_index are still captured in the range, and the loop has stopped due to a mismatch inside the current edge, split the current edge 
                # and create a new internal node AND a new leaf node
                if edge_index <= current_edge.end_index[0] and current_index <= i:
                    add_runlog_line(runlog, "    Extn " + str(j) + " applies Rule 2 (regular)")

                    # keep track of the remainder of the text to indicate parts of the suffix extension which are yet to be added into the suffix tree 
                    # the remainder is later used with the active_node and suffix links so the next extension doesn't need to restart from the root
                    remainder_start_index = suffix_start_index
                    remainder_end_index = current_index - 1

                    add_runlog_line(runlog, "    Active Node = Node " + str(current_node.node_number) + " (suffix link to Node " + str(current_node.suffix_link.node_number) + "); Remainder = S[" + str(remainder_start_index + 1) + "..." + str(remainder_end_index + 1) + "]")
                    
                    # pass the current universal_end_index so the new leaf edge created can share a global end and implicitly grow in one go in later phases 
                    next_node_number, new_internal_node = rule_2_regular_suffix_extension(text, current_node, current_edge, edge_index, current_index, i, suffix_start_index, next_node_number, universal_end_index, runlog)
                    
                    # by default the new internal node will point to the root node since that's where all suffix extensions start from 
                    new_internal_node.suffix_link = root_node

                    # if a previous rule 2 regular has been applied an internal node has already been created
                    # since rule 2 alternate applies for the current node, it needs to be updated so that it becomes the new suffix link to the previously created internal node 
                    if last_created_node is not None:
                        last_created_node.suffix_link = current_node
                        add_runlog_line(runlog, "        Linking Node " + str(last_created_node.node_number) + " to Node " + str(current_node.node_number))

                    # note down this this new internal node as the most recently created internal node, so its suffix link can be processed in the next extension 
                    last_created_node = new_internal_node

                    # store the node from whcih the split started as the new active node so that in the next extension it will follow this node's
                    # suffix link and reuse the remainder stored 
                    active_node = current_node

                    # Rule 2 creates a leaf edge so this extension can be skipped in later phases as universal_end_index will be extended in one-go
                    last_j = j
                    break

                # Rule 1: If the full edge was matched and it leads to a leaf, then Rule 1 applies. The suffix path already ends at a leaf so extend the existing leaf edge
                # to include the current character being inserted into the suffix tree
                #
                # the condition edge_index > current_edge.end_index confirms that traversal reached the end of the edge, rather than stopping midway through it (which would apply for Rule 3)
                if current_edge.child_node.captured_suffix_index is not None and edge_index > current_edge.end_index[0]:
                    rule_1_suffix_extension(current_edge, i)
                    
                    # Rule 1 has already been handled by universal_end_index[0] = i so this suffix extension can now be skipped in later phases
                    last_j = j
                    active_node = root_node
                    break

                # Rule 3: Path str[j..i + 1] already exists, so do nothing
                # if current_index has moved past i then the full path str[j ... i] has been matched in the suffix tree and has thus reached txt[i + 1] before reaching the end of the edge,
                # and thus no further structural changes are needed
                if current_index > i and edge_index <= current_edge.end_index[0]:   
                    add_runlog_line(runlog, "    Extn " + str(j) + " applies Rule 3")

                    # for rule 3 the current suffix already exists in the tree, hence the remainder is the part of the suffix before the current phase character
                    # but if the suffix only contains the current phase character, then there is no earlier part to store, so the remainder is EMPTY.
                    if suffix_start_index <= i - 1:
                        remainder_start_index = suffix_start_index
                        remainder_end_index = i - 1
                        add_runlog_line(runlog, "    Active Node = Node " + str(current_node.node_number) + " (suffix link to Node " + str(current_node.suffix_link.node_number) + "); Remainder = S[" + str(remainder_start_index + 1) + "..." + str(remainder_end_index + 1)+ "]")
                    else:
                        remainder_start_index = None
                        remainder_end_index = None
                        add_runlog_line(runlog, "    Active Node = Node " + str(current_node.node_number) + " (suffix link to Node " + str(current_node.suffix_link.node_number) + "); Remainder = EMPTY")
                    
                    rule_3_suffix_extension()

                    # if a previous rule 2 regular has been applied an internal node has already been created
                    # since rule 2 alternate applies for the current node, it needs to be updated so that it becomes the new suffix link to the previously created internal node 
                    if last_created_node is not None:
                        last_created_node.suffix_link = current_node
                        add_runlog_line(runlog, "        Linking Node " + str(last_created_node.node_number) + " to Node " + str(current_node.node_number))

                        # as this suffix link has since been resolved, the next extension can start from this current node instead of restarting from the root 
                        # and clear the last_created_node reference to avoid linking the same internal node again 
                        active_node = current_node
                        last_created_node = None 

                    phase_showstopper_implementation_boolean = True # once a rule 3 is encountered we can skip to the next extension straight away

                    # as rule 3 ends the current phase don't carry this remainder into another extension
                    remainder_start_index = None
                    remainder_end_index = None
                    active_node = root_node
                    break

                # if the full edge has been matched, but the suffix is still to be captured move down to the child node of the current node and restart the matching process 
                current_node = current_edge.child_node
        # End PHASE i + 1
        # Add a blank line between phases, but NOT for the final phase
        if i != text_length - 1:
            add_runlog_line(runlog, "")

    return root_node # the root node at this point now has references of Node and Edge objects which constructs a Suffix Tree

# LCP ARRAY #
# Each root-to-leaf path in the suffix tree represents one suffix of the input text. Therefore, every leaf node corresponds to exactly one suffix and the starting index of the suffix
# is stored in the Node object's captured_suffix_index attribute. Recording each leaf node's captured_suffix_index during this DFS therefore produces the suffix array
# 
# The suffix array returned is also in correct order due to the presence of the fixed size alphabet array which enables the DFS traversal to essentially occur in lexographical order.
# Using this fact the LCP value can be calculated based on this presumption: for 2 given leaf nodes their shared path from the root node is trivially equal to their lowest common prefix.
# Thus, the point where their paths split is their LCP
#
# During DFS, when traversal moves from one child subtree to a sibling child subtree, the corresponding parent node becomes the node holding the LCP value between the previous suffix leaf 
# and the suffix leaf in the next child sibling node. Therefore, the current_string_length at that parent node becomes the LCP value to assign to the next encountered sibling node
def DFS_suffix_tree_to_construct_suffix_and_LCP_array(input_node: Node, suffix_array: list, LCP_array: list, current_string_length: int, LCP_value_to_add: int) -> None:
    """
    Function Description: This function performs a DFS traversal of a provided suffix tree to construct a suffix and LCP array 

    Approach Description: Each leaf node in the suffix tree represents one suffix of the provided input text. The LCP array uses this fact and the traversal of DFS to be extracted correctly.
    Based on the structure of the suffix tree, two nodes suffixes will split at an internal node when their suffixes differ. Hence, the LCP between these two adjacent suffixes in the suffix 
    array is denoted by their shared path from the root to their lowest common parent node. This means their LCP is equal to the length of the string depth of the common parent node 

    Using the current_string_length, it stores the string depth of the current node. When DFS moves down an edge, this value is increased by the length of that edge. Additionally, the 
    LCP_value_to_add parameter stores the LCP value that should be added when the next leaf node is reached. If DFS enters the first child subtree of a node, it's LCP is preserved as it's technically
    still being compared to the previous suffix route. However, as soon as its adjacent siblings are traversed, their lowest common parent node contains the LCP value. 

    Input:
        - input_node, the current Node object being visited during DFS (starting from the root_node)
        - suffix_array, the array used to store suffix starting indexes in lexicographic order
        - LCP_array, the array used to store LCP values corresponding to the suffix array
        - current_string_length, an integer denoting the length of characters on the path from the root node to the current node
        - LCP_value_to_add, the LCP value to append when the next suffix leaf is reached

    Output: None, as suffix_array and LCP_array are updated recursively

    Time Complexity Analysis: O(V + E), where V is the number of nodes in the suffix tree and E is the number of edges. This is because DFS visits each node and each edge once during traversal

    Space Complexity Analysis: O(n), where n is the length of the input text. This is due to the recursive DFS call stackz
    """
    # base case: if this node is a leaf node, record the index it captures in the text 
    if input_node.captured_suffix_index is not None:
        suffix_array.append(input_node.captured_suffix_index)

        # if the first suffix in the suffix array is the terminal character, trivially LCP[0] = 0
        if len(suffix_array) == 1:
            LCP_array.append(0)

        # otherwise add the corresponding value found during traversal 
        else:
            LCP_array.append(LCP_value_to_add)

        return
    
    # tracks whether DFS has already visited one child subtree from this node
    first_child_visited_boolean = False

    # recursive case: visit each outgoing edge to connecting child nodes and recursively call DFS on these child nodes
    for ascii_value in range(0, 256):
        edge = input_node.children[ascii_value]

        if edge is not None:
            child_depth = current_string_length + extract_edge_length(edge)

            # if this is the first child subtree visited from this node continue the current DFS path AND keep the same LCP value
            if first_child_visited_boolean == False:
                LCP_value_to_add = LCP_value_to_add

            # if this is a later child subtree, DFS has moved from one sibling subtree to another, meaning its LCP is being compared to its sibling 
            # which is denoted by the current_string_length of their corresponding parent node
            else:
                LCP_value_to_add = current_string_length

            first_child_visited_boolean = True

            DFS_suffix_tree_to_construct_suffix_and_LCP_array(edge.child_node, suffix_array, LCP_array, child_depth, LCP_value_to_add)

# REFERENCE: Parts of this code snippet was copied from the "Command-line usage tutorial for Assignments"
# document provided in the assignment specifications 
if __name__ == '__main__':

    #retrieve the file paths from the commandline arguments
    _, text_file = sys.argv

    # read the input string and concatenate the terminal symbol required for suffix tree construction
    text = read_file(text_file) + "$"

    # initialise the runlog, suffix_array and LCP arrays and create the suffix tree using Ukkonnen's
    runlog = []
    suffix_array = []
    LCP_array = []
    root_node = UkkonensAlgorithm(text, runlog)

    DFS_suffix_tree_to_construct_suffix_and_LCP_array(root_node, suffix_array, LCP_array, 0, 0)

    write_output(LCP_array, "output_a2q1.txt")
    write_runlog(runlog, "runlog_a2q1.txt")
