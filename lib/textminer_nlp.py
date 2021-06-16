import math

from nltk import sent_tokenize, word_tokenize, PorterStemmer
from nltk.corpus import stopwords


def _merge_cluster_abstracts(cluster):
    merged_text = ""
    for index, row in cluster.iterrows():
        text = row["Abstract"]
        text = text.replace("...", ".")
        merged_text = merged_text + text
    return merged_text


def _create_freq_matrix(sentences):
    freq_matrix = {}
    stop_words = set(stopwords.words("english"))
    port_stemmer = PorterStemmer()

    for sent in sentences:
        freq_table = {}
        words = word_tokenize(sent)
        for word in words:
            word = word.lower()
            word = port_stemmer.stem(word)    #stem each word to calculate a more acc freq
            if word in stop_words:
                continue

            if word in freq_table:
                freq_table[word] += 1
            else:
                freq_table[word] = 1
        freq_matrix[sent[:15]] = freq_table   #Take the first 15 chars of sentence as the key

    return freq_matrix

def _create_tf_matrix(freq_matrix):   #term frequency
    tf_matrix = {}
    for sent, f_table in freq_matrix.items():
        tf_table = {}
        no_of_words_in_sent = len(f_table)

        for word, count in f_table.items():
            tf_table[word] = count / no_of_words_in_sent
        tf_matrix[sent] = tf_table

    return tf_matrix

def _create_doc_per_words(freq_matrix):   #preparatory table for IDF 
    word_per_doc_table = {}

    for sent, f_table in freq_matrix.items():
        for word, count in f_table.items():
            if word in word_per_doc_table:
                word_per_doc_table[word] += 1
            else:
                word_per_doc_table[word] = 1
    
    return word_per_doc_table

def _create_idf_matrix(freq_matrix, count_doc_per_words, total_documents):
    idf_matrix = {}

    for sent, f_table in freq_matrix.items():
        idf_table = {}
        
        for word in f_table.keys():
            idf_table[word] = math.log10(total_documents / float(count_doc_per_words[word]))

        
        idf_matrix[sent] = idf_table

    return idf_matrix

def _create_tfidf_matrix(tf_matrix, idf_matrix):
    tf_idf_matrix = {}
    for (sent1, f_table1), (sent2, f_table2) in zip(tf_matrix.items(), idf_matrix.items()):
        tf_idf_table = {}
        for (word1, value1), (word2, value2) in zip(f_table1.items(), f_table2.items()):  #word1 and word2 are the same keys
            tf_idf_table[word1] = float(value1 * value2)

        tf_idf_matrix[sent1] = tf_idf_table
    
    return tf_idf_matrix

def _score_sentences(tf_idf_matrix):
    sentencevalue = {}

    for sent, f_table in tf_idf_matrix.items():
        total_score_per_sentence = 0
        no_of_words_in_sentence = len(f_table)
        
        for word, score in f_table.items():
            total_score_per_sentence += score

        sentencevalue[sent] = total_score_per_sentence / no_of_words_in_sentence
    
    return sentencevalue

def _find_average_score(sentencevalue):
    sum_values = 0
    for entry in sentencevalue:
        sum_values += sentencevalue[entry]
    
    average = (sum_values / len(sentencevalue))

    return average

def _generate_summary(sentences, sentencevalue, threshold):
    sentence_count = 0
    summary = ""

    for sentence in sentences:
        if sentence[:15] in sentencevalue and sentencevalue[sentence[:15]] >= (threshold):
            summary += " " + sentence
            sentence_count += 1

    return summary

def create_extractive_summary(cluster, threshold):
    merged_text = _merge_cluster_abstracts(cluster)
    sentences = sent_tokenize(merged_text)
    total_documents = len(sentences)

    freq_matrix = _create_freq_matrix(sentences)
    tf_matrix = _create_tf_matrix(freq_matrix)
    count_doc_per_words = _create_doc_per_words(freq_matrix)
    idf_matrix = _create_idf_matrix(freq_matrix, count_doc_per_words, total_documents)
    tf_idf_matrix = _create_tfidf_matrix(tf_matrix, idf_matrix)
    sentence_scores = _score_sentences(tf_idf_matrix)
    average = _find_average_score(sentence_scores)

    summary = _generate_summary(sentences, sentence_scores, (threshold * average))

    return summary