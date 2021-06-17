from nltk import word_tokenize
from nltk.probability import FreqDist
from nltk.corpus import stopwords
from nltk import RegexpTokenizer
import pandas as pd
import numpy as np

TOKENIZER = RegexpTokenizer(r"\w+")

# def mine_cluster(df, word_bank, no_of_doc):
#     doc_word_count, cluster_fdist, cluster_word_list = mine_paper_info(df)
#     list_of_word_tuples = []
#     for word in cluster_fdist:
#         actual_word = word[0]
#         word_count = word[1]
#         total_word_count = word_bank[actual_word]
#         value = tf_idf(word_count, doc_word_count, total_word_count, no_of_doc)
#         list_of_word_tuples.append((actual_word, value))
#     list_of_word_tuples.sort(key=lambda x: x[1])
#     cluster_name = " ".join([x[0] for x in cluster_word_list.most_common(2)])
#     return cluster_word_list, cluster_name

def filter_stopwords(words):
    word_dict = {}
    filtered_words = []
    stop_words = set(stopwords.words("english"))
    for word in words:
        if word not in stop_words and len(word) > 0:
            filtered_words.append(word)
    for word in filtered_words:
        if word in word_dict:
            word_dict[word] += 1
        else:
            word_dict[word] = 1

    no_of_words = len(filtered_words)
    return word_dict, no_of_words


def mine_cluster(cluster, word_bank, total_no_of_doc, *args):
    words = []
    word_dict = {}
    for index, row in cluster.iterrows():
        for arg in args:
            words = words + TOKENIZER.tokenize(row[arg].lower()) 
    filtered_words, doc_word_count = filter_stopwords(words)
    for word in filtered_words.keys():
        actual_word = word
        word_count = filtered_words[word]
        total_word_count = word_bank[word]
        value = tf_idf(word_count, doc_word_count, total_word_count, total_no_of_doc)
        word_dict[word] = value

    word_tuple_list_desc = sorted(word_dict.items(), key=lambda x: x[1], reverse=True)
    cluster_name = word_tuple_list_desc[0][0] + " " + word_tuple_list_desc[1][0]

    raw_word_list = []
    for word in filtered_words.keys():
        for x in range(0, filtered_words[word]):
            raw_word_list.append(word)

    return word_dict, cluster_name, raw_word_list

    
def mine_word_bank(alldata_df, *args):
    words = []
    for index, row in alldata_df.iterrows():
        for arg in args:
            words = words + TOKENIZER.tokenize(row[arg].lower())
    filtered_words, total_no_words = filter_stopwords(words)
    return filtered_words


def term_freq(word_count, no_of_words):
    return word_count / no_of_words


def inv_doc_freq(word_count, no_of_doc):
    return np.log(no_of_doc/(word_count + 1))


def tf_idf(word_count, doc_word_count, total_word_count, no_of_doc):
    tf = term_freq(word_count, doc_word_count)
    idf = inv_doc_freq(total_word_count, no_of_doc)
    tf_idf = tf * idf
    return tf_idf
