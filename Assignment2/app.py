from asyncio import start_server
from flask import Flask, render_template, request, redirect, url_for, flash
import pymssql
import requests
import pandas as pd
from datetime import datetime
from geopy.distance import geodesic
app = Flask(__name__)
#secret key could be any string 
app.secret_key = "asdgfjhsdgfjhsdgryaesjtrjyetrjyestrajyrtesyjrtdyjrtasdyrtjsejrtestrerty"

header_html = '<html> <head> <title> Assignment2</title> </head> <body> <h1> ID: 1001967237 </h1> <h1> Name: Omkar shrikant gawade </h1> <br />'
server = "test0000@mavs.uta.edu" #please add your azure account id 
user = 'sampleuser' #add your database useranme
password = 'samplepass' # add your database pass 
conn = pymssql.connect(server, user, password, "test") #add your db name at the place of test
c1 = conn.cursor()

@app.route('/', methods=['GET','POST'])
def index():
    data = None
    if request.method == "POST":
        input = request.form['input']
        date_from = request.form['from']
        date_to = request.form['to']
        if input:
            sql1 = f"SELECT TOP {input} * FROM earthquake ORDER BY mag DESC"
            c1.execute(sql1)
            data = c1.fetchall()
        elif date_from and date_to:
            sql2 = f"SELECT * from earthquake where time between '{date_from}' and '{date_to}' and mag > 3.0"
            c1.execute(sql2)
            data = c1.fetchall()
        elif request.form.get('action1') == 'VALUE1':
            sql3 = f"select count(*) from earthquake"
            sql4 = f"select top 1 place from earthquake order by mag desc"
            c1.execute(sql3)
            data1 = c1.fetchall()
            c1.execute(sql4)
            data2 = c1.fetchall()
            data = data1 + data2
        elif request.form.get('from_mag') and request.form.get('to_mag'):
            from_mag = float(request.form['from_mag'])
            to_mag = float(request.form['to_mag'])
            place = request.form['place']
            start = from_mag
            data = []
            sql10 = f"SELECT time,latitude,longitude,mag,place FROM earthquake WHERE MAG BETWEEN {from_mag} AND {to_mag} AND place LIKE '%{place}%'"
            c1.execute(sql10)
            data = c1.fetchall()
            #data.append(c1.fetchall())
            #start = start + 0.1
        #data = data[:-1]
        elif request.form.get('lat') and request.form.get('long'):
            lat = float(request.form['lat'])
            long = float(request.form['long'])
            result = []
            magnitude = []
            sql6 = f"SELECT latitude, longitude, place, mag FROM earthquake where time > '2022-01-09' AND time < '2022-02-24'"
            c1.execute(sql6)
            data = c1.fetchall()
            start = c1.fetchall()
            for n in start:
                dist = geodesic(destination, n[:2]).kilometers
                print(dist)
                if dist<500:
                    result.append((n[0],n[1],n[2],n[3],dist))
                    magnitude.append((n[3]))
                mag = max(magnitude)
                for m in result:
                    if m[3] == mag:
                        data.append((m[0],m[1],m[2],m[3],m[4]))
        elif request.form.get('lat') and request.form.get('long'):
            replace = request.form['change_value']
            destination = (lat, long)
            sql6 = f"SELECT latitude, longitude, place, mag FROM earthquake where time > '2022-01-09' AND time < '2022-02-24'"
            c1.execute(sql6)
            data = c1.fetchall()

    return header_html+render_template("index.html",data=data)

if __name__ == '__main__':
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)

# show the total number of earthquakes ("quakes") in the data set, 
#     and give the largest one ("mag") and its location (the name, the "place" location).

'''
BELOW CODE CAN BE USED TO UPLOAD NEW DATA TO DATABASE AT AZURE
CAUTION : THIS REQUIRED MORE THEN 10-15 MIN NOT RECOMMENDED TO DO IN QUIZ
'''

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