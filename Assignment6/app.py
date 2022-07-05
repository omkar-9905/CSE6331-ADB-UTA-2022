# from flask import Flask, render_template,request
# from flask_socketio import SocketIO

# app = Flask(__name__)
# app.config['SECRET_KEY'] = 'secret!'
# socketio = SocketIO(app)

# users={}

# @app.route('/')
# def index():
#     return render_template('index.html')

# @socketio.on('username',namespace='private')
# def receive_username(username):
#     print('Username added!')

# if __name__ == '__main__':
#     socketio.run(app)

from flask import *
from flask_socketio import *
from matplotlib.pyplot import text
from numpy import broadcast
import random


global score,user_list
score = {}
user_list = {}

# Init the server
app = Flask(__name__)
app.config['SECRET_KEY'] = 'some super secret key!'
socketio = SocketIO(app, logger=True)

# Send HTML!
@app.route('/', methods=['GET','POST'])
def root():
    global pile
    pile = []
    if request.method == "POST":
        input1 = int(request.form['input1'])
        rand_number = lambda x:[random.randint(1,100) for i in range(x)] 
        pile = rand_number(input1)
    return render_template('main_page.html',data=pile)

# Prints the user id
@app.route('/user/<id>')
def user_id(id):
    return str(id)

# Display the HTML Page & pass in a username parameter
@app.route('/html/<username>')
def html(username):
    # user_list[username] = request.sid
    return render_template('index.html', username={'user' :username})

@socketio.on('register_user')
def register_user(data):
    user_list[request.sid] = {'username':data['user'],'score':0}
    print(user_list)
    emit('message_from_server', {'text':f'Game Started Please Enter values from {len(pile)} piles' })

# Receive a message from the front end HTML
@socketio.on('send_message')   
def message_recieved(data):
    if data['text']:
        pileno,stones = data['text'].split(',')
        stones = int(stones)
        pileno = int(pileno)-1
        if pile[pileno] >= stones:
            pile[pileno] = pile[pileno]-stones
            user_list[request.sid]['score'] += stones
            print(user_list)
            emit('message_from_server', {'text':f"Score is {user_list[request.sid]['score']}"})
        elif pile[pileno] < int(stones):
            session_id = max(user_list,key = lambda x: user_list[x]['score'])
            winner = user_list[session_id]['username']
            emit('message_from_server', {'text':f'Winner is {winner}'},broadcast=True)
    else:
        emit('message_from_server', {'text':'Please send "start" to begin' }) #+ request.sid})
    
# Actually Start the App
if __name__ == '__main__':
    """ Run the app. """    
    socketio.run(app, port=8000, debug=True)