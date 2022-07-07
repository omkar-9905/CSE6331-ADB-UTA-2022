from asyncio import start_server
from flask import Flask, render_template, request, redirect, url_for, flash
import pymssql
import requests
import pandas as pd
from datetime import date, datetime
from geopy.distance import geodesic
from time import time
import redis

myHostname = "test0000.redis.cache.windows.net" #Use your azure redis account username
myPassword = "dGVzdGluZ3JlZGlzUGFzc3dvcmQ=" #User redis account password(base64)

r = redis.StrictRedis(host=myHostname, port=6379,password=myPassword)

app = Flask(__name__)
#secret key could be any string
app.secret_key = "asdgfjhsdgfjhsdgryaesjtrjyetrjyestrajyrtesyjrtdyjrtasdyrtjsejrtestrerty"

header_html = '<html> <head> <title> Assignment3</title> </head> <body> <h1> ID: 1001967237 </h1> <h1> Name: Omkar shrikant gawade </h1> <br />'
server = "test0000@mavs.uta.edu" #please add your azure account id 
user = 'sampleuser' #add your database useranme
password = 'samplepass' # add your database pass 
conn = pymssql.connect(server, user, password, "test") #add your db name at the place of test
c1 = conn.cursor()


#THIS FUNCION WILL BE CALLED WHEN REDIS CAHCE IS BEING USED AND FOR FIRST TIME QUERY WILL HIT THE SQL DATABASE AND AFTER THAT GET DATA FROM REDIS CAHCE ON CLOUD
def query1(input2):
    i = 25
    tic = time()
    while i != 0:
        if r.exists(input2) == 1:
            res = r.get(input2)#.decode("utf-8") #STORING THE DATA USING SAME KEY AS INPUT IN REDIS CACHE
            #data = eval(res)
            i-=1
        else:
            sql1 = f"SELECT TOP {input2} * FROM earthquake ORDER BY mag DESC"
            c1.execute(sql1)
            data = c1.fetchall()
            r.set(input2,str(data)) #SETTING THE VALUE AND KEY IN REDIS CACHE
            i-=1
    data = eval(res)
    toc = time()
    qtime = toc-tic
    print(qtime)
    return data,qtime

#THIS FUNCTION WILL BE CALLED WHEN DIRECTLLY CALLING THE AZURE SQL DATABASE
def old_query(input1):
    i = 25
    tic = time()
    while i!= 0:
        sql1 = f"SELECT TOP {input1} * FROM earthquake ORDER BY mag DESC"
        c1.execute(sql1)
        data = c1.fetchall()
        i-=1
    toc = time()
    qtime = toc- tic
    print(qtime)
    return data, qtime

def query2(date_from,date_to):
    date_query = date_from+date_to
    print(date_query)
    if r.exists(date_query) == 1:
        print("If loop date")
        tic = time()
        res = r.get(date_query)#.decode("utf-8")
        toc = time()
        data = eval(res)
        qtime = toc-tic
        return data,qtime
    else:
        print("Else loop date")
        tic = time()
        sql2 = f"SELECT * from earthquake where time between '{date_from}' and '{date_to}' and mag > 3.0"
        c1.execute(sql2)
        toc = time()
        data = c1.fetchall()
        qtime = toc - tic
        r.set(date_query,str(data))
        return data,qtime


def range(input3,input4):
    sql2 = f"SELECT name,id from ni where id between '{input3}' and '{input4}'"
    c1.execute(sql2)
    data = c1.fetchall()
    qtime = [data[0],data[-1]]
    return qtime,data


def id_range(input5,input6,input9):
    tic = time()
    while input9 != 0:
        sql2 = f"SELECT * FROM ni t1 JOIN di t2 ON t1.id = t2.id where t1.id between '{input5}' and '{input6}'"
        c1.execute(sql2)
        input9-=1
    toc= time()
    data = c1.fetchall()
    return data, toc-tic

def n_no(input7,input8,input9):
    n = int(input9)
    print(n)
    tic = time()
    while n != 0:
        sql2 = f"SELECT top {input7} * FROM ni t1 JOIN di t2 ON t1.id = t2.id where t2.code like '%{input8}'"
        c1.execute(sql2)
        n-=1
    toc = time()
    data = c1.fetchall()
    print(data)
    qtime = toc-tic
    return data,qtime

@app.route('/', methods=['GET','POST'])
def index():
    data = None
    qtime = 0
    if request.method == "POST":
        input1 = request.form['input1']
        input2 = request.form['input2']
        input3 = request.form['input3']
        input4 = request.form['input4']
        input5 = request.form['input5']
        input6 = request.form['input6']
        input7 = request.form['input7']
        input8 = request.form['input8']
        input9 = request.form['input9']
        date_from = request.form['from']
        date_to = request.form['to']
        
#  6. (a) Allow a user to give an id number (in  tables) range, and for all id in that range, list id, name, pwd and code.

#     (b) Allow a user to give a number N (for example 5), and a code, and you will randomly select N of those with exact matching 
#         code and display the same information as the previous part (for example N=5, code= 200003)

#     Please show the time to do those queries.

        if input1:
            data, qtime = old_query(input1)
        elif input2:
            data, qtime = query1(input2)
        elif date_from and date_to:
                data, qtime = query2(date_from,date_to)
        elif input3 and input4:
            data, qtime  = range(input3,input4)
           
        elif input5 and input6 and input9:
            data,qtime = id_range(input5,input6,input9)
        
        elif input7 and input8 and input9:
            data,qtime = n_no(input7,input8,input9)
    
        elif request.form.get('action1') == 'getData':
            tic = time()
            sql3 = f"select count(*) from earthquake"
            sql4 = f"select top 1 place from earthquake order by mag desc"
            c1.execute(sql3)
            data1 = c1.fetchall()
            c1.execute(sql4)
            toc = time()
            data2 = c1.fetchall()
            data = data1 + data2
            qtime = toc - tic
        elif request.form.get('from_mag') and request.form.get('to_mag'):
            from_mag = float(request.form['from_mag'])
            to_mag = float(request.form['to_mag'])
            place = request.form['place']
            start = from_mag
            data = []
            tic = time()
            sql10 = f"SELECT time,latitude,longitude,mag,place FROM earthquake WHERE MAG BETWEEN {from_mag} AND {to_mag} AND place LIKE '%{place}%'"
            c1.execute(sql10)
            toc = time()
            qtime = toc - tic
            data = c1.fetchall()
        elif request.form.get('lat') and request.form.get('long'):
            lat = float(request.form['lat'])
            long = float(request.form['long'])
            result = []
            magnitude = []
            dest = None
            tic = time()
            sql6 = f"SELECT latitude, longitude, place, mag FROM earthquake where time > '2022-02-09' AND time < '2022-02-24'"
            c1.execute(sql6)
            toc = time()
            data = c1.fetchall()
            start = c1.fetchall()
            for n in start:
                dist = geodesic(dest, n[:2]).kilometers
                print(dist)
                if dist<500:
                    result.append((n[0],n[1],n[2],n[3],dist))
                    magnitude.append((n[3]))
                mag = max(magnitude)
                for m in result:
                    if m[3] == mag:
                        data.append((m[0],m[1],m[2],m[3],m[4]))
            qtime = toc - tic

    return header_html+render_template("index.html",data=data,qtime=qtime)

if __name__ == '__main__':
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)


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
#     #time,latitude,longitude,depth,mag,magType,nst,gap,dmin,rms,net,id,updated,place,type,horizontalError,depthError,magError,magNst,status,locationSource,magSource
#     sql2 = "create table earthquake(time varchar(25), latitude varchar(25), longitude varchar(25), depth varchar(25), mag varchar(25),magtype varchar(25),nst varchar(25),gap varchar(25),dmin varchar(25),rms varchar(25),net varchar(25),id varchar(25),updated varchar(25),place varchar(150),type varchar(25),horizontalError varchar(25),depthError varchar(25),magError varchar(25), magNst varchar(25), status varchar(25), locationSource varchar(25), magSource varchar(25));" 
#     c1.execute(sql2)
#     conn.commit()

# def uploadData():
#     newTable()
#     parseCSV()
#     col_names = ['time','latitude','longitude','depth','mag','magType','nst','gap','dmin','rms','net','id','updated','place','type','horizontalError','depthError','magError','magNst','status','locationSource','magSource']
#     csvData = pd.read_csv('downloaded.csv',names=col_names,header=None)
#     csvData = csvData.where((pd.notnull(csvData)), 0)
#     for i, row in csvData.iterrows():
#         try:
#             sql = "INSERT INTO earthquake (time,latitude,longitude,depth,mag,magType,nst,gap,dmin,rms,net,id,updated,place,type,horizontalError,depthError,magError,magNst,status,locationSource,magSource) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
#             values = (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7],row[8], row[9],row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17],row[18], row[19],row[20],row[21])
#             print(values)
#             c1.execute(sql, values)
#             conn.commit()
#             conn.close
#         except Exception as e:
#             print(e)

                 
# uploadData()