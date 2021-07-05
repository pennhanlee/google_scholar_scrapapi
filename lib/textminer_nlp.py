import math

from nltk import sent_tokenize, word_tokenize, PorterStemmer, pos_tag
from nltk.corpus import stopwords, wordnet
from nltk import RegexpTokenizer
from nltk import WordNetLemmatizer

TOKENIZER = RegexpTokenizer(r"\w+")


def _merge_cluster_abstracts(cluster):
    ''' Merge all publication abstracts of a cluster into a single string
        for easy string processing

        Parameters
        ------------
        cluster : pandas DataFrame
                    cluster pandas DataFrame containing publication information

        Returns
        -----------
        merged_text : str
                    a string of all abstracts of publications in a cluster
    '''

    merged_text = ""
    for index, row in cluster.iterrows():
        text = row["Abstract"]
        text = text.replace("...", ".")
        title = row["Title"]
        merged_text = merged_text + title + text
    return merged_text


def _create_freq_matrix(sentences):
    ''' Creates a word frequency matrix after processing each
        word by removing stopwords and stemming remaining words for
        every sentence provided.


        Parameters
        ------------
        sentences : str
                    sentence of words to be processed into a frequency matrix

        Returns
        ------------
        freq_matrix : dict of dict
                    A dictionary of sentence as keys and 
                    dictionary (of words as keys and frequency as value) as value
    '''

    freq_matrix = {}
    stop_words = set(stopwords.words("english"))
    port_stemmer = PorterStemmer()

    for sent in sentences:
        freq_table = {}
        words = TOKENIZER.tokenize(sent) 
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
    ''' Creates a term frequency matrix which is defined by
        word_count / total_no_of_words. 

        Parameters
        ------------
        freq_matrix : dict
                    A dictionary of words as keys and frequency as values

        Returns
        -----------
        tf_matrix : dict of dict
                    A dictionary of sentence as keys and dictionary (of word as key and term frequency as value) as value
    '''

    tf_matrix = {}
    for sent, f_table in freq_matrix.items():
        tf_table = {}
        no_of_words_in_sent = len(f_table)

        for word, count in f_table.items():
            tf_table[word] = count / no_of_words_in_sent
        tf_matrix[sent] = tf_table

    return tf_matrix

def _create_doc_per_words(freq_matrix):   #preparatory table for IDF
    ''' Creates a table of words and frequency of the words
        occuring in the whole document

        Parameters
        -------------
        freq_matrix : dict
                    A dictionary of sentence and wordfrequency dictionary

        Returns
        ------------
        word_per_doc_table : dict
                    A dictionary of words as keys and frequency as values

    ''' 
    word_per_doc_table = {}

    for sent, f_table in freq_matrix.items():
        for word, count in f_table.items():
            if word in word_per_doc_table:
                word_per_doc_table[word] += 1
            else:
                word_per_doc_table[word] = 1
    
    return word_per_doc_table

def _create_idf_matrix(freq_matrix, count_doc_per_words, total_documents):
    ''' Creates an inverse document frequency matrix that tracks the inverse 
        document frequency of a word, which is defined by log(total_document / number of documents containing the word)

        Parameters
        ------------
        freq_matrix : dict
                    A dictionary of sentence as key and word frequency dictionary as value

        count_doc_per_words : dict
                    A dictionary of words as keys and frequency as values for the whole document

        total_documents : int
                    The total number of documents present in analysis

        Returns
        ----------
        idf_matrix : dict of dict
                    A dictionary of sentence as key and dictionary (of word as keys and idf as value) as value
    '''

    idf_matrix = {}

    for sent, f_table in freq_matrix.items():
        idf_table = {}
        
        for word in f_table.keys():
            idf_table[word] = math.log10(total_documents / float(count_doc_per_words[word]))

        
        idf_matrix[sent] = idf_table

    return idf_matrix

def _create_tfidf_matrix(tf_matrix, idf_matrix):
    ''' Generates a tfidf matrix that tracks the tf_idf score for each word in the sentence
        tf_idf is defined as term frequency * inverse document frequency

        Parameters
        ------------
        tf_matrix : dict of dict
                    A dictionary of sentence as keys and dictionary (of word as key and term frequency as value) as value

        idf_matrix : dict of dict
                    A dictionary of sentence as key and dictionary (of word as keys and idf as value) as value

        Returns
        ------------
        tf_idf_matrix : dict of dict
                    A dictionary of sentence as key and dictionary (of word as key and tf_idf as value) as value
    '''

    tf_idf_matrix = {}
    for (sent1, f_table1), (sent2, f_table2) in zip(tf_matrix.items(), idf_matrix.items()):
        tf_idf_table = {}
        for (word1, value1), (word2, value2) in zip(f_table1.items(), f_table2.items()):  #word1 and word2 are the same keys
            tf_idf_table[word1] = float(value1 * value2)

        tf_idf_matrix[sent1] = tf_idf_table
    
    return tf_idf_matrix

def _score_sentences(tf_idf_matrix):
    ''' Scores each sentence using the sum of tf_idf value of each word in the sentence

        Parameters
        ------------
        tf_idf_matrix : dict of dict
                    A dictionary of sentence as key and dictionary (of word as key and tf_idf as value) as value

        sentencevalue : dict
                    A dictionary of sentence as key and summation of tf_idf value of each word in the sentence as value
    '''

    sentencevalue = {}

    for sent, f_table in tf_idf_matrix.items():
        total_score_per_sentence = 0
        no_of_words_in_sentence = len(f_table)
        
        for word, score in f_table.items():
            total_score_per_sentence += score

        sentencevalue[sent] = total_score_per_sentence / no_of_words_in_sentence
    
    return sentencevalue

def _find_average_score(sentencevalue):
    ''' Get the average score of all sentences
        
        Parameters
        ------------
        sentencevalue : dict 
                    A dictionary of sentence as key and summation of tf_idf value of each word in the sentence as value

        Returns
        -----------
        average : float
                    The average sentence score in the whole dictionary
    '''

    sum_values = 0
    for entry in sentencevalue:
        sum_values += sentencevalue[entry]
    
    average = (sum_values / len(sentencevalue))

    return average

def _generate_summary(sentences, sentencevalue, threshold):
    ''' Generates a summary by selecting sentences which sentence value exceeds the threshold
        which is defined by (threshold * average value)

        Parameters
        ------------
        sentences : list
                List of strings as sentences

        sentencevalue : dict
                A dictionary of sentence as key and summation of tf_idf value of each word in the sentence as value

        threshold : float
                A value provided as a multipler to adjust the threshold which is defined by
                (threshold * average sentence score)

        Returns
        ------------
        summary : str
                A string of sentences consisting of sentences that fulfill the threshold value

    '''

    sentence_count = 0
    summary = ""

    for sentence in sentences:
        if sentence[:15] in sentencevalue and sentencevalue[sentence[:15]] >= (threshold):
            summary += " " + sentence
            sentence_count += 1

    return summary

def create_extractive_summary(cluster, threshold):
    ''' Creates a extractive summary using TF-IDF to score each sentence, then picking 
        out sentences that fulfill the threshold.

        Parameters
        ------------
        cluster : pandas DataFrame
                cluster dataframe containing publication information

        threshold : float
                A value provided as a multipler to adjust the threshold which is defined by
                (threshold * average sentence score)

        Returns
        -----------
        summary : str
                A string of sentences consisting of sentences that fulfill the threshold value
    '''
    
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

def get_wordnet_pos(word) :
    ''' Maps Parts_of_speech tag to first character that lemmatize() accepts

        Parameters
        ------------
        word: str
                The word to lemmatize

        Returns
        ------------
        word_tag: wordnet POS object
                The tag of the word, defaults to Noun if POS not found. 
    '''
    tag = pos_tag([word])
    tag_first = tag[0][1][0].upper()
    tag_dict = {"J": wordnet.ADJ,
                "N": wordnet.NOUN,
                "V": wordnet.VERB,
                "R": wordnet.ADV}

    word_tag = tag_dict.get(tag_first, wordnet.NOUN)

    return word_tag

def create_tf_table(df, *args):
    tf_table = {}
    list_of_words = []
    stop_words = set(stopwords.words("english"))
    # port_stemmer = PorterStemmer()
    lemmatizer = WordNetLemmatizer()
    for index, row in df.iterrows():
        for arg in args:
            words = TOKENIZER.tokenize(row[arg]) 
            list_of_words.extend(words)

    for word in list_of_words:            #Get the frequency table
        word = word.lower()
        if word in stop_words:
            continue

        word = lemmatizer.lemmatize(word, get_wordnet_pos(word))    #lemmatize each word to calculate a more acc freq
        
        if word in tf_table:
            tf_table[word] += 1
        else:
            tf_table[word] = 1

    num_of_words_in_cluster = sum(tf_table.values())   
    for key, value in tf_table.items():          #convert to term frequency
        tf_table[key] = (value / num_of_words_in_cluster)

    return tf_table

def create_idf_table(freq_tables, total_doc_count):
    docs_per_word_table = {}
    number_of_doc = 0
    for table in freq_tables:
        for word, tf_value in table.items():
            if word in docs_per_word_table:
                docs_per_word_table[word] += 1
            else:
                docs_per_word_table[word] = 1
    idf_table = {}
    for word, doc_count in docs_per_word_table.items():
        idf_table[word] = math.log10(total_doc_count / float(doc_count))
    return idf_table

def create_tf_idf_table(tf_table, idf_table):
    tf_idf_table = {}
    for word, tf_value in tf_table.items():
        idf_value = idf_table[word]
        tf_idf_table[word] = float(tf_value * idf_value)
    return tf_idf_table


def get_word_list(cluster, *args):
    words = []
    filtered_words = []
    stop_words = set(stopwords.words("english"))
    for index, row in cluster.iterrows():
        for arg in args:
            words = words + word_tokenize(row[arg].lower())
    for word in words:
        if word in stop_words:
            continue
        else:
            filtered_words.append(word)
    return filtered_words

def create_cluster_names(clusters, df, num_words, *args):
    alldata_df = df
    list_of_tf_table = []
    cluster_names = []
    total_doc_count = len(df.index)
    for x in range(0, len(clusters)):
        cluster = clusters[x]
        cluster_df = alldata_df[alldata_df["Title"].isin(cluster)]
        tf_table = create_tf_table(cluster_df, "Title", "Abstract")
        list_of_tf_table.append(tf_table)

    idf_table = create_idf_table(list_of_tf_table, total_doc_count)
    for tf_table in list_of_tf_table:
        tf_idf_table = create_tf_idf_table(tf_table, idf_table)
        tf_idf_ordered_list = sorted(tf_idf_table.items(), key = lambda item:item[1])
        cluster_name = " ".join([tf_idf_ordered_list[x][0] for x in range(0, num_words)])
        cluster_names.append(cluster_name)


    return cluster_names
