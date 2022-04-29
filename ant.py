import tkinter as tk
from tkinter import filedialog

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pymongo
import json


class AssignmentApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.geometry(self, "600x250")
        tk.Tk.wm_title(self, "Give me a distinction")

        container = tk.Frame(self)
        container.pack(side='top', fill='both', expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (MainPage, SomeOtherPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky='nsew')

        self.show_frame(MainPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class MainPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.label1 = tk.Label(self, text='Data Analysis Tool', padx=180, pady=20)
        self.load_airport_CSVbutton = tk.Button(self, text='Load Airport CSV', command=lambda: self.load_airport_CSV())

        self.clean_and_save_button = tk.Button(self, text='Clean and Save', command=lambda: self.clean_and_save(self.airports, self.airportFreq))

        self.load_from_mongo_button = tk.Button(self, text='Load from Mongo', command=lambda: self.load_from_mongo())

        self.label1.pack()
        self.load_airport_CSVbutton.pack()
        self.clean_and_save_button.pack()
        self.load_from_mongo_button.pack()

    def load_airport_CSV(self):
        import_file_path = filedialog.askopenfilename()
        self.airports = pd.read_csv(import_file_path)

    def load_airportFreq_CSV(self):
        import_file_path = filedialog.askopenfilename()
        self.airportFreq = pd.read_csv(import_file_path)

    def clean_and_save(self, airports, airportfreqs):
        merged = pd.merge(airports, airportfreqs, left_on='ident', right_on='airport_ident')
        merged = merged[merged.type_x != 'closed']
        merged = merged[merged.type_x != 'heliport']
        merged = merged[merged.iso_country == 'GB']
        clean = merged[['type_x', 'name', 'airport_ident', 'iso_region', 'frequency_mhz']]

        client = pymongo.MongoClient("mongodb://localhost:27017")
        db = client["Airports"]
        self.collection = db['AirportFrequencyData']

        self.df = clean.to_json(orient='records')
        with open('df.json', 'w') as f:
            f.write(self.df)

        with open('df.json') as f:
            data = json.load(f)
            for i in data:
                self.collection.insert_one(i)

    def load_from_mongo(self):
        self.df = pd.DataFrame(list(self.collection.find()))


class SomeOtherPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)


app = AssignmentApp()
app.mainloop()
