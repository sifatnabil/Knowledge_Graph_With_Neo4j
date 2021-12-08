
import time

from py2neo import Node, Graph, Relationship, NodeMatcher
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import spacy

from helper import *
from definitions import *
from data_cleaning import *
from graph_functions import *
from config import *

# * Dictionary without Noun chunks
non_nc = spacy.load('en_core_web_md')

# * Dictionary with Noun chunks
nlp = spacy.load('en_core_web_md')
nlp.add_pipe('merge_noun_chunks')

with open("corpus.txt", "r", encoding="utf-8") as f:
    corpus = f.read()

start_time = time.time()
initial_tup_ls = create_svo_triples(corpus, non_nc, nlp)
time_taken = calculate_time(start_time)
total_time_taken = time_taken
print("Time took to create initial tuples list: {:.2f} seconds".format(time_taken))

start_time = time.time()
init_obj_tup_ls = get_obj_properties(api_key, initial_tup_ls)
time_taken = calculate_time(start_time)
total_time_taken += time_taken
print("Time took to get object properties: {:.2f} seconds".format(time_taken))

start_time = time.time()
new_layer_ls = add_layer(init_obj_tup_ls, api_key, non_nc, nlp)
time_taken = calculate_time(start_time)
total_time_taken += time_taken
print("Time took to add new layer: {:.2f} seconds".format(time_taken))

start_time = time.time()
starter_edge_ls = init_obj_tup_ls + new_layer_ls
time_taken = calculate_time(start_time)
total_time_taken += time_taken
print("Time took to create starter edge list: {:.2f} seconds".format(time_taken))

start_time = time.time()
edge_ls = subj_equals_obj(starter_edge_ls)
time_taken = calculate_time(start_time)
total_time_taken += time_taken
print("Time took to create edge list: {:.2f} seconds".format(time_taken))

start_time = time.time()
clean_edge_ls = check_for_string_labels(edge_ls)
time_taken = calculate_time(start_time)
total_time_taken += time_taken
print("Time took to create clean edge list: {:.2f} seconds".format(time_taken))

start_time = time.time()
edges_word_vec_ls = create_word_vectors(nlp, edge_ls)
time_taken = calculate_time(start_time)
total_time_taken += time_taken
print("Time took to create edge word vectors: {:.2f} seconds".format(time_taken))

start_time = time.time()
print("Starting Creating Graph")
orig_node_graph_query = query_google(edge_ls[0][0], api_key)
orig_node_desc, orig_node_entity, orig_node_url = orig_node_graph_query[0][0], orig_node_graph_query[1][0], orig_node_graph_query[2][0]

orig_node_tup_ls = [(edge_ls[0][0], orig_node_desc, orig_node_entity, orig_node_url, np.random.uniform(low=-1.0, high=1.0, size=(300,)))]
obj_node_tup_ls = [(tup[2], tup[3], tup[4], tup[5], tup[6]) for tup in edges_word_vec_ls]
full_node_tup_ls = orig_node_tup_ls + obj_node_tup_ls
dedup_node_tup_ls = dedup(full_node_tup_ls)
node_tup_ls = convert_vec_to_ls(dedup_node_tup_ls)
time_taken = calculate_time(start_time)
total_time_taken += time_taken
print("Time took to create node list: {:.2f} seconds".format(time_taken))

start_time = time.time()
# * Initialize Graph
graph = Graph(neo4j_url, name=neo4j_username, password=neo4j_password)
nodes_matcher = NodeMatcher(graph)

# * Add the edges from our list to the graph
add_nodes(graph, node_tup_ls)

# * Add edges to graph
add_edges(graph, nodes_matcher, Node, Relationship, edges_word_vec_ls)
time_taken = calculate_time(start_time)
total_time_taken += time_taken
print("Time took to create and feed graph: {:.2f} seconds".format(time_taken))

print("Total time taken to create graph: {:.2f} seconds".format(total_time_taken))

additional_label_addition_query = """
MATCH (n:Node) 
WHERE size(n.node_labels) > 0
CALL apoc.create.addLabels(n, n.node_labels) 
YIELD node 
RETURN node
"""

query_reply = graph.run(additional_label_addition_query)
print("Successfully added additional labels to nodes")

in_memory_graph_query = """
CALL gds.graph.create(
	'all_nodes',
    {
    	AllNodes: {label: 'Node', 
                   properties: {word_vec_embedding: {property: 'word_vec'}}}
    },
    {
    	AllRels: {type: '*', orientation: 'UNDIRECTED'}
    }
)
YIELD graphName, nodeCount, relationshipCount
"""

query_reply = graph.run(in_memory_graph_query)
print("Created in memory graph named 'all_nodes'")

node2vec_query = """
CALL gds.beta.node2vec.write('all_nodes', 
    { 
        embeddingDimension: 10, 
        writeProperty: 'n2v_all_nodes'
    } 
)
"""

query_reply = graph.run(node2vec_query)
print("Successfully created node2vec embeddings for all nodes, Property name: 'n2v_all_nodes'")