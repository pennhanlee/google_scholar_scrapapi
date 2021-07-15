class Node:
    ''' A node object is used to keep track of the publication information. It also has a dictionary to  maintain a record
        of the bibliographic couples and its weight of connection

        Attributes
        ------------
        title : str
        year : int
        abstract : str
        cite_id : str
        cite_count : int
        cite_count : int
        result_id : str
        topic_no : str, optional
        topic : str, optional
        topic_prob: str, optional

        Methods
        ----------
        add_edge(result_id)

        to_string()
    '''

    def __init__(self, title, year, abstract, authors, author_id, hyperlink, cite_id, cite_count, result_id, pub_type, citing_pub_id="", cites="", topic_no=None, topic=None, topic_prob=None):
        self.title = title
        self.year = year
        self.abstract = abstract
        self.authors = authors
        self.author_id = author_id
        self.hyperlink = hyperlink
        self.cite_id = cite_id
        self.cite_count = cite_count
        self.result_id = result_id
        self.type = pub_type
        self.citing_pub_id = citing_pub_id
        self.cites = cites
        self.topic_no = topic_no
        self.topic = topic
        self.topic_prob = topic_prob
        
        self.edge_dict = {}

    def add_edge(self, result_id):
        ''' Adds a record to the edge dictionary of this node

            Parameters
            -----------
            result_id: str
                    result_id as a unique key for the dictionary

            Returns
            ----------
            None
        '''
        
        if result_id in self.edge_dict:
            self.edge_dict[result_id] += 1
        else:
            self.edge_dict[result_id] = 1
        return None

    def to_string(self):
        ''' Prints a string statement of the Node with some of its attributes

            Parameters
            -----------
            None

            Returns
            ----------
            node_string : str
                    a string of the Node with some of its attributes
        '''

        node_string = "Title: " + self.title + ", Year: " + str(self.year) + ", Abstract: " + str(self.abstract) + "Edge_dict: " + str(self.edge_dict)
        return node_string


# if __name__ == "__main__":
#     node = Node("Test", 2020, "Testing", "Journal", "URL", 23, "URL")
#     node.node_print()