import tkinter as tk
import tkinter.ttk as ttk
from tkinter.filedialog import askopenfile, askdirectory
import os.path
from os import path
import time
import pandas as pd

import serpg
import analysis
import lib.topic_model as topic_model
import lib.textminer as textminer
import lib.textminer_nlp as textminer_nlp

SIDEBAR_LIGHTGREY = "#d4d4d4"
MAINWINDOW_WHITE = "#ffffff"
ERROR_COLOUR = "#fa8072"


class Application(tk.Frame):
    ''' Class: Application
        -------------------
        This is a tkinter class to instantiate a GUI instance for Bib Coupling programme. 

        Attributes
        -------------------


        
        Methods
        -------------------
        create_frames: create frames that will hold widgets for GUI

        create_sidebar: create sidebar widgets in the frame

        create_serpapi_btn: create button to trigger a set of widget creation

        create_cite_analysis_btn: create button to trigger a set of widget creation

        create_updates_window: create updatewindow as a frame

        update_output_message: updates the update window with a new message

        create_mainframe_analysis: creates the widgets for analysis in the mainframe

        create_mainframe_data: creates the widgets for data retrieval in the mainframe

        get_file_button: create button to open file explorer for a file

        get_folder_button: create button to open file explorer for a folder

        get_analysis_button: create button that will trigger analysis script

        retrieve_info_button: create button that will trigger data retrieval

        retrieve_file: opens file explorer for a file

        retrieve_folder: opens file explorer for a folder

        analyse_data: initiates analysis script

        get_google_data: initiates data retrieval script
    '''
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.master.title("Citation Analysis")
        canvas = tk.Canvas(self.master, width=800, height=500)
        canvas.pack()
        self.sidebar, self.main_window, self.updates_window, self.progress_bar = self.create_frames()
        self.style = ttk.Style()
        self.create_sidebar(self.sidebar, self.main_window)
        self.create_updates_window(self.updates_window)
        self.alldata_path = ""
        self.main_pub_path = ""
        self.savefolder_path = ""

    def create_frames(self):
        ''' creates frames: Sidebar, UpdateWindow, MainWindow, Progressbar

        Parameters
        -----------
        None

        Returns
        -----------
        sidebar: Frame
                The frame that has the attributes for the sidebar

        updates_window: Frame
                The frame that has the attributes for the updates window

        main_window: Frame
                The frame that has the attributes for the main window

        progress: ttk.Progressbar
                The ttk.Progressbar object
        '''

        sidebar = tk.Frame(self.master, bg=SIDEBAR_LIGHTGREY)
        sidebar.place(relx=0, rely=0.5, relwidth=0.25, relheight=1, anchor="w")

        updates_window = tk.Frame(self.master, bg=MAINWINDOW_WHITE)
        updates_window.place(relx=1, rely=0.0, relwidth=0.75, relheight=0.15, anchor="ne")
        
        main_window = tk.Frame(self.master, bg=MAINWINDOW_WHITE)
        main_window.place(relx=1, rely=0.15, relwidth=0.75, relheight=0.75, anchor="ne")

        progress = tk.ttk.Progressbar(self.master, orient='horizontal', mode='determinate')
        progress.place(relx=1, rely=0.90, relwidth=0.75, relheight=0.10, anchor="ne")

        return sidebar, main_window, updates_window, progress

    def create_sidebar(self, frame, mainwindow):
        ''' Creates the sidebar widgets

        Parameters
        ------------
        None

        Returns
        -------------
        None

        '''

        inst_text = "What would you \n like to do?"
        instructions = tk.Label(frame, text=inst_text, bg=SIDEBAR_LIGHTGREY)
        instructions.place(relx=0.2, rely=0.1, relwidth=0.5, relheight=0.3)
        self.create_serpapi_btn(frame, mainwindow)
        self.create_cite_analysis_btn(frame, mainwindow)

    def create_serpapi_btn(self, frame, mainwindow):
        ''' Creates the button that will trigger the creation of widgets for data retrieval in the
        main widow

        Parameters
        ------------
        None

        Returns
        -------------
        None

        '''

        get_folder = tk.StringVar()
        browse_btn = tk.Button(master=frame, textvariable=get_folder,
                               command=lambda: self.create_mainframe_data(mainwindow))
        get_folder.set("Receive Data")
        browse_btn.place(relx=0.2, rely=0.5, relwidth=0.5, relheight=0.1)

    def create_cite_analysis_btn(self, frame, mainwindow):
        ''' Creates the button that will trigger the creation of widgets for data analysis in the
        main window

        Parameters
        ------------
        None

        Returns
        -------------
        None

        '''

        get_file = tk.StringVar()
        browse_file = tk.Button(master=frame, textvariable=get_file,
                                command=lambda: self.create_mainframe_analysis(
                                    mainwindow)
                                )
        get_file.set("Start Analysis")
        browse_file.place(relx=0.2, rely=0.7, relwidth=0.5, relheight=0.1)

    def create_updates_window(self, frame):
        ''' Creates the button that will trigger the creation of widgets for Updates Window

        Parameters
        ------------
        None

        Returns
        -------------
        None

        '''

        text = tk.Text(frame)
        text.place(relx=0.0, rely=0.05, relwidth=1, relheight=0.95)
        frame.textbox = [text]
        text.insert("end","Please select what you would like to do \n")
        return 0
    
    def update_output_message(self, message):
        ''' Updates the update window with a new message

        Parameters
        ------------
        message: str
                The message that will be updated and shown on update window

        Returns
        -------------
        None

        '''
        for text in self.updates_window.textbox:
            text.delete("1.0", tk.END)
            text.insert(tk.END, message)
        return 0

    def create_mainframe_analysis(self, frame):
        ''' Creates the mainframe widgets for data analysis

        Parameters
        ------------
        None

        Returns
        -------------
        None

        '''

        for widget in frame.winfo_children():
            widget.destroy()

        reg_valid_number = frame.register(is_valid_number)  

        self.update_output_message("Hello")

        all_data_file_label = tk.Label(frame, text="Please provide filepath to alldata.xlsx", bg=MAINWINDOW_WHITE)
        all_data_file_label.place(relx=0.1, rely=0.10, relwidth=0.6, relheight=0.05)
        all_data_file = tk.Entry(master=frame, bg=SIDEBAR_LIGHTGREY)
        all_data_file.place(relx=0.1, rely=0.15, relwidth=0.6, relheight=0.05)
        all_data_btn = self.get_file_button(frame, all_data_file)
        all_data_btn.place(relx=0.75, rely=0.15, relwidth=0.1, relheight=0.05)

        main_data_label = tk.Label(
            frame, text="Please provide filepath to main_pubs.xlsx", bg=MAINWINDOW_WHITE)
        main_data_label.place(relx=0.1, rely=0.25, relwidth=0.6, relheight=0.05)
        main_data_file = tk.Entry(master=frame, bg=SIDEBAR_LIGHTGREY)
        main_data_file.place(relx=0.1, rely=0.30, relwidth=0.6, relheight=0.05)
        main_data_btn = self.get_file_button(frame, main_data_file)
        main_data_btn.place(relx=0.75, rely=0.30, relwidth=0.1, relheight=0.05)

        save_folder_label = tk.Label(
            frame, text="Please provide path to folder to save the documents", bg=MAINWINDOW_WHITE)
        save_folder_label.place(relx=0.1, rely=0.40, relwidth=0.6, relheight=0.05)
        save_folder = tk.Entry(master=frame, bg=SIDEBAR_LIGHTGREY)
        save_folder.place(relx=0.1, rely=0.45, relwidth=0.6, relheight=0.05)
        save_folder_btn = self.get_folder_button(frame, save_folder)
        save_folder_btn.place(relx=0.75, rely=0.45, relwidth=0.1, relheight=0.05)

        min_year_label = tk.Label(
            frame, text="Please indicate \nearliest year eg. 2010", bg=MAINWINDOW_WHITE)
        min_year_label.place(relx=0.1, rely=0.55, relwidth=0.2, relheight=0.1)
        min_year = tk.Entry(master=frame, bg=SIDEBAR_LIGHTGREY)
        min_year.config(validate="key", validatecommand=(reg_valid_number, "%P"))
        min_year.place(relx=0.1, rely=0.65, relwidth=0.2, relheight=0.05)

        max_year_label = tk.Label(
            frame, text="Please indicate \nlatest year eg. 2020", bg=MAINWINDOW_WHITE)
        max_year_label.place(relx=0.5, rely=0.55, relwidth=0.2, relheight=0.1)
        max_year = tk.Entry(master=frame, bg=SIDEBAR_LIGHTGREY)
        max_year.config(validate="key", validatecommand=(reg_valid_number, "%P"))
        max_year.place(relx=0.5, rely=0.65, relwidth=0.2, relheight=0.05)

        start_analysis = self.start_analysis_button(frame, all_data_file, main_data_file,
                                                    save_folder, min_year, max_year)
        start_analysis.place(relx=0.1, rely=0.75, relwidth=0.6, relheight=0.1)

        return 0

    def create_mainframe_data(self, frame):
        ''' Creates the mainframe widgets for data retrieval

        Parameters
        ------------
        None

        Returns
        -------------
        None

        '''

        for widget in frame.winfo_children():
            widget.destroy()

        reg_valid_number = frame.register(is_valid_number)

        self.update_output_message("Hello")

        topic_label = tk.Label(
            frame, text="Please indicate topic to be researched on", bg=MAINWINDOW_WHITE)
        topic_label.place(relx=0.1, rely=0.05, relwidth=0.6, relheight=0.05)
        topic = tk.Entry(master=frame, bg=SIDEBAR_LIGHTGREY)
        topic.place(relx=0.1, rely=0.1, relwidth=0.6, relheight=0.05)

        key_label = tk.Label(frame, text="Please provide the API key for SERP API", bg=MAINWINDOW_WHITE)
        key_label.place(relx=0.1, rely=0.15, relwidth=0.6, relheight=0.05)
        key = tk.Entry(master=frame, bg=SIDEBAR_LIGHTGREY)
        key.place(relx=0.1, rely=0.20, relwidth=0.6, relheight=0.05)

        min_year_label = tk.Label(
            frame, text="Please indicate \nearliest year eg. 2010", bg=MAINWINDOW_WHITE)
        min_year_label.place(relx=0.1, rely=0.30, relwidth=0.2, relheight=0.1)
        min_year = tk.Entry(master=frame, bg=SIDEBAR_LIGHTGREY)
        min_year.config(validate="key", validatecommand=(reg_valid_number, '%P'))
        min_year.place(relx=0.1, rely=0.40, relwidth=0.2, relheight=0.05)

        max_year_label = tk.Label(
            frame, text="Please indicate \nlatest year eg. 2020", bg=MAINWINDOW_WHITE)
        max_year_label.place(relx=0.5, rely=0.30, relwidth=0.2, relheight=0.1)
        max_year = tk.Entry(master=frame, bg=SIDEBAR_LIGHTGREY)
        max_year.config(validate="key", validatecommand=(reg_valid_number, "%P"))
        max_year.place(relx=0.5, rely=0.40, relwidth=0.2, relheight=0.05)

        root_doc_label = tk.Label(
            frame, text="Please indicate the number \nof root documents eg. 20", bg=MAINWINDOW_WHITE)
        root_doc_label.place(relx=0.0, rely=0.45, relwidth=0.4, relheight=0.1)
        root_doc = tk.Entry(master=frame, bg=SIDEBAR_LIGHTGREY)
        root_doc.config(validate="key", validatecommand=(reg_valid_number, '%P'))
        root_doc.place(relx=0.1, rely=0.55, relwidth=0.2, relheight=0.05)

        cite_doc_label = tk.Label(
            frame, text="Please indicate the number of citing \ndocuments per root document eg. 20", bg=MAINWINDOW_WHITE)
        cite_doc_label.place(relx=0.4, rely=0.45, relwidth=0.4, relheight=0.1)
        cite_doc = tk.Entry(master=frame, bg=SIDEBAR_LIGHTGREY)
        cite_doc.config(validate="key", validatecommand=(reg_valid_number, '%P'))
        cite_doc.place(relx=0.5, rely=0.55, relwidth=0.2, relheight=0.05)

        save_folder_label = tk.Label(
            frame, text="Please provide path to folder to save the documents", bg=MAINWINDOW_WHITE)
        save_folder_label.place(relx=0.1, rely=0.65, relwidth=0.65, relheight=0.05)
        save_folder = tk.Entry(master=frame, bg=SIDEBAR_LIGHTGREY)
        save_folder.place(relx=0.1, rely=0.70, relwidth=0.6, relheight=0.05)
        save_folder_btn = self.get_folder_button(frame, save_folder)
        save_folder_btn.place(relx=0.75, rely=0.70,relwidth=0.1, relheight=0.05)

        retrieve_info = self.retrieve_info_button(frame, save_folder, topic, key, min_year, max_year, root_doc, cite_doc)
        retrieve_info.place(relx=0.1, rely=0.85, relwidth=0.6, relheight=0.1)

        return 0

    def get_file_button(self, frame, entry):
        ''' Creates the button that will trigger the opening of a file explorer for a file location

        Parameters
        ------------
        entry: widget
                The entry widget that will store the file path

        Returns
        -------------
        btn: button widget

        '''

        btn = tk.Button(master=frame, text="Open",
                        command=lambda: self.retrieve_file(frame, entry))
        return btn

    def get_folder_button(self, frame, entry):
        ''' Creates the button that will trigger the opening of a file explorer for a folder location

        Parameters
        ------------
        entry: widget
                The entry widget that will store the folder path

        Returns
        -------------
        btn: button widget

        '''

        btn = tk.Button(master=frame, text="Open",
                        command=lambda: self.retrieve_folder(frame, entry))
        return btn

    def start_analysis_button(self, frame, alldata_path, mainpubs_path, save_path, min_year, max_year):
        '''Creates a button that will trigger the data analysis

        Parameters
        -----------
        alldata_path: str
                the path to the alldata.xlsx file

        mainpubs_path: str
                the path to the mainpubs.xlsx file

        savepath: str
                the path to the folder to save this cluster

        min_year : str
                the earliest year to limit the period of publication retrieval

        max_year : str
                the latest year to limit the period of publication retrieval


        Returns
        -----------
        btn: button widget

        '''

        btn = btn = tk.Button(master=frame, text="Start Analysis",
                              command=lambda: self.analyse_data(alldata_path, mainpubs_path,
                                                                save_path, min_year, 
                                                                max_year))
        return btn

    def retrieve_info_button(self, frame, savepath, topic, key, min_year, max_year, root_doc, cite_doc):
        '''Creates a button that will triggers the data analysis

        Parameters
        -----------
        savepath: str
                the path to the folder to save the retrieved data
        
        topic : str
                the topic of interest

        key : str
                    the api key to connect SERPAPI successfully

        min_year : int
                    the earliest year to limit the period of publication retrieval

        max_year : int
                    the latest year to limit the period of publication retrieval

        root_doc : int
                    the number of publications wanted

        cite_doc : int
                    the number of citing publications wanted

        Returns
        -----------
        btn: button widget
        
        '''

        btn = btn = tk.Button(master=frame, text="Retrieve Info",
                              command=lambda: self.get_google_data(savepath, topic, key,
                                                                   min_year, max_year,
                                                                   root_doc, cite_doc))
        return btn

    def retrieve_file(self, frame, entry):
        ''' Opens a file explorer to retrieve a file path

        Parameters
        -----------
        entry: widget
                The entry widget that will store the file path
        
        Returns
        ---------
        file: str
                The file path
        '''

        entry.config({"background": SIDEBAR_LIGHTGREY})
        file = askopenfile(parent=frame, title="Open file")
        entry.delete(0, tk.END)
        entry.insert(tk.END, file.name)
        return file

    def retrieve_folder(self, frame, entry):
        ''' Opens a file explorer to retrieve a folder path

        Parameters
        -----------
        entry: widget
                The entry widget that will store the folder path
        
        Returns
        ---------
        file: str
                The folder path
        '''

        entry.config({"background": SIDEBAR_LIGHTGREY})
        folder = askdirectory(parent=frame, title="Open folder")
        entry.delete(0, tk.END)
        entry.insert(tk.END, folder)
        return folder

    def analyse_data(self, alldata_path, mainpubs_path, save_path, min_year, max_year):
        ''' Function that will initiate the analysis of data. This function will execute
            input validation too.

            Parameters
            -----------
            alldata_path: str
                the path to the alldata.xlsx file

            mainpubs_path: str
                    the path to the mainpubs.xlsx file

            savepath: str
                    the path to the folder to save this cluster

            min_year : str
                    the earliest year to limit the period of publication retrieval

            max_year : str
                    the latest year to limit the period of publication retrieval

            Returns
            ----------
            None

        '''

        all_valid = True
        alldata_file = alldata_path.get()
        mainpubs_file = mainpubs_path.get()
        folder_path = save_path.get()
        minimum_year = min_year.get()
        maximum_year = max_year.get()
        error_message = ""
        if (len(alldata_file) == 0) or not path.exists(alldata_file):
            alldata_path.config({'background': ERROR_COLOUR})
            error_message += "Alldata.xlsx file path does not exist. \n"
            all_valid = False

        if (len(mainpubs_file) == 0) or not path.exists(mainpubs_file):
            mainpubs_path.config({'background': ERROR_COLOUR})
            error_message += "Mainpubs.xlsx file path does not exist. \n"
            all_valid = False

        if (len(folder_path) == 0) or not path.exists(folder_path):
            save_path.config({'background': ERROR_COLOUR})
            error_message += "Folder path does not exist. \n"
            all_valid = False 

        if (len(minimum_year) == 0):
            min_year.config({'background': ERROR_COLOUR})
            error_message += "Earliest Year cannot be empty. \n"
            all_valid = False

        if (len(maximum_year) == 0):
            max_year.config({'background': ERROR_COLOUR})
            error_message += "Latest Year cannot be empty. \n"
            all_valid = False  
        
        if (all_valid):
            all_entry = [alldata_path, mainpubs_path, save_path, min_year, max_year]
            for entry in all_entry:
                entry.config({'background': SIDEBAR_LIGHTGREY})
            print("EXECUTING")
            analysis_of_data(alldata_file, mainpubs_file, folder_path, minimum_year, maximum_year)
            return "COMPLETED"
        else:
            self.update_output_message(error_message)
            return "ERROR IN INPUTS"

    def get_google_data(self, savepath, topic, key, min_year, max_year, root_doc, cite_doc):
        ''' Function that will initiate the analysis of data. This function will execute
        input validation too.

        Parameters
        -----------
        savepath: str
                the path to the folder to save the retrieved data
        
        topic : str
                the topic of interest

        key : str
                    the api key to connect SERPAPI successfully

        min_year : int
                    the earliest year to limit the period of publication retrieval

        max_year : int
                    the latest year to limit the period of publication retrieval

        root_doc : int
                    the number of publications wanted

        cite_doc : int
                    the number of citing publications wanted

        Returns
        ----------
        None

        '''

        all_valid = True
        folder_path = savepath.get()
        query_topic = topic.get()
        api_key = key.get()
        minimum_year = min_year.get()
        maximum_year = max_year.get()
        no_of_root_doc = root_doc.get()
        no_of_cite_doc = cite_doc.get()
        error_message = ""
        if (len(folder_path) == 0) or not path.exists(folder_path):
            savepath.config({'background': ERROR_COLOUR})
            error_message += "Folder path does not exist. \n"
            all_valid = False

        if (len(query_topic) == 0):
            topic.config({'background': ERROR_COLOUR})
            error_message += "Query Topic cannot be empty. \n"
            all_valid = False

        if (len(api_key) == 0):
            topic.config({'background': ERROR_COLOUR})
            error_message += "API Key cannot be empty. \n"
            all_valid = False

        if (len(minimum_year) == 0):
            min_year.config({'background': ERROR_COLOUR})
            error_message += "Earliest Year cannot be empty. \n"
            all_valid = False

        if (len(maximum_year) == 0):
            max_year.config({'background': ERROR_COLOUR})
            error_message += "Latest Year cannot be empty. \n"
            all_valid = False

        if (len(no_of_root_doc) == 0):
            root_doc.config({'background': ERROR_COLOUR})
            error_message += "Number of Root Documents cannot be empty. \n"
            all_valid = False

        if (len(no_of_cite_doc) == 0):
            cite_doc.config({'background': ERROR_COLOUR})
            error_message += "Number of Citing Documents cannot be empty. \n"
            all_valid = False

        if (all_valid):
            all_entry = [savepath, topic, min_year, max_year, root_doc, cite_doc]
            for entry in all_entry:
                entry.config({'background': SIDEBAR_LIGHTGREY})

            retrieval_of_data(folder_path, query_topic, api_key, minimum_year, maximum_year, no_of_root_doc, no_of_cite_doc)
            return "COMPLETED"
        else:
            self.update_output_message(error_message)
            return "ERROR IN INPUTS"

# input validation callbacks, universal checker
def is_valid_number(input):
    if input.isdigit():
        return True
    elif input == "":
        return True
    else:
        return False

def retrieval_of_data(savepath, topic, key, min_year, max_year, limit, citation_limit):
    total_retrieved = 0
    app.update_output_message("Starting retrieval of data")
    app.master.update()
    try:
        alldata_col = ['Title', 'Year', 'Abstract', 'Citedby_id', 'No_of_citations', 'Result_id']
        alldata_df = pd.DataFrame(columns=alldata_col)
        main_data_col = ['Title', 'Year', 'Abstract', 'Citedby_id', 'No_of_citations', 'Result_id', 'Type_of_Pub', 'Citing_pubs_id']
        main_data_df = pd.DataFrame(columns=main_data_col)

        app.progress_bar["value"] = 10
        app.master.update()
        limit = int(limit)
        citation_limit = int(citation_limit)
        app.update_output_message("Connecting Google Scholar")
        app.master.update()
        remainder = limit - total_retrieved
        while (total_retrieved < limit):
            
            num_to_retrieve = 20 if remainder >= 20 else remainder
            alldata, mainpubs = serpg.retrieve_docs_2(topic, key, min_year, max_year, num_to_retrieve, citation_limit, total_retrieved)
            
            total_retrieved += len(mainpubs.keys())
            alldata_df = serpg.add_to_df(alldata_df, alldata)
            main_data_df = serpg.add_to_df(main_data_df, mainpubs)

            app.update_output_message("Retrieved " + str(total_retrieved) + " number of documents")
            app.progress_bar["value"] += (80/limit)
            app.master.update()

        if (alldata_df.empty or main_data_df.empty):
            raise Exception("No publications retrieved, please check Google Scholar API or Inputs")

        alldata_path = savepath + "/alldata.xlsx"
        alldata_df.to_excel(alldata_path, index=False)
        mainpub_path = savepath + "/main_pubs.xlsx"
        main_data_df.to_excel(mainpub_path, index=False)

        app.update_output_message("Retrieval of data Complete")
        app.progress_bar["value"] = 100
        app.master.update()

    except Exception as err:
        app.update_output_message("{}".format(err).upper())
        app.progress_bar["value"] = 0
        app.master.update()

    return 0

def analysis_of_data(alldata_file, mainpubs_file, savepath, min_year, max_year):
    min_year = int(min_year)
    max_year = int(max_year)
    app.update_output_message("Starting retrieval of data")
    app.master.update()
    try: 
        alldata_df = pd.read_excel(alldata_file)
        mainpubs_df = pd.read_excel(mainpubs_file)
        

        no_of_topics = int(len(alldata_df.index) * 0.10)   # 10% of all publications in the topic
        topics, lda_model, dictionary = topic_model.prepare_topics(alldata_df, no_of_topics)
        alldata_df = analysis.tag_pubs_to_topics(alldata_df, lda_model, dictionary)

        app.update_output_message("Creating Network file now")
        app.progress_bar["value"] = 10
        app.master.update()

        node_dict = analysis.create_nodes(alldata_df, mainpubs_df)
        app.update_output_message("Number of nodes: " + str(len(node_dict.keys())))
        app.progress_bar["value"] = 15
        app.master.update()
        MIN_STRENGTH = 2; 
        connected_nodes_list, components = analysis.create_network_file(node_dict, alldata_df, MIN_STRENGTH, savepath)

        app.progress_bar["value"] = 20
        app.master.update()

        cluster_names = textminer_nlp.create_cluster_names(components, alldata_df, 2, "Title", "Abstract")
        clusters = {}
        linegraph_data_dict = {}
        for x in range(0, len(components)):

            cluster = components[x]
            cluster_no = x + 1
            cluster_name = cluster_names[x]
            
            app.update_output_message("Analysing Component " + str(cluster_no) + ": " + cluster_name)
            app.progress_bar["value"] += (70/len(components))
            app.master.update()

            
            cluster_df, linegraph_data = analysis.create_cluster_indi_2(cluster, cluster_no, cluster_name,
                                                                        alldata_df, min_year, max_year, 
                                                                        lda_model, dictionary, savepath)
            clusters[cluster_name] = cluster_df
            linegraph_data_dict[cluster_name] = linegraph_data

        combined_df = pd.concat(clusters)
        combineddata_path = savepath + "/combined_data.xlsx"
        combined_df.to_excel(combineddata_path, index=False)
        analysis.create_cluster_sum(clusters, linegraph_data_dict, min_year, max_year, savepath)

        app.update_output_message("Analysis Completed")
        app.progress_bar["value"] = 100
        app.master.update()
    except Exception as err:
        raise Exception
        app.update_output_message("{}".format(err).upper())
        app.progress_bar["value"] = 0
        app.master.update()

    # list_of_cluster_df, linegraph_data = analysis.create_cluster_indi(components, alldata_df, word_bank, min_year, max_year, lda_model, dictionary)
    # analysis.create_cluster_sum(list_of_cluster_df, linegraph_data, min_year, max_year)

    return 0
    

root = tk.Tk()
app = Application(master=root)
app.mainloop()
