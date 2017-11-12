# Assignment 2 template code
# Jamiel Sheikh

# Resources:
# https://code.tutsplus.com/tutorials/creating-a-web-app-from-scratch-using-python-flask-and-mysql--cms-22972
# https://www.w3schools.com/bootstrap/default.asp
# https://www.w3schools.com/bootstrap/bootstrap_buttons.asp


from flask import Flask, render_template, request
import urllib.request as req
import numpy as np
import scipy as sp
import pandas as pd
import matplotlib as mp
from pymongo import MongoClient
#simport plotly
from bs4 import BeautifulSoup

blotter  = pd.DataFrame(columns=['Side','Ticker','Volume','Price','Date','Cash'])

app = Flask(__name__)

def connectDB():
    '''Connects to database.'''
    global db
    
    client = MongoClient("mongodb://trader:traderpw@data602-shard-00-00-thsko.mongodb.net:27017,data602-shard-00-01-thsko.mongodb.net:27017,data602-shard-00-02-thsko.mongodb.net:27017/test?ssl=true&replicaSet=Data602-shard-0&authSource=admin")
    db = client.web_trader

def retrieveBlotter():
    '''Retrieves full Blotter information from the database.'''
    global blotter
    global db

    if db.blotter.count()==0:
        blotter = blotter.iloc[0:0]
    else:
        blotter = pd.DataFrame(list(db.blotter.find({})))
        del blotter['_id']

@app.route("/")
@app.route("/main")
def show_main_page():
    return render_template('main.html')

@app.route("/buy")
def show_trade_screen():
    return render_template('buy.html', defsym='', defamount='', 
                           message='Testing Status')

@app.route("/blotter")
def show_blotter():
    global db
    global blotter
    
    connectDB()
    retrieveBlotter()
  
    return render_template('blotter.html',tables=[blotter.to_html()])

@app.route("/pl")
def show_pl():
    return render_template('pl.html')

@app.route("/submitTrade",methods=['POST'])
def execute_trade():
    symbol = request.form['symbol']
    price = get_quote(symbol)

    # pull quote
    # calculate trade value
    # insert into blotter
    # calculate impact to p/l and cash
    return "You traded at " + price

# Used snippet of Bloomberg scraping as posted on Slack
def get_quote(symbol):
    url = 'https://www.bloomberg.com/quote/' + symbol + ':US'
    page = req.urlopen(url)
    soup = BeautifulSoup(page, 'html.parser')
    price_box = soup.find('div', attrs={'class':'price'})
    price = price_box.text
    return price

@app.route("/sample")
def show_sample():
    return render_template('sample.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0') # host='0.0.0.0' needed for docker
