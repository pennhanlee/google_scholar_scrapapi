import numpy as np
import pandas as pd
import networkx as nx
import os
from datetime import datetime
from networkx.algorithms import community
from networkx.algorithms import centrality
from networkx.algorithms import components

from lib.node_serpapi import Node

ALLDATA_FILE = "./data/10-06-2021_1604_Computer Vision/alldata.xlsx"
MAINPUBS_FILE = "./data/10-06-2021_1604_Computer Vision/main_pubs.xlsx"
SAVEPATH = "./data/10-06-2021_1604_Computer Vision/"


def create_nodes(alldata_df, mainpubs_df):
    full_node_dict = {}
    for index, row in mainpubs_df.iterrows():
        citing_pubs_id_list = row["Citing_pubs_id"].split(";")
        for result_id in citing_pubs_id_list:
            node = None
            if result_id not in full_node_dict:
                entry = alldata_df.loc[alldata_df['Result_id'] == result_id]
                entry = entry.iloc[0]
                node = Node(entry["Title"], entry["Year"], entry["Abstract"], entry['Citedby_id'],
                            entry["No_of_citations"], entry["Result_id"])
                full_node_dict[node.result_id] = node
            else:
                node = full_node_dict[result_id]
            for result_id in citing_pubs_id_list:
                if result_id != node.result_id:
                    node.add_edge(result_id)
    return full_node_dict


def create_network_file(node_dict, alldata_df):
    connected_nodes = []
    for node in node_dict.values():
        bib_couple_dict = node.edge_dict
        pub_title = node.title
        for couple in bib_couple_dict.items():
            couple_id = couple[0]
            couple_pub = alldata_df.loc[alldata_df["Result_id"] == couple_id]
            couple_pub_title = couple_pub.iloc[0]["Title"]
            edge_weight = couple[1]
            connected_nodes.append([pub_title, couple_pub_title, edge_weight])
    col = ['Pub_1', 'Pub_2', 'Weight']
    excel_df = pd.DataFrame(data=connected_nodes, columns=col)
    path = SAVEPATH + "network.xlsx"
    excel_df.to_excel(path, index=False)
    return connected_nodes


def create_cluster_indi(components, alldata_df):
    clusters = []
    for x in range(0, len(components)):
        cluster_no = x + 1
        cluster = components[x]
        cluster_df = alldata_df[alldata_df["Title"].isin(cluster)]
        cluster_df.insert(len(cluster_df.columns), "Cluster", cluster_no)
        path = SAVEPATH + "cluster_{}.xlsx".format(str(cluster_no))
        cluster_df.to_excel(path, index=False)
        clusters.append(cluster_df)
    combined_df = pd.concat(clusters)
    combineddata_path = SAVEPATH + "combined_data.xlsx".format(str(cluster_no))
    combined_df.to_excel(combineddata_path, index=False)
    return clusters


def create_cluster_sum(list_of_df):

    return None


def create_graph(node_list):
    graph = nx.Graph()
    for node in node_list:
        graph.add_edge(node[0], node[1], weight=node[2])
    return graph


def create_clusters(graph):
    # components = girvan_with_modularity(graph)
    components = community.greedy_modularity_communities(graph)
    return components

# def girvan_algo(graph):
#     u, v = edge_to_remove(graph)
#     print("Girvan Algo")
#     print(u)
#     print(v)
#     print("**********")
#     graph.remove_edge(u, v)
#     clusters = components.connected_components(graph)
#     print(len(list(clusters)))
#     return graph, clusters

# def edge_to_remove(graph):
#     dict_of_values = centrality.edge_betweenness_centrality(graph)
#     list_of_tuples = list(dict_of_values.items())
#     list_of_tuples.sort(key=lambda x:x[1], reverse= True)
#     print(list_of_tuples[0][1])
#     return list_of_tuples[0][0]

# def girvan_with_modularity(graph):
#     highest_modularity = 0.0
#     current_modularity = 1.0
#     latest_graph = graph
#     clusters = None
#     while (current_modularity >= highest_modularity):
#         latest_graph, clusters = girvan_algo(latest_graph)
#         current_modularity = community.modularity(graph, clusters)
#         if (current_modularity > highest_modularity):
#             highest_modularity = current_modularity
#         print("current_modularity")
#         print(current_modularity)
#         print("**********")

#     print(next(clusters))
#     return clusters


def main():
    # alldata_file = input("Please provide filepath to alldata.xlsx: ")
    # mainpubs_file = input("Please provide filepath to main_pubs.xlsx: ")
    # savepath = input("Please provide the folder path to save the documents: ")
    alldata_file = ALLDATA_FILE
    mainpubs_file = MAINPUBS_FILE
    savepath = SAVEPATH
    alldata_df = pd.read_excel(alldata_file)
    mainpubs_df = pd.read_excel(mainpubs_file)
    node_dict = create_nodes(alldata_df, mainpubs_df)
    connected_nodes_list = create_network_file(node_dict, alldata_df)
    graph = create_graph(connected_nodes_list)
    components = create_clusters(graph)
    list_of_cluster_df = create_cluster_indi(components, alldata_df)
    create_cluster_sum(list_of_cluster_df)
    # create_clustersummary_file(components)
    return None


if __name__ == "__main__":
    main()
