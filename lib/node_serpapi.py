class Node:
    def __init__(self, title, year, abstract, cite_id, cite_count, result_id, topic_no, topic, topic_prob):
        self.title = title
        self.year = year
        self.abstract = abstract
        self.cite_id = cite_id
        self.cite_count = cite_count
        self.result_id = result_id
        self.topic_no = topic_no
        self.topic = topic
        self.topic_prob = topic_prob
        self.edge_dict = {}

    def add_edge(self, result_id):
        if result_id in self.edge_dict:
            self.edge_dict[result_id] += 1
        else:
            self.edge_dict[result_id] = 1
        return None

    def to_string(self):
        node_string = "Title: " + self.title + ", Year: " + str(self.year) + ", Abstract: " + str(self.abstract) + "Edge_dict: " + str(self.edge_dict)
        return node_string


# if __name__ == "__main__":
#     node = Node("Test", 2020, "Testing", "Journal", "URL", 23, "URL")
#     node.node_print()