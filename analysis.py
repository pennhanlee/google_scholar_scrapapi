import numpy as np
import pandas as pd
import networkx as nx
import os
from datetime import datetime
from networkx.algorithms import community
from networkx.algorithms import centrality
from networkx.algorithms import components

from lib.node_serpapi import Node
import lib.graphcreator as graphcreator
import lib.metrics as metrics
import lib.textminer as textminer
import lib.textminer_nlp as textminer_nlp

ALLDATA_FILE = "./data/16-06-2021_1444_Natural Language Processing/alldata.xlsx"
MAINPUBS_FILE = "./data/16-06-2021_1444_Natural Language Processing/main_pubs.xlsx"
SAVEPATH = "./data/16-06-2021_1444_Natural Language Processing"
MIN_YEAR = 2010
MAX_YEAR = 2020

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


def create_cluster_indi(components, alldata_df, word_bank, min_year, max_year):
    clusters = {}
    linegraph_data_dict = {}
    no_of_doc = len(alldata_df.index)
    for x in range(0, len(components)):
        print("Starting analysis on Component " + str(x+1) + "/" + str(len(components)))
        cluster_no = x + 1
        cluster = components[x]
        cluster_df = alldata_df[alldata_df["Title"].isin(cluster)]
        cluster_df.insert(len(cluster_df.columns), "Cluster", cluster_no)
        cluster_word_dict, cluster_name, raw_word_list = textminer.mine_cluster(cluster_df, word_bank, no_of_doc, "Title", "Abstract")
        cluster_summary = textminer_nlp.create_extractive_summary(cluster_df, 2)
        print(cluster_name)
        print(cluster_summary)
        if not os.path.exists(SAVEPATH + "/{}".format(cluster_name)):
            os.makedirs(SAVEPATH + "/{}".format(cluster_name))
        data_path = SAVEPATH + "/{}/{}.xlsx".format(cluster_name, cluster_name)
        linegraph_path = SAVEPATH + "/{}/linegraph.png".format(cluster_name)
        wordcloud_path = SAVEPATH + "/{}/wordcloud.png".format(cluster_name)
        # cluster_df.to_excel(data_path, index=False)
        clusters[cluster_name] = cluster_df
        # graphcreator.generate_word_cloud(raw_word_list, wordcloud_path)
        linegraph_data = graphcreator.generate_year_linegraph(cluster_df, linegraph_path, min_year, max_year)
        linegraph_data_dict[cluster_name] = linegraph_data
        print("Completed analysis on Component " + str(x+1) + "/" + str(len(components)) + ": " + cluster_name)
    combined_df = pd.concat(clusters)
    combineddata_path = SAVEPATH + "combined_data.xlsx"
    combined_df.to_excel(combineddata_path, index=False)
    
    return clusters, linegraph_data_dict


def create_cluster_sum(clusters_dict, linegraph_data, min_year, max_year):
    cluster_summary = []
    total_doc = sum([len(cluster.index) for cluster in clusters_dict.values()])
    year_range = max_year - min_year
    for cluster in clusters_dict:
        cluster_name = cluster
        cluster_df = clusters_dict[cluster]
        size = len(cluster_df.index)
        growth = metrics.growth_index(cluster_df, total_doc, max_year, min_year)
        impact = metrics.impact_index(cluster_df)
        cluster_type = metrics.get_cluster_type(cluster_df, year_range)
        current_cluster = [cluster_name, cluster_type, size, growth, impact]   #TBH change to cluster type once year is solved
        cluster_summary.append(current_cluster)

    col=['Name', 'Type', 'Size', 'Growth Index', 'Impact Index']
    cluster_sum_df = pd.DataFrame(cluster_summary, columns=col)
    data_path = SAVEPATH + "/summary.xlsx"
    linegraph_path = SAVEPATH + "/combined_linegraph.png"
    cluster_sum_df.to_excel(data_path, index=False)
    graphcreator.generate_summary_linegraph(linegraph_data, linegraph_path)
    return cluster_sum_df

def create_graph(node_list):
    graph = nx.Graph()
    for node in node_list:
        graph.add_edge(node[0], node[1], weight=node[2])
    return graph

def create_clusters(graph):
    # components = girvan_with_modularity(graph)
    components = community.greedy_modularity_communities(graph)
    return components


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

    network_graph = create_graph(connected_nodes_list)
    components = create_clusters(network_graph)

    word_bank = textminer.mine_word_bank(alldata_df, "Title", "Abstract")
    list_of_cluster_df, linegraph_data = create_cluster_indi(components, alldata_df, word_bank, MIN_YEAR, MAX_YEAR)
    create_cluster_sum(list_of_cluster_df, linegraph_data, MIN_YEAR, MAX_YEAR)
    return None


if __name__ == "__main__":
    main()


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