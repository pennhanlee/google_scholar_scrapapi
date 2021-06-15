from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt


def plot_cloud(wordcloud):
    plt.figure(figsize=(40, 30))
    plt.imshow(wordcloud)
    plt.axis("öff")
    return None


def generate_word_cloud(list_of_words, save_path):
    word_cloud = WordCloud(width=3000, height=2000, random_state=1,
                           background_color="grey", colormap="Pastel1",
                           collocations=False, stopwords=STOPWORDS).generate(" ".join(list_of_words))
    word_cloud.to_file(save_path)
    return None


def generate_year_linegraph(cluster, save_path, min_year, max_year):
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
