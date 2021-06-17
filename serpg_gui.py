import tkinter as tk
from tkinter.filedialog import askopenfile, askdirectory

import serpg
import analysis

SIDEBAR_LIGHTGREY = "#d4d4d4"
MAINWINDOW_WHITE = "#ffffff"


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.master.title("Citation Analysis")
        canvas = tk.Canvas(self.master, width=800, height=500)
        canvas.pack()
        sidebar, main_window = self.create_frames()
        self.create_sidebar(sidebar, main_window)
        self.create_mainframe(main_window)
        self.alldata_path = ""
        self.main_pub_path = ""
        self.savefolder_path = ""

    def create_frames(self):
        sidebar = tk.Frame(self.master, bg=SIDEBAR_LIGHTGREY)
        sidebar.place(relx=0, rely=0.5, relwidth=0.25,
                      relheight=1, anchor="w")
        main_window = tk.Frame(self.master, bg=MAINWINDOW_WHITE)
        main_window.place(relx=1, rely=0.5, relwidth=0.75,
                          relheight=1, anchor="e")
        return sidebar, main_window

    def create_sidebar(self, frame, mainwindow):
        inst_text = "What would you \n like to do?"
        instructions = tk.Label(frame, text=inst_text, bg=SIDEBAR_LIGHTGREY)
        instructions.place(relx=0.2, rely=0.1, relwidth=0.5, relheight=0.3)
        self.create_serpapi_btn(frame, mainwindow)
        self.create_cite_analysis_btn(frame, mainwindow)

    def create_serpapi_btn(self, frame, mainwindow):
        get_folder = tk.StringVar()
        browse_btn = tk.Button(master=frame, textvariable=get_folder,
                               command=lambda: self.create_mainframe_data(mainwindow))
        get_folder.set("Receive Data")
        browse_btn.place(relx=0.2, rely=0.5, relwidth=0.5, relheight=0.1)

    def create_cite_analysis_btn(self, frame, mainwindow):
        get_file = tk.StringVar()
        browse_file = tk.Button(master=frame, textvariable=get_file,
                                command=lambda: self.create_mainframe_analysis(
                                    mainwindow)
                                )
        get_file.set("Start Analysis")
        browse_file.place(relx=0.2, rely=0.7, relwidth=0.5, relheight=0.1)

    def create_mainframe(self, frame):
        mainframe_text = "Main Frame"
        main_frame_inst = tk.Label(
            frame, text=mainframe_text, bg=MAINWINDOW_WHITE)
        main_frame_inst.place(relx=0.4, rely=0.00,
                              relwidth=0.2, relheight=0.05)

    def create_mainframe_analysis(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()
        all_data_file_label = tk.Label(
            frame, text="Please provide filepath to alldata.xlsx", bg=MAINWINDOW_WHITE)
        all_data_file_label.place(
            relx=0.1, rely=0.05, relwidth=0.6, relheight=0.05)
        all_data_file = tk.Entry(master=frame, bg=SIDEBAR_LIGHTGREY)
        all_data_file.place(relx=0.1, rely=0.1, relwidth=0.6, relheight=0.05)
        all_data_btn = self.get_file_button(frame, all_data_file)
        all_data_btn.place(relx=0.75, rely=0.1, relwidth=0.1, relheight=0.05)

        main_data_label = tk.Label(
            frame, text="Please provide filepath to main_pubs.xlsx", bg=MAINWINDOW_WHITE)
        main_data_label.place(relx=0.1, rely=0.2, relwidth=0.6, relheight=0.05)
        main_data_file = tk.Entry(master=frame, bg=SIDEBAR_LIGHTGREY)
        main_data_file.place(relx=0.1, rely=0.25, relwidth=0.6, relheight=0.05)
        main_data_btn = self.get_file_button(frame, main_data_file)
        main_data_btn.place(relx=0.75, rely=0.25, relwidth=0.1, relheight=0.05)

        save_folder_label = tk.Label(
            frame, text="Please provide path to folder to save the documents", bg=MAINWINDOW_WHITE)
        save_folder_label.place(relx=0.1, rely=0.35,
                                relwidth=0.6, relheight=0.05)
        save_folder = tk.Entry(master=frame, bg=SIDEBAR_LIGHTGREY)
        save_folder.place(relx=0.1, rely=0.40, relwidth=0.6, relheight=0.05)
        save_folder_btn = self.get_folder_button(frame, save_folder)
        save_folder_btn.place(relx=0.75, rely=0.40,
                              relwidth=0.1, relheight=0.05)

        min_year_label = tk.Label(
            frame, text="Please indicate \nearliest year eg. 2010", bg=MAINWINDOW_WHITE)
        min_year_label.place(relx=0.1, rely=0.50, relwidth=0.2, relheight=0.1)
        min_year = tk.Entry(master=frame, bg=SIDEBAR_LIGHTGREY)
        min_year.place(relx=0.1, rely=0.60, relwidth=0.2, relheight=0.05)

        max_year_label = tk.Label(
            frame, text="Please indicate \nlatest year eg. 2020", bg=MAINWINDOW_WHITE)
        max_year_label.place(relx=0.5, rely=0.50, relwidth=0.2, relheight=0.1)
        max_year = tk.Entry(master=frame, bg=SIDEBAR_LIGHTGREY)
        max_year.place(relx=0.5, rely=0.60, relwidth=0.2, relheight=0.05)

        start_analysis = self.start_analysis_button(frame, all_data_file, main_data_file,
                                                    save_folder, min_year, max_year)
        start_analysis.place(relx=0.1, rely=0.70, relwidth=0.6, relheight=0.1)

    def create_mainframe_data(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()
        topic_label = tk.Label(
            frame, text="Please indicate topic to be researched on", bg=MAINWINDOW_WHITE)
        topic_label.place(relx=0.1, rely=0.05, relwidth=0.6, relheight=0.05)
        topic = tk.Entry(master=frame, bg=SIDEBAR_LIGHTGREY)
        topic.place(relx=0.1, rely=0.1, relwidth=0.6, relheight=0.05)

        min_year_label = tk.Label(
            frame, text="Please indicate \nearliest year eg. 2010", bg=MAINWINDOW_WHITE)
        min_year_label.place(relx=0.1, rely=0.20, relwidth=0.2, relheight=0.1)
        min_year = tk.Entry(master=frame, bg=SIDEBAR_LIGHTGREY)
        min_year.place(relx=0.1, rely=0.30, relwidth=0.2, relheight=0.05)

        max_year_label = tk.Label(
            frame, text="Please indicate \nlatest year eg. 2020", bg=MAINWINDOW_WHITE)
        max_year_label.place(relx=0.5, rely=0.20, relwidth=0.2, relheight=0.1)
        max_year = tk.Entry(master=frame, bg=SIDEBAR_LIGHTGREY)
        max_year.place(relx=0.5, rely=0.30, relwidth=0.2, relheight=0.05)

        root_doc_label = tk.Label(
            frame, text="Please indicate the number \nof root documents eg. 20", bg=MAINWINDOW_WHITE)
        root_doc_label.place(relx=0.0, rely=0.40, relwidth=0.4, relheight=0.1)
        root_doc = tk.Entry(master=frame, bg=SIDEBAR_LIGHTGREY)
        root_doc.place(relx=0.1, rely=0.50, relwidth=0.2, relheight=0.05)

        cite_doc_label = tk.Label(
            frame, text="Please indicate the number of citing \ndocuments per root document eg. 20", bg=MAINWINDOW_WHITE)
        cite_doc_label.place(relx=0.4, rely=0.40, relwidth=0.4, relheight=0.1)
        cite_doc = tk.Entry(master=frame, bg=SIDEBAR_LIGHTGREY)
        cite_doc.place(relx=0.5, rely=0.50, relwidth=0.2, relheight=0.05)

        save_folder_label = tk.Label(
            frame, text="Please provide path to folder to save the documents", bg=MAINWINDOW_WHITE)
        save_folder_label.place(
            relx=0.1, rely=0.6, relwidth=0.6, relheight=0.05)
        save_folder = tk.Entry(master=frame, bg=SIDEBAR_LIGHTGREY)
        save_folder.place(relx=0.1, rely=0.65, relwidth=0.6, relheight=0.05)
        save_folder_btn = self.get_folder_button(frame, save_folder)
        save_folder_btn.place(relx=0.75, rely=0.65,
                              relwidth=0.1, relheight=0.05)

        retrieve_info = self.retrieve_info_button(frame, save_folder, topic, min_year, 
                                                    max_year, root_doc, cite_doc)
        retrieve_info.place(relx=0.1, rely=0.75, relwidth=0.6, relheight=0.1)

    def get_file_button(self, frame, entry):
        btn = tk.Button(master=frame, text="Open",
                        command=lambda: self.retrieve_file(frame, entry))
        return btn

    def get_folder_button(self, frame, entry):
        btn = tk.Button(master=frame, text="Open",
                        command=lambda: self.retrieve_folder(frame, entry))
        return btn

    def start_analysis_button(self, frame, alldata_path, mainpubs_path, save_path, min_year, max_year):
        btn = btn = tk.Button(master=frame, text="Start Analysis",
                              command=lambda: self.analyse_data(alldata_path.get(), mainpubs_path.get(),
                                                                save_path.get(), min_year.get(), 
                                                                max_year.get()))
        return btn

    def retrieve_info_button(self, frame, save_folder, topic, min_year, max_year, root_doc, cite_doc):
        btn = btn = tk.Button(master=frame, text="Retrieve Info",
                              command=lambda: self.get_google_data(save_folder.get(), topic.get(),
                                                                   min_year.get(), max_year.get(),
                                                                   root_doc.get(), cite_doc.get()))
        return btn

    def retrieve_file(self, frame, entry):
        file = askopenfile(parent=frame, title="Open file")
        entry.insert(tk.END, file.name)
        return file

    def retrieve_folder(self, frame, entry):
        folder = askdirectory(parent=frame, title="Open folder")
        entry.insert(tk.END, folder)
        return folder

    def analyse_data(self, alldata_path, mainpubs_path, save_path, min_year, max_year):
        if (len(alldata_path) == 0 or len(mainpubs_path) == 0 or len(min_year) == 0 or len(max_year) == 0 or len(save_path) == 0):
            print("alldata_path: " + alldata_path)
            print("mainpubs_path: " + mainpubs_path)
            print("min_year: " + min_year)
            print("max_year: " + max_year)
            print("save_path: " + save_path)
            print("STILL EXECUTING")
            return "ERROR, PLEASE CHECK INPUTS"
        else:
            print("EXECUTING")
            analysis.start_analysis(
                alldata_path, mainpubs_path, save_path, min_year, max_year)
            return "COMPLETED"

    def get_google_data(self, save_folder, topic, min_year, max_year, root_doc, cite_doc):
        if (len(save_folder) == 0 or len(topic) == 0 or len(min_year) == 0 or len(max_year) == 0 or len(root_doc) == 0 or len(cite_doc) == 0):
            print("save folder: " + save_folder)
            print("topic: " + topic)
            print("min_year: " + min_year)
            print("max_year: " + max_year)
            print("root_doc: " + root_doc)
            print("cite_doc: " + cite_doc)
            print("STILL EXECUTING")
            return "ERROR, PLEASE CHECK INPUTS"
        else:
            print("EXECUTING")
            serpg.get_google_data(save_folder, topic, min_year,
                                  max_year, root_doc, cite_doc)
            return "COMPLETED"

# root = tk.Tk()
# root.title("Citation Analysis")
# canvas = tk.Canvas(master=root, width=800, height=500)
# canvas.pack()

# sidebar = tk.Frame(root, bg="#d4d4d4")
# sidebar.place(relx=0, rely=0.5, relwidth=0.25, relheight=1, anchor="w")

# main_window = tk.Frame(root, bg="#ffffff")
# main_window.place(relx=1, rely=0.5, relwidth=0.75, relheight=1, anchor="e")


# # instructions
# inst_text = "What would you \n like to do?"
# instructions = tk.Label(sidebar, text=inst_text, bg="#d4d4d4")
# instructions.place(relx=0.2, rely=0.1, relwidth=0.5, relheight=0.3)
# # get_folder
# get_folder = tk.StringVar()
# browse_btn = tk.Button(master=sidebar, textvariable=get_folder,
#                        command=lambda: retrieve_data())
# get_folder.set("Receive Data")
# browse_btn.place(relx=0.2, rely=0.5, relwidth=0.5, relheight=0.1)
# alldata_file_path = tk.Entry()
# # get_files
# get_file = tk.StringVar()
# browse_file = tk.Button(master=sidebar, textvariable=get_file,
#                         command=lambda: retrieve_data()
#                         )
# get_file.set("Start Analysis")
# browse_file.place(relx=0.2, rely=0.7, relwidth=0.5, relheight=0.1)
root = tk.Tk()
app = Application(master=root)
app.mainloop()
