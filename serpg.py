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


def retrieve_docs_2(topic, key, min_year, max_year, num_to_retrieve, citation_limit, offset):
    ''' Retrieves publications of a topic in Google Scholar through the SERPAPI
    as well as the publications that cite this publication for 1 iteration.
    To be used together with GUI for GUI to track each iteration for UX feature

    Parameters
    ----------------
    topic : str
                the topic of interest

    key : str
                the api key to connect SERPAPI successfully

    min_year : int
                the earliest year to limit the period of publication retrieval

    max_year : int
                the latest year to limit the period of publication retrieval

    num_to_retrieve : int
                the number of publications wanted

    citation_limit : int
                the number of citing publications wanted

    offset : int
                the offset to be provided to SERPAPI to retrieve new publications.
    
    Returns
    ---------------
    alldata_dict : dict
                a dictionary containing all publications extracted

                key, value = Result_id, List of Publication info
                Publication info = ['Title', 'Year', 'Abstract', 'Citedby_id', 'No_of_citations', 'Result_id']

    mainpubs_dict : dict
                a dictionary containing root publications extracted. Does
                not contain publications extracted by retrieve_citing_pub(...)

                key, value = Result_id, List of Publication info
                Publication info = ['Title', 'Year', 'Abstract', 'Citedby_id', 'No_of_citations', 'Result_id', 'Type_of_Pub', 'Citing_pubs_id']
    '''

    params = {
        "api_key": key,
        "engine": "google_scholar",
        "q": topic,
        "hl": "en",
        "as_ylo": min_year,
        "as_yhi": max_year,
        "start": offset,
        "num": num_to_retrieve,
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    alldata_dict = {}
    rootpub_counter = 0
    if ("organic_results" in results):
        result_list = results["organic_results"]
        for entry in result_list:
            title = entry["title"]
            year, authors, authors_id = extract_year_and_authors(entry["publication_info"])
            snippet = entry["snippet"] if "snippet" in entry else "Empty"
            hyperlink = entry["link"] if "link" in entry else "Unavaliable"
            cite_id = entry["inline_links"].get("cited_by").get("cites_id") if "cited_by" in entry["inline_links"] else "Empty"
            total_cites = entry["inline_links"].get("cited_by").get("total") if "cited_by" in entry["inline_links"] else 0
            result_id = entry["result_id"]

            node_data, citing_result_id = retrieve_citing_pub(result_id, cite_id, min_year, max_year, citation_limit, key)
            alldata_df_entry = Node(title, year, snippet, authors, authors_id, hyperlink, cite_id, total_cites, result_id, "Root Publication", citing_pub_id=citing_result_id)

            alldata_dict[result_id] = alldata_df_entry
            if result_id in node_data:
                node_data.pop(result_id)
            alldata_dict.update(node_data)  #Need to make sure it doesnt update the Root Publications
        rootpub_counter = len(result_list)
            
    return alldata_dict, rootpub_counter


def retrieve_citing_pub(root_pub_id, cites_id, min_year, max_year, citation_limit, key):
    ''' Retrieves the citing publications of a specific publication in Google Scholar through the SERPAPI

    Parameters
    ----------------
    cites_id : str
                the cites_id of a publication that is provided by Google Scholar

    min_year : int
                the earliest year to limit the period of publication retrieval

    max_year : int
                the latest year to limit the period of publication retrieval

    citation_limit : int
                the number of citing publications wanted

    key : str
                the api key to connect SERPAPI successfully

    Returns
    ---------------
    node_data : dict
                a dictionary of publications that cite the main publication identified by cites_id.
                key, value = Result_id, Publication

    citing_pub_id_string : str
                a string of Result_id of the retrieved publication, separated by ;
    '''

    node_data = {}
    result_id_list = []
    # result_list = []
    total_retrieved = 0
    while (total_retrieved < citation_limit):
        if cites_id == "Empty":
            break
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
            # result_list += results["organic_results"]
            for doc in results['organic_results']:
                title = doc["title"]
                snippet = doc["snippet"] if "snippet" in doc else "Empty"
                cite_id = doc["inline_links"].get("cited_by").get("cites_id") if "cited_by" in doc["inline_links"] else "Empty"
                year, authors, authors_id = extract_year_and_authors(doc["publication_info"])
                hyperlink = doc["link"] if "link" in doc else "Unavaliable"
                total_cites = doc["inline_links"].get("cited_by").get("total") if "cited_by" in doc["inline_links"] else 0
                result_id = doc["result_id"]
                node = Node(title, year, snippet, authors, authors_id, hyperlink, cite_id, total_cites, result_id, "Citing Publication", cites=root_pub_id)
                # node_in_list_form = [title, year, snippet, authors, authors_id, hyperlink, cites_id, total_cites, result_id, "Citing Publication", ""]
                node_data[result_id] = node
                result_id_list.append(result_id)
            total_retrieved += len(results["organic_results"])
        else:
            break
    citing_pub_id_string = ";".join(result_id_list)
    return node_data, citing_pub_id_string

def extract_year_and_authors(publication_info):
    ''' extracts the authors and their ids from a list of dictionaries retrieved from google scholar

        Parameters
        ------------
        publication_info: dict
                        A dictionary of "Year" : string and "Authors" : list

        Returms
        ------------
        year: int
                The year of publication
        authors : str
                names of authors separated by ;
        authors_id : str
                id of authors separated by ;
    '''
    year = 0
    authors = "Unavaliable"
    authors_id = "Unavaliable"

    year_string = publication_info["summary"]
    match = re.search(r'\b(19|20)\d{2}(?=[ ])(?![^ ])\b', year_string)
    if match:
        year = int(match.group())

    if "authors" in publication_info:
        author_name_list = []
        author_id_list = []
        for author in publication_info["authors"]:
            author_name_list.append(author["name"])
            author_id_list.append(author["author_id"])
        authors = ";".join(author_name_list)
        authors_id = ";".join(author_id_list)
        

    return year, authors, authors_id


def add_to_df(df, pub_dict):
    ''' Adds a dictionary of publication into the dataframe. This function
    will check if an entry already exists by checking for the unique Result_id of the publication
    which should be the key of the dictionary. 

    Parameters
    ----------------
    df : pandas Dataframe
    
    pub_dict : publication dictionary (key,value = Result_id, Publication)
    
    Returns
    ---------------
    pandas Dataframe : Updated pandas Dataframe containing the dictonary
    '''

    for pub_id, pub in pub_dict.items():
        publication = [pub.title, pub.year, pub.abstract, pub.authors, 
                        pub.author_id, pub.hyperlink, pub.cite_id, 
                        pub.cite_count, pub.result_id, pub.type , pub.citing_pub_id, pub.cites]
        if (df.loc[(df['Result_id'] == pub_id)].empty):  # avoiding duplicates
            df_entry = publication
            df.loc[len(df.index)] = df_entry
        else:
            pub_in_df = df.loc[(df["Result_id"] == pub_id)][0]
            if (pub_in_df["Type of Pub"] == "Citing Publication" and pub.type == "Root Publication"):
                pub_in_df["Type of Pub"] = "Root Publication"
                pub_in_df["Citing_pubs_id"] = pub.citing_pub_id
                pub_in_df["Cites"] = pub_in_df["Cites"] + ";" + pub.cites
                
    return df


def getKey():
    ''' Retrieves the key from key.json file

    Returns
    --------------
    str : specific key located in the key.json file

    '''
    key = ''
    with open('key.json') as json_file:
        data = json.load(json_file)
        key = data['SERPAPIKey']
    json_file.close()
    return key


if __name__ == "__main__":
    main()
