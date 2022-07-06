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

def parseCSV(filepath):
    if filepath.endswith('.csv'):
        #newTable()
        col_names=['objects', 'minimum' , 'maximum' , 'picture' , 'charm' ]
        csvData = pd.read_csv(filepath,names=col_names,header=None)
        csvData = csvData.where((pd.notnull(csvData)), 0)
        for i, row in csvData.iterrows():
            if i > 0:
                try:
                    sql = "INSERT INTO test (object, minimum , maximum , picture , charm ) VALUES (%s,%s, %s, %s, %s)"
                    value = (row[0], row[1], row[2], row[3], row[4])
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
    # account_name = 'yxg7510'
    # account_key = 'MMpaw4Ik9LOnBUJe0whabcMm96nA6e0Sw68PzqFtmIZLdJa297OcAkfL8Otc7XZ6KSYK3j+H0iK6+AStby1a5A=='
    # container_name = 'test'
    urls = None
    if request.method == "POST":
        user = request.form['user']
        salaryGrt = request.form['salaryGrt']
        salaryLes = request.form['salaryLes']
        if user:
            names = getCharm(user)
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

def getCharm(charm):
    names = []
    try:
        sql = "SELECT * from test where charm like LIKE :charm", {"charm": '%' + charm + '%'}
        c1.execute(sql)
        names = c1.fetchall()
    except Exception as e:
        print(e)
    return names


def getPicture(name):
    try:
        sql = f"select charm from test where name='{name}'"
        c1.execute(sql)
        names = c1.fetchall()
        for i, name in enumerate(names):
            names[i] = name[0]
            return names
    except:
        flash("IMAGE FILE DOES NOT EXIST")

def salaryGrtquery(maximum):
    try:
        sql = f"select picture from test where salary > {maximum}"
        c1.execute(sql)
        names = c1.fetchall()
        for i,name in enumerate(names):
            names[i] = name[0]
    except:
        pass
    return names

def salaryLesquery(minimum):
    try:
        sql = f"select picture from test where salary < {minimum}"
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
        sql = "SELECT * from test"
        c1.execute(sql)
        names = c1.fetchall()
    except Exception as e:
        print(e)
    return names


@app.route('/edit',methods=['GET','POST'])
def edit():
    if request.method == "POST":
        objects = request.form['objects'].lower()
        minimum = request.form['minimum']
        maximum  = request.form['maximum']
        picture = request.form['picture']
        charm = request.form['charm']

        if request.form['submit_button'] == 'edit':
            try:
                if picture:
                    sql = f"UPDATE test set object = '{objects}',minimum = '{minimum}', maximum = {maximum},picture = '{picture}', charm= '{charm}'  where object = '{objects}'"
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
                    sql = f"UPDATE test set object = '{objects}',minimum = '{minimum}', maximum = {maximum},picture = '{picture}', charm= '{charm}'  where object = '{objects}'"
                    print(sql)
                c1.execute(sql)
                conn.commit()
            except Exception as e:
                print(e)
        elif  request.form['submit_button'] == 'remove':
            sql = f"DELETE FROM test where bject = '{objects}'"
            c1.execute(sql)
            conn.commit()
    names = getNames()
    return render_template("edit.html", names=names)
