from flask import Flask, render_template, request, redirect, url_for, flash
import pymssql
import requests
import pandas as pd

'''
PURELY WRITTEN TO UPLOAD DATA ON AZURE DATABASE FASTER 
SO THAT IT COULD SAVE SOME TIME IN QUIZ
'''


server = "test0000@mavs.uta.edu" #please add your azure account id 
user = 'sampleuser' #add your database useranme
password = 'samplepass' # add your database pass 
conn = pymssql.connect(server, user, password, "test") #add your db name at the place of test
c1 = conn.cursor()


# def parseCSV():
#     #url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.csv"
#     #req = requests.get(url)
#     #url_content = req.content
#     csv_file = open('downloaded.csv', 'wb')
#     csv_file.write(url_content)
#     csv_file.close()

# def newTable():
#     #sql1 = "DROP TABLE IF EXISTS earthquake"
#     c1.execute(sql1)
#     conn.commit()
#     #time,latitude,longitude,depth,mag,magType,nst,gap,dmin,rms,net,id,updated,place,type,horizontalError,depthError,magError,magNst,status,locationSource,magSource
#     # sql2 = "create table earthquake(time varchar(25), latitude varchar(25), longitude varchar(25), depth varchar(25), mag varchar(25),magtype varchar(25),nst varchar(25),gap varchar(25),dmin varchar(25),rms varchar(25),net varchar(25),id varchar(25),updated varchar(25),place varchar(150),type varchar(25),horizontalError varchar(25),depthError varchar(25),magError varchar(25), magNst varchar(25), status varchar(25), locationSource varchar(25), magSource varchar(25));" 
#     sql2 = "create table ni(name varchar(30), id varchar(25) primary "
#     c1.execute(sql2)
#     conn.commit()

def uploadData():
    #newTable()
    #parseCSV()
    # col_names = ['time']
    col_names = ['a', 'b','c']
    csvData = pd.read_csv('data-1.csv',names=col_names,header=None)
    csvData = csvData.where((pd.notnull(csvData)), 0)
    for i, row in csvData.iterrows():
        try:
            # sql = "INSERT INTO earthquake (time) VALUES (%s)"
            sql = "Insert into data(a,b,c) values (%s,%s,%s)"
            values = (row[0], row[1],row[2])
            print(values)
            c1.execute(sql, values)
            conn.commit()
            conn.close
        except Exception as e:
            print(e)

                 
uploadData()