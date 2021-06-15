import numpy as np
import pandas as pd
import csv
import os
import re
from datetime import datetime
from serpapi import GoogleSearch

from lib.node_serpapi import Node
import json

TOPIC = "Computer Vision"
MIN_YEAR = 2010
MAX_YEAR = 2020
LIMIT = 10
SAVE_PATH = "./data/"
CURRENT_TIME_STRING = datetime.now().strftime("%d-%m-%Y_%H%M")


def retrieve_docs(topic, min_year, max_year, limit, citation_limit, key):
    total_retrieved = 0
    alldata_col = ['Title', 'Year', 'Abstract',
                   'Citedby_id', 'No_of_citations', 'Result_id']
    alldata_df = pd.DataFrame(columns=alldata_col)
    main_data_col = ['Title', 'Year', 'Abstract', 'Citedby_id',
                     'No_of_citations', 'Result_id', 'Type_of_Pub', 'Citing_pubs_id']
    main_data_df = pd.DataFrame(columns=main_data_col)
    while (total_retrieved < limit):
        remainder = limit - total_retrieved
        num_to_retrieve = 20 if remainder >= 20 else remainder
        params = {
            "api_key": key,
            "engine": "google_scholar",
            "q": topic,
            "hl": "en",
            "as_ylo": min_year,
            "as_yhi": max_year,
            "start": total_retrieved,
            "num": num_to_retrieve
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        if ("organic_results" in results):
            result_list = results["organic_results"]
            for entry in result_list:
                title = entry["title"]
                year = extract_year(entry["publication_info"]["summary"])
                snippet = entry["snippet"]
                cites_id = entry["inline_links"]["cited_by"]["cites_id"]
                total_cites = entry["inline_links"]["cited_by"]["total"]
                result_id = entry["result_id"]

                node_data, citing_result_id = retrieve_citing_pub(cites_id,
                                                                min_year, max_year,
                                                                citation_limit, key)

                alldata_df_entry = [title, year, snippet, cites_id, total_cites, result_id]
                main_df_entry = [title, year, snippet, cites_id, total_cites, 
                                result_id, "Main_Pub", citing_result_id]

                main_data_df.loc[len(main_data_df.index)] = main_df_entry
                if (alldata_df.loc[(alldata_df['Result_id'] == result_id)].empty):
                    alldata_df.loc[len(alldata_df.index)] = alldata_df_entry
                alldata_df = add_to_df(alldata_df, node_data)
            total_retrieved += len(result_list)
        else: 
            break

    alldata_path = SAVE_PATH + "alldata.xlsx"
    alldata_df.to_excel(alldata_path, index=False)
    mainpub_path = SAVE_PATH + "main_pubs.xlsx"
    main_data_df.to_excel(mainpub_path, index=False)

    return alldata_df, main_data_df


def extract_year(string):
    match = re.search(r'\b(19|20)\d{2}(?=[ ])(?![^ ])\b', string)
    if match:
        return int(match.group())
    else:
        return 0


def add_to_df(df, pub_list):
    for pub in pub_list:
        if (df.loc[(df['Result_id'] == pub.result_id)].empty):  # avoiding duplicates
            df_entry = [pub.title,
                        pub.year,
                        pub.abstract,
                        pub.cite_id,
                        pub.cite_count,
                        pub.result_id]
            df.loc[len(df.index)] = df_entry
    return df


def retrieve_citing_pub(cites_id, min_year, max_year, citation_limit, key):
    node_data = []
    result_id_list = []
    result_list = []
    total_retrieved = 0
    while (total_retrieved < citation_limit):
        remainder = citation_limit - total_retrieved
        num_to_retrieve = remainder if remainder < 20 else 20
        params = {
            "api_key": key,
            "engine": "google_scholar",
            "hl": "en",
            "as_ylo": min_year,
            "as_yhi": max_year,
            "start": total_retrieved,
            "num": remainder,
            "cites": cites_id,
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        if ("organic_results" in results):
            result_list += results["organic_results"]
            for doc in result_list:
                title = doc["title"]
                year = extract_year(doc["publication_info"]["summary"])
                snippet = doc["snippet"] if "snippet" in doc else "Empty",
                cite_id = doc["inline_links"].get("cited_by").get(
                    "cites_id") if "cited_by" in doc["inline_links"] else "Empty"
                total_cited = doc["inline_links"].get("cited_by").get(
                    "total") if "cited_by" in doc["inline_links"] else 0
                result_id = doc["result_id"]
                node = Node(title, year, snippet, cite_id,
                            total_cited, result_id)
                node_data.append(node)
                result_id_list.append(result_id)
            total_retrieved += len(results["organic_results"])
        else: 
            break
    citing_pub_id_string = ";".join(result_id_list)
    return node_data, citing_pub_id_string


def getKey():
    key = ''
    with open('key.json') as json_file:
        data = json.load(json_file)
        key = data['SERPAPIKey']
    json_file.close()
    return key


def main():
    topic = input("Please indicate topic to be researched on: ")
    min_year = int(input("Please indicate min year eg. 2010: "))
    max_year = int(input("Please indicate max year eg. 2020: "))
    limit = int(input("Please indicate the number of root documents eg. 20: "))
    citation_limit = int(input(
        "Please indicate the number of citing documents per root document eg. 20: "))
    # topic = TOPIC
    # min_year = MIN_YEAR
    # max_year = MAX_YEAR
    # limit = LIMIT
    api_key = getKey()
    global SAVE_PATH  # Change global constant
    SAVE_PATH = "./data/" + CURRENT_TIME_STRING + "_" + topic + "/"
    if not os.path.exists(SAVE_PATH):
        os.makedirs(SAVE_PATH)
    alldata_df, main_pubs_df = retrieve_docs(
        topic, min_year, max_year, limit, citation_limit, api_key)
    # cited_node_dict, data_df, path_to_cited_doc = prepare_citedby_node(main_doc_list, MIN_YEAR, MAX_YEAR, CITATION_LIMIT, api_key)
    # save_all_nodes(cited_node_dict)
    # create_network_excel(cited_node_dict, data_df)
    return None


if __name__ == "__main__":
    main()
