from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
import pymssql
import requests
import pandas as pd
app = Flask(__name__)
app.secret_key = "asdgfjhsdgfjhsdgryaesjtrjyetrjyestrajyrtesyjrtdyjrtasdyrtjsejrtestrerty"

header_html = '<html> <head> <title> Assignment7</title> </head> <body> <h1> ID: 1001967237 </h1> <h1> Name: Omkar shrikant gawade </h1> <br />'
server = "test0000@mavs.uta.edu" #please add your azure account id 
user = 'sampleuser' #add your database useranme
password = 'samplepass' # add your database pass 
conn = pymssql.connect(server, user, password, "test") #add your db name at the place of test
c1 = conn.cursor()

@app.route('/', methods=['GET','POST'])
def index():
    data1 = None
    if request.method == "POST":
        input = request.form['input']
        if input:
            # start = datetime.now()
            sql1 = f"SELECT TOP {input} * FROM earthquake ORDER BY mag DESC"
            c1.execute(sql1)
            data1 = c1.fetchall()
            # stop = datetime.now()
            # data2 = (stop - start).total_seconds()
    return header_html+render_template("index.html",data1=data1)

if __name__ == '__main__':
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)

# show the total number of earthquakes ("quakes") in the data set, 
#     and give the largest one ("mag") and its location (the name, the "place" location).


# def parseCSV():
#     url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.csv"
#     req = requests.get(url)
#     url_content = req.content
#     csv_file = open('downloaded.csv', 'wb')
#     csv_file.write(url_content)
#     csv_file.close()

# def newTable():
#     sql1 = "DROP TABLE IF EXISTS earthquake"
#     c1.execute(sql1)
#     conn.commit()
#     #time,latitude,longitude,depth,mag,type,gap,net,id,place
#     sql2 = "create table earthquake(time varchar(25), latitude varchar(25), longitude varchar(25), depth varchar(25), mag varchar(25),type varchar(25),gap varchar(25),net varchar(25),id varchar(25),place varchar(50));" 
#     c1.execute(sql2)
#     conn.commit()

# def uploadData():
#     newTable()
#     col_names = ['time','latitude','longitude','depth','mag','type','gap','net','id','place']
#     csvData = pd.read_csv('eq.csv',names=col_names,header=None)
#     csvData = csvData.where((pd.notnull(csvData)), 0)
#     for i, row in csvData.iterrows():
#         if i > 0:
#                 try:
#                     sql = "INSERT INTO earthquake (time,latitude,longitude,depth,mag,type,gap,net,id,place) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
#                     values = (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],row[8], row[9])
#                     c1.execute(sql, values)
#                     conn.commit()
#                     conn.close
#                 except Exception as e:
#                     print(e)
                 
# uploadData()