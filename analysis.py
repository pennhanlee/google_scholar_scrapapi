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


def create_nodes(alldata_df):
    ''' Creates node objects for each entry in the dataframe including
        the bibliographic couples and their weights

        Parameters
        ------------
        alldata_df : pandas DataFrame
                a DataFrame containing all publications extracted
                columns : ['Title', 'Year', 'Abstract',
                    'Citedby_id', 'No_of_citations', 'Result_id']

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
    rootpub_df = alldata_df[alldata_df["Type of Pub"] == "Root Publication"]
    for index, row in rootpub_df.iterrows():
        rootpub = row
        rootpub_node = Node(rootpub["Title"], rootpub["Year"], rootpub["Abstract"], rootpub["Authors"],
                            rootpub["Authors_id"], rootpub["Hyperlink"], rootpub['Citedby_id'],
                            rootpub["No_of_citations"], rootpub["Result_id"], rootpub["Type of Pub"],
                            rootpub["Citing_pubs_id"], rootpub["Cites"], rootpub['Topic Number'], rootpub['Topic'], 
                            rootpub['Topic Probability'])
        citing_pubs_id_list=rootpub["Citing_pubs_id"].split(";")
        if rootpub_node.result_id not in full_node_dict:
            full_node_dict[rootpub_node.result_id]=rootpub_node
        else:
            pub_in_dict=full_node_dict[rootpub_node.result_id]
            rootpub_node.edge_dict.update(pub_in_dict.edge_dict)
            full_node_dict[rootpub_node.result_id]=rootpub_node

        for result_id in citing_pubs_id_list:
            node=None
            if result_id not in full_node_dict:
                citing_pub=alldata_df.loc[alldata_df['Result_id'] == result_id]
                citing_pub=citing_pub.iloc[0]
                node=Node(citing_pub["Title"], citing_pub["Year"], citing_pub["Abstract"], citing_pub["Authors"],
                            citing_pub["Authors_id"], citing_pub["Hyperlink"], citing_pub['Citedby_id'],
                            citing_pub["No_of_citations"], citing_pub["Result_id"], citing_pub["Type of Pub"],
                            citing_pub["Citing_pubs_id"], citing_pub["Cites"], citing_pub['Topic Number'], citing_pub['Topic'],
                            citing_pub['Topic Probability'])
                full_node_dict[node.result_id]=node
            else:
                node=full_node_dict[result_id]
            for bibcouple_id in citing_pubs_id_list:
                if bibcouple_id != node.result_id:
                    node.add_edge(bibcouple_id)

            rootpub_node.add_edge(result_id)

    return full_node_dict


def create_network_file(node_dict, alldata_df, min_strength, savepath):
    ''' Creates a network .xlsx file to be used for visualisation on Cytoscape
        columns: ['Publication_1', 'Publication_2',
            'Weight', 'Topic Number', 'Topic']

        Parameters
        ------------
        node_dict : dict
                dictionary of nodes
                key, value: Result_id, Node object

        alldata_df : pandas DataFrame
                a DataFrame containing all publications extracted
                columns : ['Title', 'Year', 'Abstract',
                    'Citedby_id', 'No_of_citations', 'Result_id']

        min_strength: int
                the minimum coupling strength to add this edge into the graph

        savepath: str
                the path to the folder to save this cluster

        Returns :
        connected_nodes : list
                List of lists of node and edge information

        components : list
                List of the clusters in the analysis
    '''

    connected_nodes=[]
    node_in_network=set()
    counter=1
    network_graph=nx.Graph()
    for node in node_dict.values():
        bib_couple_dict=node.edge_dict
        pub_title=node.title
        pub_topic_no=node.topic_no
        pub_topic=node.topic
        node_in_network.add(pub_title)
        added_to_graph=False
        for couple_id, couple_edge_weight in bib_couple_dict.items():
            couple_pub=alldata_df.loc[alldata_df["Result_id"] == couple_id]
            couple_pub_title=couple_pub.iloc[0]["Title"]
            # To avoid duplication of edges ( A - B and B - A )
            if (couple_pub_title in node_in_network) or couple_edge_weight < min_strength:
                continue
            else:
                connected_nodes.append(
                    [pub_title, couple_pub_title, couple_edge_weight, pub_topic_no, pub_topic])
                network_graph.add_edge(
                    pub_title, couple_pub_title, weight=couple_edge_weight)
                added_to_graph=True
        if not added_to_graph:
            network_graph.add_node(pub_title)
            connected_nodes.append([pub_title])

    graphpath=savepath + "/networkgraph.graphml"
    nx.write_graphml_lxml(network_graph, graphpath)

    print(alldata_df.iloc[0]["Year"])
    print(alldata_df[["Year"]].head(1))
    col=['Publication_1', 'Publication_2', 'Weight', 'Topic Number', 'Topic']
    network_df=pd.DataFrame(data=connected_nodes, columns=col)
    components=_create_clusters_greedynewman(network_graph)
    clusters=[]
    temp_df_list=[]
    recent_outlier=[]
    outlier=[]
    cluster_counter=1
    for x in range(0, len(components)):
        cluster=components[x]
        if (len(cluster) <= 1):
            temp_df=alldata_df[alldata_df["Title"].isin(
                cluster)]  # add cluster number to nodes
            if is_recent_outlier(temp_df.iloc[0]["Year"], alldata_df["Year"].max()):
                recent_outlier.append(temp_df)
            else:
                outlier.append(temp_df)
            network_df_entry=temp_df[["Title"]].rename(
                columns={"Title": "Publication_1"}, inplace=False)
            temp_df_list.append(network_df_entry)
            continue
        else:
            temp_df=network_df[network_df["Publication_1"].isin(
                cluster)]  # add cluster number to nodes
            temp_df.insert(len(temp_df.columns), "Cluster", cluster_counter)
            temp_df_list.append(temp_df)
            clusters.append(cluster)
            cluster_counter += 1


    network_path=savepath + "/network.xlsx"
    recent_outlier_path=savepath + "/recently emerging outliers.xlsx"
    outlier_path=savepath + "/outliers.xlsx"
    network_df=pd.concat(temp_df_list)
    network_df.to_excel(network_path, index=False)
    recent_outlier_df=pd.concat(recent_outlier) if len(
        recent_outlier) else pd.DataFrame()
    recent_outlier_df.to_excel(recent_outlier_path, index=False)
    outlier_df=pd.concat(outlier) if len(outlier) else pd.DataFrame()
    outlier_df.to_excel(outlier_path, index=False)

    return connected_nodes, clusters

def create_network_file_2(node_dict, alldata_df, min_strength, savepath):
    node_in_network = set()
    network_graph=nx.Graph()
    final_interaction_list = []
    for node_id, node in node_dict.items():
        pub_couple_dict = node.edge_dict
        pub_id = node_id
        node_in_network.add(pub_id)
        added_to_graph = False
        interactions = create_bib_couple_edges(node, alldata_df, min_strength)
        for interaction in interactions:
            pub_1_id = interaction[0]
            pub_2_id = interaction[1]
            couple_edge_weight = interaction[2]
            if (pub_2_id in node_in_network):
                continue
            else:
                network_graph.add_edge(pub_1_id, pub_2_id, weight=couple_edge_weight)
                final_interaction_list.append(interaction)
                added_to_graph=True
        if not added_to_graph:
            network_graph.add_node(pub_id)

    components=_create_clusters_greedynewman(network_graph)

    col=['Pub_1', 'Pub_2', 'Weight', "Interaction", 
          'Pub_1_title', 'Pub_1_abstract', 'Pub_1_year', 'Pub_1_authors', 'Pub_1_topic', 'Pub_1_link', "Pub_1_type",
          'Pub_2_title', 'Pub_2_abstract', 'Pub_2_year', 'Pub_2_authors', 'Pub_2_topic', 'Pub_2_link', "Pub_2_type" ]
    network_df = pd.DataFrame(data=final_interaction_list, columns=col)
    create_outlier_files(components, alldata_df, savepath)
    network_df, clusters = tag_publication_to_clusters(network_df, components)
    
    root_and_citing_pubs = link_root_and_cite_pubs(alldata_df)

    for interaction in root_and_citing_pubs:
        network_df.loc[len(network_df.index)] = interaction

    network_path=savepath + "/network.xlsx"
    network_df.to_excel(network_path, index=False)

    return clusters

def link_root_and_cite_pubs(alldata_df):
    root_pub_df = alldata_df[alldata_df["Type of Pub"] == "Root Publication"]
    root_cite_interaction = []
    for index, row in root_pub_df.iterrows():
        root_pub = row
        root_pub_id = row["Result_id"]
        root_pub_title = root_pub["Title"]
        root_pub_abstract = root_pub["Abstract"]
        root_pub_year = root_pub["Year"]
        root_pub_authors = root_pub["Authors"]
        root_pub_topic = root_pub["Topic"]
        root_pub_hyperlink = root_pub["Hyperlink"]
        root_pub_type = root_pub["Type of Pub"]
        root_pub_citing_pubs = root_pub["Citing_pubs_id"]
        list_of_citing_pubs = root_pub_citing_pubs.split(";")
        for citing_pub_id in list_of_citing_pubs:
            citing_pub = alldata_df.loc[alldata_df["Result_id"] == citing_pub_id]
            citing_pub = citing_pub.iloc[0]
            citing_pub_title = citing_pub["Title"]
            citing_pub_abstract = citing_pub["Abstract"]
            citing_pub_year = citing_pub["Year"]
            citing_pub_authors = citing_pub["Authors"]
            citing_pub_topic = citing_pub["Topic"]
            citing_pub_hyperlink = citing_pub["Hyperlink"]
            citing_pub_type = citing_pub["Type of Pub"]
            citing_pub_cites = citing_pub["Cites"]
            interaction = [root_pub_id, citing_pub_id, 1, "Cited By", 
                                root_pub_title, root_pub_abstract, root_pub_year, root_pub_authors, root_pub_topic, root_pub_hyperlink, root_pub_type, 
                                citing_pub_title, citing_pub_abstract, citing_pub_year, citing_pub_authors, citing_pub_topic, citing_pub_hyperlink, citing_pub_type, ""]
            root_cite_interaction.append(interaction)

    return root_cite_interaction

def create_bib_couple_edges(node, alldata_df, min_strength):
    interaction_list = []
    bib_couple_dict = node.edge_dict
    pub_id = node.result_id
    pub_title = node.title
    pub_abstract = node.abstract
    pub_year = node.year
    pub_authors = node.authors
    pub_topic = node.topic
    pub_hyperlink = node.hyperlink
    pub_type = node.type
    pub_cites = node.cites
    for couple_id, couple_edge_weight in bib_couple_dict.items():
        if couple_edge_weight >= min_strength:
            couple_pub = alldata_df.loc[alldata_df["Result_id"] == couple_id]
            couple_pub = couple_pub.iloc[0]
            couple_pub_id = couple_id
            couple_pub_title = couple_pub["Title"]
            couple_pub_abstract = couple_pub["Abstract"]
            couple_pub_year = couple_pub["Year"]
            couple_pub_authors = couple_pub["Authors"]
            couple_pub_topic = couple_pub["Topic"]
            couple_pub_hyperlink = couple_pub["Hyperlink"]
            couple_pub_type = couple_pub["Type of Pub"]
            couple_pub_cites = couple_pub["Cites"]
            interaction = [pub_id, couple_pub_id, couple_edge_weight, "Bibliographic Couple", 
                            pub_title, pub_abstract, pub_year, pub_authors, pub_topic, pub_hyperlink, pub_type,
                            couple_pub_title, couple_pub_abstract, couple_pub_year, couple_pub_authors, couple_pub_topic, couple_pub_hyperlink, couple_pub_type]
            interaction_list.append(interaction)

    return interaction_list

def tag_publication_to_clusters(network_df, components):
    temp_df_list = []
    clusters = []
    cluster_counter = 1
    for x in range(0, len(components)):
        cluster = components[x]
        if len(cluster) <= 1:
            continue

        temp_df = network_df[network_df["Pub_1"].isin(cluster)]  # add cluster number to nodes
        temp_df.insert(len(temp_df.columns), "Cluster", cluster_counter)
        temp_df_list.append(temp_df)
        clusters.append(cluster)
        cluster_counter += 1
    
    new_df = pd.concat(temp_df_list)
    
    return new_df, clusters

def create_outlier_files(components, alldata_df, savepath):
    recent_outlier = []
    outlier = []
    for x in range(0, len(components)):
        cluster=components[x]
        if (len(cluster) <= 1):
            temp_df=alldata_df[alldata_df["Title"].isin(cluster)]  # add cluster number to nodes
            if is_recent_outlier(temp_df.iloc[0]["Year"], alldata_df["Year"].max()):
                recent_outlier.append(temp_df)
            else:
                outlier.append(temp_df)

    recent_outlier_path = savepath + "/recently emerging outliers.xlsx"
    outlier_path = savepath + "/outliers.xlsx"
    recent_outlier_df = pd.concat(recent_outlier) if (len(recent_outlier) > 0) else pd.DataFrame()
    recent_outlier_df.to_excel(recent_outlier_path, index=False)
    outlier_df = pd.concat(outlier) if (len(recent_outlier) > 0) else pd.DataFrame()
    outlier_df.to_excel(outlier_path, index=False)

    return alldata_df
    

def is_recent_outlier(year, max_year):
    if (max_year - year < 3):
        return True
    else:
        return False

def create_cluster_indi_2(cluster, cluster_no, cluster_name, alldata_df, min_year, max_year, savepath):
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
                columns : ['Title', 'Year', 'Abstract',
                    'Citedby_id', 'No_of_citations', 'Result_id']

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

        savepath: str
                the path to the folder to save this cluster

        Returns
        ----------
        cluster_name : str
                cluster name derived from analysis

        cluster_df : pandas DataFrame
                pandas DataFrame containing entries of the cluster

        linegraph_data : linegraph object
                Linegraph object created from analysis
    '''

    no_of_doc=len(alldata_df.index)
    cluster_df=alldata_df[alldata_df["Result_id"].isin(cluster)]
    cluster_df.insert(len(cluster_df.columns), "Cluster", cluster_no)
    word_list=textminer_nlp.get_word_list(cluster_df, "Title", "Abstract")
    cluster_name = "cluster " + str(cluster_no)
    # cluster_summary = textminer_nlp.create_extractive_summary(cluster_df, 2)
    # print(cluster_name)
    # print(cluster_summary)
    if not os.path.exists(savepath + "/{}".format(cluster_name)):
        os.makedirs(savepath + "/{}".format(cluster_name))
    data_path=savepath + "/{}/{}.xlsx".format(cluster_name, cluster_name)
    linegraph_path=savepath + "/{}/linegraph.png".format(cluster_name)
    quadrantgraph_path=savepath + "/{}/linegraph.png".format(cluster_name)
    wordcloud_path=savepath + "/{}/wordcloud.png".format(cluster_name)
    cluster_df.to_excel(data_path, index=False)
    graphcreator.generate_word_cloud(word_list, wordcloud_path)
    linegraph_data=graphcreator.generate_year_linegraph(
        cluster_df, linegraph_path, min_year, max_year)
    quadrant_graph = graphcreator.generate_quadrant_graph(cluster_df, quadrantgraph_path)

    return cluster_df, linegraph_data

def create_cluster_sum(clusters_dict, linegraph_data, min_year, max_year, savepath):
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

        savepath : str
                the path to the folder to save this cluster

        Returns
        ------------
        cluster_sum_df : pandas DataFrame
                pandas DataFrame of the summary of the clusters

    '''
    cluster_summary=[]
    total_doc=sum([len(cluster.index) for cluster in clusters_dict.values()])
    for cluster in clusters_dict:
        cluster_name=cluster
        cluster_df=clusters_dict[cluster]
        size=len(cluster_df.index)
        growth=metrics.growth_index(cluster_df, total_doc, min_year, max_year)
        impact=metrics.impact_index(cluster_df)
        cluster_type=metrics.get_cluster_type(cluster_df, min_year, max_year)
        current_cluster=[cluster_name, cluster_type, size, growth, impact]
        cluster_summary.append(current_cluster)

    col=['Name', 'Type', 'Size', 'Growth Index', 'Impact Index']
    cluster_sum_df=pd.DataFrame(cluster_summary, columns=col)
    data_path=savepath + "/summary.xlsx"
    linegraph_path=savepath + "/combined_linegraph.png"
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

    topics=lda_model.print_topics(num_topics=-1, num_words=4)
    topics.sort(key=lambda x: x[0])
    for index, row in cluster_df.iterrows():
        title=row["Title"]
        title=topic_model.prepare_text_for_lda(title)
        title_bow=dictionary.doc2bow(title)
        topic=lda_model.get_document_topics(title_bow)
        if len(topic) > 0:
            topic.sort(key=lambda x: x[1], reverse=True)
            # 0th index of First Tuple in list [(3, 0.523), ...]
            top_topic=topics[topic[0][0]]
            cluster_df.loc[index, 'Topic Number']=top_topic[0]
            cluster_df.loc[index, 'Topic']=top_topic[1]
            cluster_df.loc[index, 'Topic Probability']=topic[0][1]
        else:
            cluster_df.loc[index, 'Topic Number']=-1
            cluster_df.loc[index, 'Topic']="No Topic Assigned"
            cluster_df.loc[index, 'Topic Probability']=0

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

    graph=nx.Graph()
    for node in node_list:
        graph.add_edge(node[0], node[1], weight=node[2])
    return graph

def _create_clusters_girvannewman(graph):
    ''' Creates clusters based on the girvan newman clustering algorthim with modularity

        Parameters
        -----------
        graph : networkx graph
                a graph of nodes and edges created using the networkx graph constructor

        Returns
        -----------
        clusters: list of tuples
                the clusters derived from girvan_newman algorithm
    '''

    # components = girvan_with_modularity(graph)
    latest_mod=float(0)
    highest_mod=float(0)
    components=community.girvan_newman(graph)
    clusters=None
    while round(latest_mod, 2) >= round(highest_mod, 2):
        print(highest_mod)
        print(latest_mod)
        highest_mod=latest_mod
        clusters=next(components)
        latest_mod=community.modularity(graph, clusters)

    print(highest_mod)
    print(len(clusters))
    return clusters

def _create_clusters_greedynewman(graph):
    components=community.greedy_modularity_communities(graph)
    return components


def main():
    # alldata_file = input("Please provide filepath to alldata.xlsx: ")
    # mainpubs_file = input("Please provide filepath to main_pubs.xlsx: ")
    # savepath = input("Please provide the folder path to save the documents: ")
    # min_year = input("Please provide the earliest year in the analysis eg: 2010: ")
    # max_year = input("Please provide the latest year in the analysis eg: 2020: ")
    alldata_file=ALLDATA_FILE
    mainpubs_file=MAINPUBS_FILE
    savepath=SAVEPATH
    min_year=MIN_YEAR
    max_year=MAX_YEAR
    alldata_df=pd.read_excel(alldata_file)
    mainpubs_df=pd.read_excel(mainpubs_file)

    # 5% of all publications in the topic
    no_of_topics=int(len(alldata_df.index) * 0.05)
    topics, lda_model, dictionary=topic_model.prepare_topics(
        alldata_df, no_of_topics)
    alldata_df=tag_pubs_to_topics(alldata_df, lda_model, dictionary)
    node_dict=create_nodes(alldata_df, mainpubs_df)
    connected_nodes_list, components=create_network_file(node_dict, alldata_df)

    word_bank=textminer.mine_word_bank(alldata_df, "Title", "Abstract")
    list_of_cluster_df, linegraph_data=create_cluster_indi(
        components, alldata_df, word_bank, min_year, max_year, lda_model, dictionary)
    create_cluster_sum(list_of_cluster_df, linegraph_data, min_year, max_year)
    return None

def start_analysis(alldata_file, mainpubs_file, savepath, min_year, max_year):
    min_year=int(min_year)
    max_year=int(max_year)
    alldata_df=pd.read_excel(alldata_file)
    mainpubs_df=pd.read_excel(mainpubs_file)
    global SAVEPATH
    SAVEPATH=savepath

    # 5% of all publications in the topic
    no_of_topics=int(len(alldata_df.index) * 0.05)
    print("Number of topics: " + str(no_of_topics))
    topics, lda_model, dictionary=topic_model.prepare_topics(
        alldata_df, no_of_topics)
    alldata_df=tag_pubs_to_topics(alldata_df, lda_model, dictionary)

    print("Creating Network File now")
    node_dict=create_nodes(alldata_df, mainpubs_df)
    connected_nodes_list, components=create_network_file(node_dict, alldata_df)
    print("Looking into Clusters now")

    word_bank=textminer.mine_word_bank(alldata_df, "Title", "Abstract")
    list_of_cluster_df, linegraph_data=create_cluster_indi(
        components, alldata_df, word_bank, min_year, max_year, lda_model, dictionary)
    create_cluster_sum(list_of_cluster_df, linegraph_data, min_year, max_year)
    print("Analysis Completed")

    return 0


if __name__ == "__main__":
    alldata=pd.read_excel("./data/pizza/alldata.xlsx")
    create_nodes(alldata)


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
