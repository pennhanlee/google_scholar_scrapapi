import random
import pandas as pd
import numpy as np
from kneed import KneeLocator
import matplotlib.pyplot as plt

from nltk.corpus import wordnet, stopwords
from spacy.lang.en import English

from gensim.corpora import Dictionary
from gensim.models.ldamodel import LdaModel

from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

parser = English()
en_stop = set(stopwords.words('english'))


def tokenise(text):
    ''' Tokenises the provided string into individual words and converting them into lower caps, 
        in the process removing URLs and special titles that starts with @

        Parameters
        ------------
        text : str
                A string of words

        Returns
        ------------
        lda_tokens : list
                A list of words
    '''

    lda_tokens = []
    tokens = parser(text)
    for token in tokens:
        if token.orth_.isspace():
            continue
        elif token.like_url:
            lda_tokens.append('URL')
        elif token.orth_.startswith('@'):
            lda_tokens.append('SCREEN_NAME')
        else:
            lda_tokens.append(token.lower_)
    return lda_tokens


def get_lemma(word):
    ''' Converts a given word by lemmatization into its root form.
        
        Parameters
        ------------
        word : str
                a provided word to be lemmatized

        Returns
        -----------
        word : str
                the original word if lemmatization fails

        or

        lemma : str
                the root form of the word
    '''

    lemma = wordnet.morphy(word)
    if lemma is None:
        return word
    else:
        return lemma


def prepare_text_for_lda(text):
    ''' Prepares a string of words into individual words by processing
        the text through a minimum length of 4 chars, stopword filtering, lemmatizing

        Parameters
        ------------
        text : str
            A string of words

        Returns
        -----------
        tokens : list
            A list of words that have been processed
    '''

    tokens = tokenise(text)
    tokens = [token for token in tokens if len(token) >= 4]
    tokens = [token for token in tokens if token not in en_stop]
    tokens = [get_lemma(token) for token in tokens]
    return tokens


def prepare_bow_dictionary(text_list):
    ''' Prepares a list of words to create a bag of word dictionary and a corpus

        Parameters
        ------------
        text_list : list
                A list of words

        Returns
        -----------
        dictionary : gensim library dictionary object
                A dictionary object by gensim that contains words in the text and its frequency

        corpus : gensim library corpus object
    ''' 
    dictionary = Dictionary(text_list)
    corpus = [dictionary.doc2bow(text) for text in text_list]
    return dictionary, corpus



def retrieve_topic_for_doc(token_list, ldamodel, dictionary):
    ''' Analyses the documents and returns the probabilities for the topic that a document belongs to

        Parameters
        ------------
        token_list : list
                The list of words that was tokenised from the document

        ldamodel : gensim LDAModel
                The LDAModel produced through training with a set of data

        dictionary : gensim library dictionary object
                A dictionary object by gensim that contains words in the text and its frequency

        Returns
        ------------
        topic : list of tuples
                A list of topics with probabilities of how close the document matchs the topics
    '''
    
    content_bow = dictionary.doc2bow(token_list)
    topic = ldamodel.get_document_topics(content_bow)

    return topic

def get_optimal_cluster_value(df):
    list_of_docs = []
    for index, row in df.iterrows():
        list_of_docs.append(row["Title"] + " " + row["Abstract"])

    max_cluster = int(len(df.index) / 4) #25% of the size of the cluster

    tfidf = TfidfVectorizer(min_df = 3, max_df = 0.95, max_features=8000, stop_words='english')
    text = tfidf.fit_transform(list_of_docs)
    optimal_cluster = find_optimal_clusters(text, max_cluster)
    if optimal_cluster == None:
        optimal_cluster = 1
    return optimal_cluster


def find_optimal_clusters(data, max_k):
    iters = range(1, max_k+1)
    sse = []
    for k in iters:
        sse.append(KMeans(n_clusters=k, random_state=20).fit(data).inertia_)

    fig, ax = plt.subplots(1, 1)
    ax.plot(iters, sse, marker='o')
    ax.set_xlabel('Cluster Centers')
    ax.set_xticks(iters)
    ax.set_xticklabels(iters)
    ax.set_ylabel('SSE')
    ax.set_title('SSE by Cluster Center Plot')
    kn = KneeLocator(iters, sse, curve='convex', direction='decreasing')
    if kn.knee is not None:
        plt.vlines(kn.knee, plt.ylim()[0], plt.ylim()[1], linestyles='dashed')
    return kn.knee


def apply_topic_modelling(df):
    num_of_topics = get_optimal_cluster_value(df)
    print("NUMBER OF TOPICS " + str(num_of_topics))
    text_list = []
    for index, row in df.iterrows():
        tokens = prepare_text_for_lda(row["Title"])
        tokens.extend(prepare_text_for_lda(row["Abstract"]))
        text_list.append(tokens)

    dictionary, corpus = prepare_bow_dictionary(text_list)

    ldamodel = LdaModel(
        corpus, num_topics=num_of_topics, id2word=dictionary, passes=15, random_state=0)

    topics = ldamodel.show_topics(num_topics=-1, formatted=False)
    topics = sorted(topics)
    topic_word_list = []
    topic_dict = {}
    for topic_number, topic in topics:
        list_of_words = []
        for word, value in topic:
            list_of_words.append(word)
        topic_dict[topic_number] = list_of_words

    df.insert(len(df.columns), "Topic", None)
    df.insert(len(df.columns), "Topic Keyword", None)
    df.insert(len(df.columns), "Topic Probability", None)
    for index, row in df.iterrows():
        pub_bow = prepare_text_for_lda(row["Title"])
        pub_bow.extend(prepare_text_for_lda(row["Abstract"]))
        pub_topics = retrieve_topic_for_doc(pub_bow, ldamodel, dictionary)
        topic_keywords = "OUTLIER"
        topic_number = -1
        topic_probablity = 0
        if len(pub_topics) > 0:
            pub_topics.sort(key=lambda x:x[1], reverse=True)
            topic_keywords = topic_dict[pub_topics[0][0]]
            topic_number = pub_topics[0][0]
            topic_probablity = pub_topics[0][1]

        df.at[index, "Topic"] = topic_number
        df.at[index, "Topic Keyword"] = topic_keywords
        df.at[index, "Topic Probability"] = topic_probablity


    return df