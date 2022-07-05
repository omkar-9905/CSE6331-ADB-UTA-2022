#BeautifulSoup4,html5lib,lxml
from pydoc import doc
import string
from tkinter.font import names
import pandas as pd
import urllib.request
import ssl,os
import re,requests
import nltk
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from flask import Flask,render_template,request,redirect
import pymssql

def browse_data():
    links = ['https://www.gutenberg.org/cache/epub/34/pg34.html',
        'https://www.gutenberg.org/files/67747/67747-h/67747-h.htm']
    ssl._create_default_https_context = ssl._create_unverified_context
    tmp = []
    for link in links:
        with urllib.request.urlopen(link) as webPageResponse:
	        #outputHtml = webPageResponse.read()
            outputHtml = webPageResponse.read()
            data = outputHtml.decode("utf-8").split(' ')
            tmp.append(data_cleaner(data))
    return tmp

def file_read():
    docs = []
    tmp = []
    for file in os.listdir('./books'):
        if file.endswith('.txt'):
            docs.append('./books/'+file)
    for doc in docs:
        with open(doc) as file:
            data = file.read().split(' ')
            tmp.append(data_cleaner(data))
    return tmp

def data_cleaner(data):
    filtered_words = []
    for raw in data:
        document_test = re.sub(r'[^\x00-\x7F]+','', raw)
        document_test = re.sub(r'@\w+','', document_test)
        document_test = re.sub(r'[%s]' % re.escape(string.punctuation), '', document_test)
        document_test = document_test.lower()
        document_test = re.sub(r'[0-9]', '', document_test)
        document_test = re.sub(r'\s{2,}', '', document_test)
        filtered_words.append(document_test)
    filtered_words = [word for word in filtered_words if word not in stopwords.words('english')]
    filterd_string = ' '.join(filtered_words)
    return filterd_string


def build_index():
    global vectorizer
    global df
    data = file_read()
    X = vectorizer.fit_transform(data)
    X = X.T.toarray()
    df = pd.DataFrame(X, index=vectorizer.get_feature_names_out())


# global vectorizer
# global df
# vectorizer = TfidfVectorizer(ngram_range=(2,2))
# df = None

# build_index()
app = Flask(__name__)
app.secret_key = "asdgfjhsdgfjhsdgryaesjtrjyetrjyestrajyrtesyjrtdyjrtasdyrtjsejrtestrerty"
header_html = '<html> <head> <title> Assignment2</title> </head> <body> <h1> ID: 1001967237 </h1> <h1> Name: Omkar shrikant gawade </h1> <br />'

def get_similar_articles(q):
    global vectorizer
    global df
    filenames = os.listdir('./books') 
    q = [q]
    q_vec = vectorizer.transform(q).toarray().reshape(df.shape[0],)
    sim = {}
    for i in range(df.shape[1]):
        sim[filenames[i]] = np.dot(df.loc[:, i].values, q_vec) / np.linalg.norm(df.loc[:, i]) * np.linalg.norm(q_vec)
    print(sim)
    sim_sorted = sorted(sim.items(), key=lambda x: x[1], reverse=True)
    for k, v in sim_sorted:
        if v != 0.0:
            print("Similar :", v)
            print(k)
            print()
    return sim_sorted


@app.route('/search',methods=['GET','POST'])
def index():
    data = None
    if request.method == "POST":
        input = request.form['input']
        if input:
            # data =  get_similar_articles(input)
            data = file_read()
    return header_html+render_template("index.html",data=data)

if __name__ == '__main__':
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)