from fileinput import filename
from ipaddress import IPV4LENGTH
from logging import exception
from flask import Flask, render_template, request, redirect, url_for, flash
import azure.core.exceptions
import os, os.path
from datetime import datetime, timedelta
import urllib
import pandas as pd
from os.path import join, dirname, realpath
import pymssql
from sqlalchemy import create_engine
from azure.storage.blob import BlobClient,generate_blob_sas, BlobSasPermissions,PublicAccess,BlobServiceClient
import urllib.request

app = Flask(__name__)
#secret key could be any string 
app.secret_key = "asdgfjhsdgfjhsdgryaesjtrjyetrjyestrajyrtesyjrtdyjrtasdyrtjsejrtestrerty"

UPLOAD_FOLDER = 'static/files'
app.config['UPLOAD_FOLDER'] =  UPLOAD_FOLDER

server = "test0000@mavs.uta.edu" #please add your azure account id 
user = 'sampleuser' #add your database useranme
password = 'samplepass' # add your database pass 
conn = pymssql.connect(server, user, password, "test") #add your db name at the place of test
c1 = conn.cursor()

account_name = 'test0000' #add account name 
'''
reference for where to find account key and in place it below
https://docs.microsoft.com/en-us/azure/storage/common/storage-account-keys-manage?tabs=azure-portal 
'''
account_key = 'samplekey' 
container_name = 'test'
'''
reference for how to find connections string and place it below
https://docs.microsoft.com/en-us/azure/storage/common/storage-configure-connection-string
'''
connection_string = 'DefaultEndpointsProtocol=https;AccountName=test0000;AccountKey=samplekey;EndpointSuffix=core.windows.net'


path = 'static/files'

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/uploadFile', methods=['GET', 'POST'])
def uploadFile():
    if request.method == "POST":
        file_names = os.listdir(path)
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
            if not file_path.endswith(('.csv','.png','.jpg','.jpeg')):
                flash('File not in proper format')
            else:
                uploaded_file.save(file_path)
                parseCSV(file_path)
    return render_template("upload.html")

def newTable():
    sql1 = "DROP TABLE IF EXISTS users"
    c1.execute(sql1)
    conn.commit()
    sql2 = "create table users(name varchar(10), state varchar(5), salary int, grade varchar(5), room int, telnum int, picture varchar(20), keywords varchar(100) primary key (name));"
    c1.execute(sql2)
    conn.commit()

def parseCSV(filepath):
    if filepath.endswith('.csv'):
        newTable()
        col_names=['name','state','salary','grade','room','telnum','picture','keywords']
        csvData = pd.read_csv(filepath,names=col_names,header=None)
        csvData = csvData.where((pd.notnull(csvData)), 0)
        for i, row in csvData.iterrows():
            if i > 0:
                try:
                    sql = "INSERT INTO users (name,state, salary,grade, room, telnum, picture, keywords) VALUES (%s,%s, %s, %s, %s, %s, %s, %s)"
                    value = (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
                    c1.execute(sql, value)
                    conn.commit()
                    conn.close
                except Exception as e:
                    print(e)
        flash('File Uploaded')

    elif filepath.endswith(('.png','.jpg','.jpeg')):
        # file_names = os.listdir(path)
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)
        _,blob_name =  os.path.split(filepath)
        # for file_name in file_names:
        #     if file_name.endswith(('.png','.jpg')):
        #         blob_name = file_name
        #         file_path = path+'/'+file_name
        blob_client = container_client.get_blob_client(blob_name)
        try:
            with open(filepath, "rb") as data:
                blob_client.upload_blob(data, blob_type="BlockBlob", overwrite=False)
            flash('File Uploaded')
        except azure.core.exceptions.ResourceExistsError as e:
            print(e)
            flash("Image already present")
    else:
        pass

@app.route('/search', methods=['GET','POST'])
def search():
    urls = None
    if request.method == "POST":
        user = request.form['user']
        salaryGrt = request.form['salaryGrt']
        salaryLes = request.form['salaryLes']
        if user:
            names = getPicture(user)
            print(names)
        elif salaryGrt:
            names = salaryGrtquery(salaryGrt)
        else:
            names = salaryLesquery(salaryLes)
        urls = []
        if names == [' '] or names == None or names == ['']:
            flash('Image not present')
        else:
            for name in names:
                blob_name = name
                blob = get_blob_sas(account_name, account_key, container_name, blob_name)
                url = 'https://' + account_name + '.blob.core.windows.net/' + container_name + '/' + blob_name + '?' + blob
                urls.append(url)
    return render_template('search.html',urls=urls)

def getPicture(name):
    try:
        sql = f"select picture from users where name='{name}'"
        c1.execute(sql)
        names = c1.fetchall()
        for i, name in enumerate(names):
            names[i] = name[0]
            return names
    except:
        flash("IMAGE FILE DOES NOT EXIST")

def salaryGrtquery(salaryGrt):
    try:
        sql = f"select picture from users where salary > {salaryGrt}"
        c1.execute(sql)
        names = c1.fetchall()
        for i,name in enumerate(names):
            names[i] = name[0]
    except:
        pass
    return names

def salaryLesquery(salaryLes):
    try:
        sql = f"select picture from users where salary < {salaryLes}"
        c1.execute(sql)
        names = c1.fetchall()
        for i,name in enumerate(names):
            names[i] = name[0]
    except:
        pass
    return names

def get_blob_sas(account_name, account_key, container_name, blob_name):
    sas_blob = generate_blob_sas(account_name=account_name,
                                 container_name=container_name,
                                 blob_name=blob_name,
                                 account_key=account_key,
                                 permission=BlobSasPermissions(read=True),
                                 expiry=datetime.utcnow() + timedelta(hours=2))
    return sas_blob

def getNames():
    names = []
    try:
        sql = "SELECT * from users"
        c1.execute(sql)
        names = c1.fetchall()
    except Exception as e:
        print(e)
    return names


@app.route('/edit',methods=['GET','POST'])
def edit():
    if request.method == "POST":
        name = request.form['name'].lower()
        state = request.form['state']
        salary = request.form['salary']
        grade = request.form['grade']
        room = request.form['room']
        telnum = request.form['telnum']
        picture = request.form['picture']
        keywords = request.form['keywords']
        if request.form['submit_button'] == 'edit':
            try:
                if picture:
                    sql = f"UPDATE users set name = '{name}',state = '{state}', salary = {salary},grade = '{grade}', room={room},telnum={telnum},picture='{picture}',keywords='{keywords}' where name = '{name}'"
                    file_name = request.form['picture']
                    if file_name.endswith(('.png','.jpg')):
                        blob_name = file_name
                        file_path = path + '/' + file_name
                        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
                        container_client = blob_service_client.get_container_client(container_name)
                        blob_client = container_client.get_blob_client(blob_name)
                        with open(file_path, "rb") as data:
                            blob_client.upload_blob(data, blob_type="BlockBlob", overwrite=True)
                else:
                    sql = f"UPDATE users set name = '{name}',state = '{state}', salary = {salary},grade = '{grade}', room={room},telnum={telnum},picture='{picture}',keywords='{keywords}' where name = '{name}'"
                    print(sql)
                c1.execute(sql)
                conn.commit()
            except Exception as e:
                print(e)
        elif  request.form['submit_button'] == 'remove':
            sql = f"DELETE FROM users where name='{name}'"
            c1.execute(sql)
            conn.commit()
    names = getNames()
    return render_template("edit.html", names=names)
