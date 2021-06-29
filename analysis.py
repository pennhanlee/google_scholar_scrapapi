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
import lib.topic_model as topic_model

ALLDATA_FILE = "./data/16-06-2021_1444_Natural Language Processing/alldata.xlsx"
MAINPUBS_FILE = "./data/16-06-2021_1444_Natural Language Processing/main_pubs.xlsx"
SAVEPATH = "./data/16-06-2021_1444_Natural Language Processing"
MIN_YEAR = 2010
MAX_YEAR = 2020

def create_nodes(alldata_df, mainpubs_df):
    ''' Creates node objects for each entry in the dataframe including
        the bibliographic couples and their weights

        Parameters
        ------------
        alldata_df : pandas DataFrame
                a DataFrame containing all publications extracted
                columns : ['Title', 'Year', 'Abstract', 'Citedby_id', 'No_of_citations', 'Result_id']

        mainpubs_dict : dict
                a dictionary containing root publications extracted. Does
                not contain publications extracted by retrieve_citing_pub(...)

                key, value = Result_id, List of Publication info
                Publication info = ['Title', 'Year', 'Abstract', 'Citedby_id', 'No_of_citations', 'Result_id', 'Type_of_Pub', 'Citing_pubs_id']

        Returns
        -----------
        full_node_dict : dict
                Dictionary of the nodes
                Key, Value: Result_id, Node Object
    '''

    full_node_dict = {}
    for index, row in mainpubs_df.iterrows():
        citing_pubs_id_list = row["Citing_pubs_id"].split(";")
        for result_id in citing_pubs_id_list:
            node = None
            if result_id not in full_node_dict:
                entry = alldata_df.loc[alldata_df['Result_id'] == result_id]
                entry = entry.iloc[0]
                node = Node(entry["Title"], entry["Year"], entry["Abstract"], entry['Citedby_id'],
                            entry["No_of_citations"], entry["Result_id"], entry['Topic Number'], 
                            entry['Topic'], entry['Topic Probability'])
                full_node_dict[node.result_id] = node
            else:
                node = full_node_dict[result_id]
            for result_id in citing_pubs_id_list:
                if result_id != node.result_id:
                    node.add_edge(result_id)
    return full_node_dict


def create_network_file(node_dict, alldata_df):
    ''' Creates a network .xlsx file to be used for visualisation on Cytoscape
        columns: ['Publication_1', 'Publication_2', 'Weight', 'Topic Number', 'Topic']

        Parameters
        ------------
        node_dict : dict
                dictionary of nodes
                key, value: Result_id, Node object
        
        alldata_df : pandas DataFrame
                a DataFrame containing all publications extracted
                columns : ['Title', 'Year', 'Abstract', 'Citedby_id', 'No_of_citations', 'Result_id']

        Returns : 
        connected_nodes : list
                List of lists of node and edge information

        components : list
                List of the clusters in the analysis
    '''

    connected_nodes = []
    node_in_network = set()
    counter = 1;
    for node in node_dict.values():
        print(counter)
        bib_couple_dict = node.edge_dict
        pub_title = node.title
        pub_topic_no = node.topic_no
        pub_topic = node.topic
        node_in_network.add(pub_title)
        added_to_graph = False
        for couple_id, couple_edge_weight in bib_couple_dict.items():
            couple_pub = alldata_df.loc[alldata_df["Result_id"] == couple_id]
            couple_pub_title = couple_pub.iloc[0]["Title"]
            if (couple_pub_title in node_in_network):   #To avoid duplication of edges ( A - B and B - A )
                continue
            else:
                connected_nodes.append([pub_title, couple_pub_title, couple_edge_weight, pub_topic_no, pub_topic])
                added_to_graph = True
        if not added_to_graph:
            connected_nodes.append([pub_title, pub_title, 0, -1, "No Topic Assigned"])  #Putting the node into the network to make sure it is not excluded. 

        counter += 1
    col = ['Publication_1', 'Publication_2', 'Weight', 'Topic Number', 'Topic']
    network_df = pd.DataFrame(data=connected_nodes, columns=col)
    network_graph = _create_graph(connected_nodes) #create graph to apply clustering algo
    components = _create_clusters(network_graph)   # apply clustering algo
    temp_df_list = []
    for x in range(0, len(components)):
        cluster_id = x + 1
        cluster = components[x]
        temp_df = network_df[network_df["Publication_1"].isin(cluster)]  #add cluster number to nodes
        temp_df.insert(len(temp_df.columns), "Cluster", cluster_id)
        temp_df_list.append(temp_df)
    network_df = pd.concat(temp_df_list)
    path = SAVEPATH + "/network.xlsx"
    network_df.to_excel(path, index=False)
    return connected_nodes, components


def create_cluster_indi(components, alldata_df, word_bank, min_year, max_year, lda_model, dictionary):
    ''' Analyses entries of each cluster in the publications DataFrame and groups the entries into
        its individual cluster dataframe. Creates wordcloud and linegraph for each cluster.

        Parameter
        ------------
        components : list
                list of clusters

        alldata_df : pandas DataFrame
                a DataFrame containing all publications extracted
                columns : ['Title', 'Year', 'Abstract', 'Citedby_id', 'No_of_citations', 'Result_id']

        word_bank : dict
                dictionary of words and frequencies.
                key, value: word, frequency

        min_year : int
                the earliest year to limit the period of publication retrieval

        max_year : int
                the latest year to limit the period of publication retrieval

        lda_model : LDA model object
                trained Latent Dirichlet Algorithm

        dictionary : dict
                Dictionary of words and occurrence frequency
                key, value = word, frequency

        Returns
        ----------
        clusters : dict
                Dictionary of cluster name to cluster DataFrame
                key, value : name, cluster dataframe

        linegraph_data_dict : dict
                Dictionary of cluster name to cluster linegraph
                key, value : name, cluster linegraph                 
    '''

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
        word_list = textminer_nlp.get_word_list(cluster_df, "Title", "Abstract")
        # cluster_summary = textminer_nlp.create_extractive_summary(cluster_df, 2)
        # print(cluster_name)
        # print(cluster_summary)
        if not os.path.exists(SAVEPATH + "/{}".format(cluster_name)):
            os.makedirs(SAVEPATH + "/{}".format(cluster_name))
        data_path = SAVEPATH + "/{}/{}.xlsx".format(cluster_name, cluster_name)
        linegraph_path = SAVEPATH + "/{}/linegraph.png".format(cluster_name)
        wordcloud_path = SAVEPATH + "/{}/wordcloud.png".format(cluster_name)
        cluster_df.to_excel(data_path, index=False)
        clusters[cluster_name] = cluster_df
        graphcreator.generate_word_cloud(word_list, wordcloud_path)
        linegraph_data = graphcreator.generate_year_linegraph(cluster_df, linegraph_path, min_year, max_year)
        linegraph_data_dict[cluster_name] = linegraph_data
        print("Completed analysis on Component " + str(x+1) + "/" + str(len(components)) + ": " + cluster_name)
    combined_df = pd.concat(clusters)
    combineddata_path = SAVEPATH + "/combined_data.xlsx"
    combined_df.to_excel(combineddata_path, index=False)
    
    return clusters, linegraph_data_dict

def create_cluster_indi_2(cluster, cluster_no, alldata_df, word_bank, min_year, max_year, lda_model, dictionary):
    ''' Analyses entries of one cluster in the publications DataFrame and groups the entries into
        a dataframe. Creates wordcloud and linegraph for this cluster.
        To be used together with GUI for GUI to track each cluster iteration for UX feature 

        Parameter
        ------------
        cluster : list
                list of entries

        cluster_no : int
                cluster number for this analysis

        alldata_df : pandas DataFrame
                a DataFrame containing all publications extracted
                columns : ['Title', 'Year', 'Abstract', 'Citedby_id', 'No_of_citations', 'Result_id']

        word_bank : dict
                dictionary of words and frequencies.
                key, value: word, frequency

        min_year : int
                the earliest year to limit the period of publication retrieval

        max_year : int
                the latest year to limit the period of publication retrieval

        lda_model : LDA model object
                trained Latent Dirichlet Algorithm

        dictionary : dict
                Dictionary of words and occurrence frequency
                key, value = word, frequency

        Returns
        ----------
        cluster_name : str
                cluster name derived from analysis

        cluster_df : pandas DataFrame
                pandas DataFrame containing entries of the cluster

        linegraph_data : linegraph object
                Linegraph object created from analysis
    '''

    no_of_doc = len(alldata_df.index)
    cluster_df = alldata_df[alldata_df["Title"].isin(cluster)]
    cluster_df.insert(len(cluster_df.columns), "Cluster", cluster_no)
    cluster_word_dict, cluster_name, raw_word_list = textminer.mine_cluster(cluster_df, word_bank, no_of_doc, "Title", "Abstract")
    # cluster_summary = textminer_nlp.create_extractive_summary(cluster_df, 2)
    # print(cluster_name)
    # print(cluster_summary)
    if not os.path.exists(SAVEPATH + "/{}".format(cluster_name)):
        os.makedirs(SAVEPATH + "/{}".format(cluster_name))
    data_path = SAVEPATH + "/{}/{}.xlsx".format(cluster_name, cluster_name)
    linegraph_path = SAVEPATH + "/{}/linegraph.png".format(cluster_name)
    wordcloud_path = SAVEPATH + "/{}/wordcloud.png".format(cluster_name)
    cluster_df.to_excel(data_path, index=False)
    graphcreator.generate_word_cloud(raw_word_list, wordcloud_path)
    linegraph_data = graphcreator.generate_year_linegraph(cluster_df, linegraph_path, min_year, max_year)

    return cluster_name, cluster_df, linegraph_data

def create_cluster_sum(clusters_dict, linegraph_data, min_year, max_year):
    ''' Creates a summary of each cluster that includes cluster metrics
        and saves an .xlsx file of this summary

        Parameters
        ------------
        clusters_dict : dict
                        dictionary of clusters
                        key, value = cluster name, pandas Dataframe of cluster

        linegraph_data : list
                        list of linegraph data of each cluster

        min_year : int
                the earliest year to limit the period of publication retrieval

        max_year : int
                the latest year to limit the period of publication retrieval

        Returns
        ------------
        cluster_sum_df : pandas DataFrame
                pandas DataFrame of the summary of the clusters

    '''
    cluster_summary = []
    total_doc = sum([len(cluster.index) for cluster in clusters_dict.values()])
    for cluster in clusters_dict:
        cluster_name = cluster
        cluster_df = clusters_dict[cluster]
        size = len(cluster_df.index)
        growth = metrics.growth_index(cluster_df, total_doc, min_year, max_year)
        impact = metrics.impact_index(cluster_df)
        cluster_type = metrics.get_cluster_type(cluster_df, min_year, max_year)
        current_cluster = [cluster_name, cluster_type, size, growth, impact]
        cluster_summary.append(current_cluster)

    col=['Name', 'Type', 'Size', 'Growth Index', 'Impact Index']
    cluster_sum_df = pd.DataFrame(cluster_summary, columns=col)
    data_path = SAVEPATH + "/summary.xlsx"
    linegraph_path = SAVEPATH + "/combined_linegraph.png"
    cluster_sum_df.to_excel(data_path, index=False)
    graphcreator.generate_summary_linegraph(linegraph_data, linegraph_path)
    return cluster_sum_df

def tag_pubs_to_topics(cluster_df, lda_model, dictionary):
    ''' Takes a Publications pandas DataFrame and tags each
        row to a specific topic based on the trained LDA Model and dictionary provided
        The title of each publication is used to retrieve the topic

        Parameters
        -------------
        cluster_df : pandas DataFrame
                Publications DataFrame

        lda_model : LDA model object
                trained Latent Dirichlet Algorithm

        dictionary : dict
                Dictionary of words and occurrence frequency
                key, value = word, frequency

        Returns
        ------------
        cluster_df : updated Pandas DataFrame
    '''

    topics = lda_model.print_topics(num_topics=-1, num_words=4)
    topics.sort(key=lambda x:x[0])
    for index, row in cluster_df.iterrows():
        title = row["Title"]
        title = topic_model.prepare_text_for_lda(title)
        title_bow = dictionary.doc2bow(title)
        topic = lda_model.get_document_topics(title_bow)
        if len(topic) > 0:
            topic.sort(key=lambda x:x[1], reverse=True)
            top_topic = topics[topic[0][0]]    #0th index of First Tuple in list [(3, 0.523), ...]
            cluster_df.loc[index, 'Topic Number'] = top_topic[0]
            cluster_df.loc[index, 'Topic'] = top_topic[1]
            cluster_df.loc[index, 'Topic Probability'] = topic[0][1]
        else:
            cluster_df.loc[index, 'Topic Number'] = -1
            cluster_df.loc[index, 'Topic'] = "No Topic Assigned"
            cluster_df.loc[index, 'Topic Probability'] = 0
    
    return cluster_df

def _create_graph(node_list):
    ''' Creates a graph of Publications and Publication Bibliographic Coupling 
        as nodes and edges respectively using networkX graph constructor

        Parameters
        ------------
        node_list : list
                    List of List of publication connections
                    eg. [['Publication_1', 'Publication_2', 'Weight', 'Topic Number', 'Topic']]

        Returns
        -----------
        graph : networkX graph object
                    a graph object of Publication and the corresponding Bibliographic Couples

    '''

    graph = nx.Graph()
    for node in node_list:
        graph.add_edge(node[0], node[1], weight=node[2])
    return graph

def _create_clusters(graph):
    ''' Creates clusters based on the girvan newman clustering algorthim

        Parameters
        -----------
        graph : networkx graph
                a graph of nodes and edges created using the networkx graph constructor

        Returns
        -----------
        components: clusters derived from the algorithm
    '''

    # components = girvan_with_modularity(graph)
    components = community.greedy_modularity_communities(graph)
    return components


def main():
    # alldata_file = input("Please provide filepath to alldata.xlsx: ")
    # mainpubs_file = input("Please provide filepath to main_pubs.xlsx: ")
    # savepath = input("Please provide the folder path to save the documents: ")
    # min_year = input("Please provide the earliest year in the analysis eg: 2010: ")
    # max_year = input("Please provide the latest year in the analysis eg: 2020: ")
    alldata_file = ALLDATA_FILE
    mainpubs_file = MAINPUBS_FILE
    savepath = SAVEPATH
    min_year = MIN_YEAR
    max_year = MAX_YEAR
    alldata_df = pd.read_excel(alldata_file)
    mainpubs_df = pd.read_excel(mainpubs_file)

    no_of_topics = int(len(alldata_df.index) * 0.05)   # 5% of all publications in the topic
    topics, lda_model, dictionary = topic_model.prepare_topics(alldata_df, no_of_topics)
    alldata_df = tag_pubs_to_topics(alldata_df, lda_model, dictionary)
    node_dict = create_nodes(alldata_df, mainpubs_df)
    connected_nodes_list, components = create_network_file(node_dict, alldata_df)

    word_bank = textminer.mine_word_bank(alldata_df, "Title", "Abstract")
    list_of_cluster_df, linegraph_data = create_cluster_indi(components, alldata_df, word_bank, min_year, max_year, lda_model, dictionary)
    create_cluster_sum(list_of_cluster_df, linegraph_data, min_year, max_year)
    return None

def start_analysis(alldata_file, mainpubs_file, savepath, min_year, max_year):
    min_year = int(min_year)
    max_year = int(max_year)
    alldata_df = pd.read_excel(alldata_file)
    mainpubs_df = pd.read_excel(mainpubs_file)
    global SAVEPATH
    SAVEPATH = savepath

    no_of_topics = int(len(alldata_df.index) * 0.05)   # 5% of all publications in the topic
    print("Number of topics: " + str(no_of_topics))
    topics, lda_model, dictionary = topic_model.prepare_topics(alldata_df, no_of_topics)
    alldata_df = tag_pubs_to_topics(alldata_df, lda_model, dictionary)

    print("Creating Network File now")
    node_dict = create_nodes(alldata_df, mainpubs_df)
    connected_nodes_list, components = create_network_file(node_dict, alldata_df)
    print("Looking into Clusters now")

    word_bank = textminer.mine_word_bank(alldata_df, "Title", "Abstract")
    list_of_cluster_df, linegraph_data = create_cluster_indi(components, alldata_df, word_bank, min_year, max_year, lda_model, dictionary)
    create_cluster_sum(list_of_cluster_df, linegraph_data, min_year, max_year)
    print("Analysis Completed")

    return 0


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