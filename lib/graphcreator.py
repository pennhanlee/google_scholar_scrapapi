from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt


def plot_cloud(wordcloud):
    ''' Displays a created wordcloud in a window of 30 by 40cm

    Parameters
    ------------
    wordcloud: wordcloud object

    Returns
    -----------
    None
    '''

    plt.figure(figsize=(40, 30))
    plt.imshow(wordcloud)
    plt.axis("öff")
    return None


def generate_word_cloud(list_of_words, save_path):
    ''' Generates a word cloud from a list of words

    Parameters
    -----------
    list_of_words : list
                list of words to be analysed into a word cloud
    
    save_path: str
                the path to save the word cloud image file

    Returns
    -----------
    None
    '''

    word_cloud = WordCloud(width=3000, height=2000, random_state=1,
                           background_color="grey", colormap="Pastel1",
                           collocations=False, stopwords=STOPWORDS).generate(" ".join(list_of_words))
    word_cloud.to_file(save_path)
    return None


def generate_year_linegraph(cluster, save_path, min_year, max_year):
    ''' Generates a linegraph of Number of Publications by Years for the cluster

    Parameters
    -----------
    cluster : pandas DataFrame
                the cluster DataFrame that contains publication info of that cluster
    
    save_path: str
                the path to save the linegraph image file

    min_year : int
                the earliest year to limit the period of publication years

    max_year : int
                the latest year to limit the period of publication years

    Returns
    ----------
    tuple: (year_range, papers_published)
    '''

    # cluster = cluster["Year"].value_counts().sort_index(ascending=True)
    year_range = [x for x in range(min_year, max_year + 1)]
    papers_published = []
    counter = 0
    for x in range(0, (max_year - min_year + 1)):
        counter = counter + len(cluster[cluster["Year"] == year_range[x]])
        papers_published.append(counter)

    plt.plot(year_range, papers_published, color="red")
    plt.xlabel("Years")
    plt.ylabel("Culmulative Papers Published")
    plt.grid(True)
    plt.savefig(save_path)
    plt.close()
    return (year_range, papers_published)

def generate_summary_linegraph(linegraph_data, save_path):
    ''' Generates a linegraph of Number of publications by Years for all clusters in 1 graph

        Parameters
        ------------
        linegraph_data : dict
                    key, value: cluster name, cluster linegraph data

        save_path: str
                the path to save the linegraph image file 

        Returns
        ----------
        None
    '''

    for key in linegraph_data.keys():
        year_distribution = linegraph_data[key][0]
        paper_distribution = linegraph_data[key][1]
        plt.plot(year_distribution, paper_distribution, label=key)
    plt.xlabel("Years")
    plt.ylabel("Culmulative Papers Published")
    plt.grid(True)
    legend = plt.legend(bbox_to_anchor=(1.05, 1.0), loc="upper left")
    plt.savefig(save_path,
                format='png',
                bbox_extra_artists=(legend,),
                bbox_inches="tight")
    plt.close()
    return None

def generate_summary_linegraph(df, save_path):
    return 0