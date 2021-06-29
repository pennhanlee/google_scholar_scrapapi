import random
import pandas as pd
import gensim

from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import wordnet
import nltk

import spacy
from spacy.lang.en import English


parser = English()
en_stop = set(nltk.corpus.stopwords.words('english'))


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


def get_lemma2(word):
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
    return WordNetLemmatizer().lemmatize(word)


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
    dictionary = gensim.corpora.Dictionary(text_list)
    corpus = [dictionary.doc2bow(text) for text in text_list]
    return dictionary, corpus

def prepare_topics(dataframe, no_topics):
    ''' Analyses the provided dataframe to produce a number of topics as
        indicated by the user

        Parameters
        ------------
        dataframe : pandas DataFrame
                A dataframe containing publication information

        no_topics : int
                The intended number of topics to be produced

        Returns
        ----------
        topics : gensim LDAModel 
                The topics produced from the dataframe publication information

        ldamodel : gensim LDAModel
                The LDAModel produced through training using the provided data from the DataFrame

        dictionary : gensim library dictionary object
                A dictionary object by gensim that contains words in the text and its frequency
    '''

    text_list = []
    for index, row in dataframe.iterrows():
        tokens = prepare_text_for_lda(row["Title"])
        text_list.append(tokens)

    dictionary, corpus = prepare_bow_dictionary(text_list)

    ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics=no_topics, 
                                                id2word=dictionary, passes=15, 
                                                random_state=0)

    topics = ldamodel.print_topics(num_words=4)
    return topics, ldamodel, dictionary

def retrieve_topic_for_doc(doc, ldamodel, dictionary):
    ''' Analyses the documents and returns the probabilities for the topic that a document belongs to

        Parameters
        ------------
        doc : str
            A string of words

        ldamodel : gensim LDAModel
                The LDAModel produced through training with a set of data

        dictionary : gensim library dictionary object
                A dictionary object by gensim that contains words in the text and its frequency

        Returns
        ------------
        topic : list of tuples
                A list of topics with probabilities of how close the document matchs the topics
    '''
    
    content = prepare_text_for_lda(doc)
    content_bow = dictionary.doc2bow(new_doc)
    topic = ldamodel.get_document_topics(content_bow)

    return topic

if __name__ == "__main__":
    FILEPATH = "C:/Users/luciu/Desktop/NUS Lecture Notes/Y2S2/Summer Internship/bibicite/gscholar/data/16-06-2021_1444_Natural Language Processing/networks neural/networks neural.xlsx"
    NUM_TOPICS = 5
    cluster_df = pd.read_excel(FILEPATH)
    text_list = []
    for index, row in cluster_df.iterrows():
        tokens = prepare_text_for_lda(row["Title"])
        text_list.append(tokens)

    dictionary, corpus = prepare_bow_dictionary(text_list)

    ldamodel = gensim.models.ldamodel.LdaModel(
        corpus, num_topics=NUM_TOPICS, id2word=dictionary, passes=15, random_state=0)

    topics = ldamodel.print_topics(num_words = 4)
    print("\n")
    for topic in topics:
        print(topic)

    new_doc = cluster_df.iloc[3]["Title"]
    new_doc = prepare_text_for_lda(new_doc)
    new_doc_bow = dictionary.doc2bow(new_doc)
    print("\n")
    print(new_doc)
    print(new_doc_bow)
    print(ldamodel.get_document_topics(new_doc_bow))
