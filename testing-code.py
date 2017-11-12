# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 13:14:06 2017

@author: ikats
"""

# Connecting to MongoDB
from pymongo import MongoClient
client = MongoClient("mongodb://trader:traderpw@data602-shard-00-00-thsko.mongodb.net:27017,data602-shard-00-01-thsko.mongodb.net:27017,data602-shard-00-02-thsko.mongodb.net:27017/test?ssl=true&replicaSet=Data602-shard-0&authSource=admin")
db = client.web_trader
symbols = db.symbols

# Testing adding one record manually
sym = {"symbol":"PIH",
       "name":"1347 Property Insurance Holdings, Inc.",
       "sector":"Finance",
       "industry":"Property-Casualty Insurers",
       "nasdaq_link":"http://www.nasdaq.com/symbol/pih"}
sym_id = symbols.insert_one(sym).inserted_id
sym_id

# Reading from MongoDB
import pprint
pprint.pprint(symbols.find_one())
pprint.pprint(symbols.find_one({"symbol": "AAPL"}))
pprint.pprint(symbols.find_one({"symbol": "AMZN"})["name"])
pprint.pprint(symbols.find_one({"_id": sym_id}))
symbols.count()

# Deleting from MongoDB
symbols.delete_one({"_id": sym_id})
symbols.delete_many({})

# Reading CSV into Data Frame and writing to MongoDB
import pandas as pd
symbolsDF = pd.read_csv("C:/Users/ikats/OneDrive/Documents/GitHub/data602-assignment2/companylist.csv")
symbolsDF = symbolsDF.iloc[:,[0,1,6,7,8]]
symbolsDF.columns = ["symbol","name","sector","industry","nasdaq_link"]
symbolsDF.tail(5).to_dict('records')
symbols.insert_many(symbolsDF.to_dict('records'))

# Reading from MongoDB to Data Frame
symDF = pd.DataFrame(list(symbols.find({})))
del symDF['_id']
symDF.loc[:,["symbol","name"]].head(5)

# Closing connection
client.close
t