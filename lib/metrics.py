import pandas as pd
from datetime import datetime

def growth_index(cluster, total_doc, max_year, min_year):
    no_of_doc_cluster = len(cluster.index)
    cluster_percentage = no_of_doc_cluster / total_doc
    data_collection_period = max_year - min_year
    sum_of_growth = 0
    for x in range(0, data_collection_period):
        up_to_current_year = max_year - x
        up_to_previous_year = up_to_current_year - 1
        current_year_count = len(cluster[cluster["Year"] <= up_to_current_year])
        previous_year_count = len(cluster[cluster["Year"] <= up_to_previous_year])
        if (previous_year_count > 0):
            sum_of_growth = sum_of_growth + ((current_year_count - previous_year_count) / previous_year_count)
        else:
            sum_of_growth = current_year_count
            break

    growth_index = cluster_percentage * (sum_of_growth / ((data_collection_period - 1) * 100))
    print(cluster_percentage)
    print(sum_of_growth)
    return growth_index

def impact_index(cluster):
    times_cited = cluster["No_of_citations"].sum()
    cluster_size = len(cluster.index)
    impact_index = times_cited / cluster_size
    return impact_index

# def sci_based_index():
#     return None

def get_cluster_type(cluster, year_range):
    recently_emerging_counter = 0
    persistent_emerging_counter = set()
    current_year = datetime.now().year
    for index, row in cluster.iterrows():
        published_year = row["Year"]
        if published_year == 0:
            continue
        else: 
            persistent_emerging_counter.add(published_year)
            if (int(published_year) >= current_year - 3):
                recently_emerging_counter = recently_emerging_counter + 1
    cluster_type = None
    if (len(cluster) < 0):
        cluster_type = "Outlier"
    else:
        if ((recently_emerging_counter/len(cluster) * 100) >= 80):
            cluster_type = "Recently Emerging Cluster"
        elif (len(persistent_emerging_counter) > (year_range/2)):
            cluster_type = "Persistently Emerging Cluster"
        else:
            cluster_type = "Neutral Cluster"
    
    return cluster_type

