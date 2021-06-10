class Node:
    def __init__(self, title, year, abstract, venue, citedby_url, no_of_cites, pub_url):
        self.title = title
        self.year = year
        self.abstract = abstract
        self.venue = venue
        self.citedby_url = citedby_url
        self.no_of_cites = no_of_cites
        self.pub_url = pub_url
        self.node_hash = hash(pub_url)
        self.edge_dict = {}

    def add_edge(node_hash):
        if node in self.edge_dict:
            self.edge_dict[node_hash] += 1
        else:
            self.edge_dict[node_hash] = 1
        return None

    def node_print(self):
        print("Title: " + self.title 
                + ", Year: " + str(self.year) 
                + ", Abstract: " + self.abstract)
        print("Edge_dict: " + str(self.edge_dict))
        return None


if __name__ == "__main__":
    node = Node("Test", 2020, "Testing", "Journal", "URL", 23, "URL")
    node.node_print()