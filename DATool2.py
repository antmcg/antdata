#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import tkinter as tk
from tkinter import filedialog
from tkinter import *
from tkinter import messagebox
from tkinter.filedialog import asksaveasfile

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pymongo
import json

root = tk.Tk()

canvas = tk.Canvas(root, width=900, height=800, bg='white', relief='raised')
canvas.grid()

label1 = tk.Label(root, text='Data Analysis Tool', bg='white')
label1.config(font=('helvetica', 20))
canvas.create_window(150, 60, window=label1)

# Initial set the Path to home
# not sure what this is here for; It exists as a mere remnant of the GUI code I found on google
path = './'

# Loading CSV files needed. Need them to be loaded in in a specific order in order to assign them to the correct variable names
# so that the cleaning data functions will work.
    
def loadCSV():
    global airports
    import_file_path = filedialog.askopenfilename()
    airports = pd.read_csv(import_file_path)
    #not sure how this will work now 
    global airportFreq
    import_file_path = filedialog.askopenfilename()
    airportFreq = pd.read_csv(import_file_path)
    
loadCSVBtn = tk.Button(text="Import Airport Data", command=loadCSV, bg='blue', fg='white',font=('helvetica', 12, 'bold'))
canvas.create_window(150, 130, window=loadCSVBtn)


#______________________________________________________________________

# Cleaning the loaded CSV file. Need a way of assigning respective folders to variable names seen below
# what if someone 
def cleanAndSave():
    merged = pd.merge(airports, airportFreq, left_on='ident', right_on='airport_ident')
    #remove all closed and none airport types
    merged = merged[merged.type_x != 'closed']
    merged = merged[merged.type_x != 'heliport']
    #remove non GB airports
    merged = merged[merged.iso_country == 'GB']
    #create final dataframe holding the values relevant to the cleints requests
    clean = merged[['type_x', 'name','airport_ident','iso_region','frequency_mhz']]

    # Create client to connect to MongoDB
    client = pymongo.MongoClient("mongodb://localhost:27017")
    db = client["Airports"]
    collection = db['AirportFrequencyData']

    #Save dataframe to JSON and then insert data to mongo
    df = clean.to_json(orient='records')
    with open('df.json','w') as f:
        f.write(df)


    with open('df.json') as f:
        data = json.load(f)
        for i in data:
            ins = collection.insert_one(i)

CleanAndSaveButton= tk.Button(text='Clean CSV File', command=cleanAndSave, bg='blue', fg='white',font=('helvetica', 12, 'bold'))
canvas.create_window(150, 230, window=CleanAndSaveButton)

#_____________________________________________________________________

def loadFromMongo():
    #Get Data from mongo
    #db = client['Airports'] ----- Don't know if I need to keep this
    #collection = db['AirportFrequencyData'] ----- Don't know if I need to keep this either
    df = pd.DataFrame(list(collection.find()))
    
LoadFromMongoButton = tk.Button(text="Load Data From MongoDB", command=loadFromMongo, bg='blue', fg='white', font'helvetica', 12, 'bold')
canvas.create_window(150, 280, window=LoadFromMongoButton)

#_____________________________________________________________________

# Rearranging and Visualising Data

# Visualisation 1
def vis1():
    large_airports = df.groupby(['type_x'])
    #Produce the mean, mode and median for the ‘frequency_mhz’, For large_airport, For frequencies more than 100 mhz
    large_airports = large_airports.get_group('large_airport')
    #remove frequencies below 100
    large_airports = large_airports[large_airports.frequency_mhz >= 100]
    #produce mean, median and mode for each large airport freq
    mean = large_airports['frequency_mhz'].mean()
    median = large_airports['frequency_mhz'].median()
    mode = large_airports['frequency_mhz'].mode().iloc[0]

    #plot data
    plotdata = {'Mean':mean, 'Median':median, 'Mode':mode}
    x = list(plotdata.keys())
    values = list(plotdata.values())

    fig = plt.figure(figsize = (10, 5))

    plt.bar(x, values, color = 'maroon', width = 0.4)
    plt.xlabel("Measures of Central Tendency")
    plt.ylabel("Frequency mhz")
    plt.title("Produce the mean, mode and median for frequency_mhz, For large_airport with frequencies more than 100 mhz")
    plt.ylim(120, 125)
    plt.show()

vis1PlotBtn = tk.Button(text= "Vis 1 Plot", command=vis1,bg='orange', fg='white', font=('helvetica' 12, 'bold'))
canvas.create_window(150, 280, window=vis1PlotBtn)

#Visualisation 2
def vis2():
    small_airports = df.groupby('type_x')
    small_airports = small_airports.get_group('small_airport')

    plot_data_2 = small_airports.groupby('iso_region', as_index=False)['frequency_mhz'].mean()

    fig = plt.figure(figsize = (10, 5))

    plot_data_2.plot.bar(x='iso_region', y= 'frequency_mhz')

    plt.xlabel("UK Region")
    plt.ylabel("Frequency mhz")
    plt.title("Mean Communications frequencies used by small airports, grouped by region")
    plt.ylim(120, 135)
    plt.show()

vis2PlotBtn = tk.Button(text= "Vis 2 Plot", command=vis1,bg='orange', fg='white', font=('helvetica' 12, 'bold'))
canvas.create_window(150, 330, window=vis2PlotBtn)



#______________________________________________________________________
# Exiting the Application
def exitapplication():
    MsgBox = tk.messagebox.askquestion('Exit Application', 'Are you sure you want to exit the application',icon='warning')
    if MsgBox == 'yes':
        root.destroy()


exitButton = tk.Button(root, text='       Exit Application     ', command=exitapplication, bg='brown', fg='white',font=('helvetica', 12, 'bold'))
canvas.create_window(150, 380, window=exitButton)

root.mainloop()

