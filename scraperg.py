import numpy as np
import pandas as pd
from scholarly import scholarly
from scholarly import ProxyGenerator
from scraper_api import ScraperAPIClient

from lib.node import Node
import json

TOPIC = "Computer Vision"
MIN_YEAR = 2010
MAX_YEAR = 2020
LIMIT = 4
CITATION_LIMIT = 3

def retrieve_main_doc(topic, min_year, max_year, limit, pg):
    scholarly.use_proxy(pg)
    # search_query = scholarly.search_pubs(query=topic, year_low=min_year, year_high=max_year, sort_by='relevance')
    search_query = scholarly.search_author('Steven A Cholewiak')
    doc = next(search_query)
    scholarly.pprint(doc)
    # cited_by = scholarly.citedby(next(search_query))
    main_doc_list = []
    main_doc_excel = []
    return None
    # for x in range(0, limit):
    #     #create_entries
    #     doc = next(search_query)
    #     scholarly.pprint(doc)
    #     # print([citation['bib']['title'] for citation in scholarly.citedby(doc)])
    #     main_doc_list.append(doc)
    #     df_entry = [doc["bib"]["title"], doc["bib"]["pub_year"], doc["bib"]["abstract"], 
    #                 doc["bib"]["venue"], doc["citedby_url"], doc["num_citations"], 
    #                 doc["pub_url"], hash(doc["pub_url"])]
    #     main_doc_excel.append(df_entry)

    # col = ['Title', 'Year', 'Abstract', 'Venue', 'Citedby_url', 'No_of_citations', 'Pub_url', 'Pub_url_hash']
    # main_doc_df = pd.DataFrame(data=main_doc_excel, columns=col)
    # path = "./data/test.xlsx"
    # main_doc_df.to_excel(path, index=False)
    
    # return main_doc_list

def prepare_citedby_node(doc_list, pg):
    full_node_table = {}
    scholarly.use_proxy(pg)
    for doc in doc_list:
        limit = doc["num_citations"] if (doc["num_citations"] < CITATION_LIMIT) else CITATION_LIMIT
        print([citation['bib']['title'] for citation in scholarly.citedby(doc)])
        indi_doc_list = []
        # for x in range(0, limit):
        #     doc = next(citedby_query)
        #     scholarly.pprint(doc)
        #     doc_list.append(doc)
        # for doc in indi_doc_list:
        #     print("*****************")
        #     print(hash(doc["pub_url"]))
        #     print("xxxxxxxxxxxxxxxxx")
        #     if hash(doc["pub_url"]) not in full_node_table:
        #         node = Node(doc["bib"]["title"], doc["bib"]["pub_year"], doc["bib"]["abstract"], 
        #                 doc["bib"]["venue"], doc["citedby_url"], doc["num_citations"], 
        #                 doc["pub_url"])
        #         full_node_table[node.node_hash] = node
        #     else:
        #         node = full_node_table[hash(doc["pub_url"])]
        #     for doc in indi_doc_list:
        #         if hash(doc["pub_url"]) != node.node_hash:
        #             node.add_edge(hash(doc["pub_url"]))

    # return full_node_table
    return None

def getKey():
    key = ''
    with open('key.json') as json_file:
        data = json.load(json_file)
        key = data['ScraperAPIKey']
    json_file.close()
    return key

def main():
    # topic = input("Please indicate topic to be researched on: ")
    # min_year = input("Please indicate min year: ")
    # max_year = input("Please indicate max year: ")
    api_key = getKey()
    pg = ProxyGenerator()
    pg.ScraperAPI(api_key)
    main_doc_list = retrieve_main_doc(TOPIC, MIN_YEAR, MAX_YEAR, LIMIT, pg)
    # cited_node_dict = prepare_citedby_node(main_doc_list, pg)
    # cited_node_dict.values()[0].node_print
    return None


if __name__ == "__main__":
    main() 