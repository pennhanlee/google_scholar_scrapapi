import numpy as np
import pandas as pd
import os
from datetime import datetime

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
    excel_items = []
    for node in node_dict.values():
        bib_couple_dict = node.edge_dict
        pub_title = node.title
        for couple in bib_couple_dict.items():
            couple_id = couple[0]
            couple_pub = alldata_df.loc[alldata_df["Result_id"] == couple_id]
            couple_pub_title = couple_pub.iloc[0]["Title"]
            edge_weight = couple[1]
            excel_items.append([pub_title, couple_pub_title, edge_weight])
    col = ['Pub_1', 'Pub_2', 'Weight']
    excel_df = pd.DataFrame(data=excel_items, columns=col)
    path = SAVEPATH + "network.xlsx"
    excel_df.to_excel(path, index=False)
    return None

def create_clustersummary_file():
    return None

def create_cluster_file():
    return None

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
    create_network_file(node_dict, alldata_df)
    return None

if __name__ == "__main__":
    main()