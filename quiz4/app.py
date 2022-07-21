from flask import Flask, render_template, request 
import pymssql
import pprint

app = Flask(__name__)
app.secret_key = "asdgfjhsdgfjhsdgryaesjtrjyetrjyestrajyrtesyjrtdyjrtasdyrtjsejrtestrerty"
header_html = '<html> <head> <title> Quiz4</title> </head> <body> <h1> ID: 1001967237 </h1> <h1> Name: Omkar shrikant gawade </h1> <br />'
server = "test0000@mavs.uta.edu" #please add your azure account id 
user = 'sampleuser' #add your database useranme
password = 'samplepass' # add your database pass 
conn = pymssql.connect(server, user, password, "test") #add your db name at the place of test
c1 = conn.cursor()

@app.route('/', methods=['GET','POST'])
def index():
    data = {'Task':'Value'}
    if request.method == "POST":
        input = request.form['input1']
        if input:
            sql = f"SELECT TOP {input} Place,Mag FROM earthquake ORDER BY mag DESC"
            c1.execute(sql)
            result = c1.fetchall()
            for Place, Mag in result:
                data[Place] = float(Mag)
        elif request.form.get('n'):
            # from_mag = float(request.form['low'])
            # to_mag = float(request.form['high'])
            n = int(request.form['n'])
            cal = float((211-8)/n)
            print(cal)
            sql = "SELECT c from data"
            c1.execute(sql)
            result = c1.fetchall()
            output=[result[i:i + n] for i in range(0, len(result), n)]
            print(output)
            while result:
                data[n] = result[0]
            print(data)
            # while(start <= to_mag):
            #     sql = "SELECT COUNT(*) AS COUNT FROM earthquake WHERE MAG BETWEEN " + str(start) + " AND " + str(start + 1)
            #     c1.execute(sql)
            #     result = c1.fetchall()
            #     data[start] = result[0][0]
            #     start = start + 1
            #     print(data)

    return header_html+render_template("index.html",data=data)

if __name__ == '__main__':
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)

