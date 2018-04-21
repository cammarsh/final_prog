from flask import Flask, render_template




app = Flask(__name__)

@app.route('/', methods = ['GET','POST'])
def rankings():
    name = request.form['year']
    typeType = request.form['type']
