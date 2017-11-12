# -*- coding: utf-8 -*-
"""
Web-Based Equities Trading System
DATA 602 Assignment 2 / Prof. Jamiel Sheikh

TBD

Created October/November 2017
@author: Ilya Kats
"""


# Required libraries
import urllib.request as req
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from pymongo import MongoClient


# Global variables
symbols = ('AAPL','AMZN','MSFT','INTC','SNAP')
menu = ['[B]uy','[S]ell','Show [P]/L','Show Blotte[r]','[Q]uit']
initial_cash = 10000000.00
cash = 0.00
blotter  = pd.DataFrame(columns=['Side','Ticker','Volume','Price','Date','Cash'])
pl = pd.DataFrame(columns=['Ticker','Position','WAP','RPL'])


# Stock price is extracted from Yahoo! Finance page.
# Rather than extracting display value from HTML,
# the price is extracted from data stored in JavaScript code.
def getPrice(symbol):
    '''
    Gets current market price. 
    
    Args:
        symbol: Ticker symbol.
    Returns:
        Current stock price for a symbol from Yahoo! Finance or 
        -1 if price could not be extracted.
    '''
    price = -1
    
    url = 'https://finance.yahoo.com/quote/'+symbol
    page = req.urlopen(url).read()
    soup = BeautifulSoup(page, 'html.parser')
    scripts = soup.findAll('script')
    # Cycle through all script blocks to find the one with data
    # Ideally, data in JSON format should be properly converted and read
    # Here it is simply extracted with string functions
    for s in scripts:
        pos = s.text.find('currentPrice')
        if pos>0:
            sPrice = s.text[pos:s.text.find(',',pos)]
            try:
                price = float(sPrice[sPrice.rfind(':')+1:])
            except ValueError:
                return -1
            break
    return price


def showBlotter():
    '''Displays entire blotter'''
    print('\nCURRENT BLOTTER')
    print('{:<5s} {:<7s} {:>8s} {:>10s} {:>30s} {:>15s}'.format(
            'Side','Ticker','Volume','Price','Date and Time','Cash')
    )
    for index, row in blotter.iterrows():
        print('{:<5s} {:<7s} {:>8d} {:>10.2f} {:>30s} {:>15.2f}'.format(
                row['Side'],
                row['Ticker'],
                row['Volume'],
                row['Price'],
                str(row['Date']),
                row['Cash']
                ))
    if blotter.empty:
        print('[No Trades Recorded]')
    print('')


# Using same function for calculating UPL and RPL since the formula is the same
def getPL(position, price, wap):
    '''Calculates UPL or RPL based on position/volume, market/sell price and WAP.'''
    return (position*(price-wap))


def updateWAP(currentWAP, currentPosition, price, volume):
    '''Calculates new WAP based on previous WAP and new buy information.'''
    return ((currentWAP*currentPosition)+(price*volume))/(currentPosition+volume)


# Display current P/L with refreshed market price
def showPL():
    '''Displays current P/L with updated market price.'''
    print('\nCURRENT P/L')
    print('{:<7s} {:>10s} {:>10s} {:>10s} {:>10s} {:>10s}'.format(
            'Ticker','Position','Market','WAP','UPL','RPL')
    )
    for index, row in pl.iterrows():
        price = getPrice(row['Ticker'])
        print('{:<7s} {:>10d} {:>10.2f} {:>10.2f} {:>10.2f} {:>10.2f}'.format(
                row['Ticker'],
                row['Position'],
                price,
                row['WAP'],
                getPL(row['Position'], price, row['WAP']),
                row['RPL'])
        )
    if pl.empty:
        print('[Holding no positions]')
    print('Cash: ${:,.2f}\n'.format(cash))


def getShares(side):
    '''Prompt for and return number of shares to buy or sell. 
    Argument is either "buy" or "sell".'''
    
    shares = input('Enter number of shares to {:s}: '.format(side))
    try:
        numShares = int(shares)
    except ValueError:
        print ('Invalid number of shares.\n')
        return -1
    if numShares<0:
        print ('Invalid number of shares. Must be positive.\n')
        return -1
    return numShares


def getSymbol(side):
    '''Prompt for and return stock symbol to buy or sell. 
    Argument is either "buy" or "sell".'''
    
    symbol = input('Enter stock symbol to {:s}: '.format(side)).upper()
    if symbol not in symbols:
        print ('Invalid symbol. Valid symbols:')
        for s in symbols:
            print(s, end=" ")
        print('\n')
        return ''
    return symbol


def doBuy(symbol, volume):
    '''
    Buys given amount of selected stock. 
    
    Args:
        symbol: Stock to purchase.
        volume: Number of shares to purchase.
    Returns: 
        TRUE if successful and FALSE otherwise.
    '''
    global cash
    global blotter
    global pl
    global db
    
    # Check that it's a valid symbol
    if symbol not in symbols:
        print ('Buy unsuccessful. Not a valid symbol ({:s}).\n'.format(symbol))
        return False
    
    # Refresh price to get most up to date information
    price = getPrice(symbol)
    if price<0:
        print ('Buy unsuccessful. Could not get valid market price.\n')
        return False
        
    # Check that have enough cash 
    if (volume*price)>cash:
        print ('Buy unsuccessful. Not enough cash.\n')
        return False

    # Perform buy - add to P/L and adjust cash position
    if symbol in pl.index:        
        pl.at[symbol,'WAP'] = updateWAP(pl.loc[symbol]['WAP'], 
             pl.loc[symbol]['Position'], 
             price, volume)
        pl.at[symbol,'Position'] += volume
    else:
        entry = pd.DataFrame([[symbol,volume,updateWAP(0,0,price,volume),0]],
                               columns=['Ticker','Position','WAP','RPL'],
                               index=[symbol])
        pl = pl.append(entry)
    savePL()
    cash -= volume*price
    saveCash()
    
    # Add to blotter
    entry = pd.DataFrame([['Buy',symbol,volume,price,datetime.now(),cash]], 
                           columns=['Side','Ticker','Volume','Price','Date','Cash'])
    blotter = blotter.append(entry, ignore_index=True)
    db.blotter.insert_one(entry.to_dict('records')[0])
    
    # Output status
    print ('Buy successful. Purchased {:,d} shares of {:s} at ${:,.2f}.\n'.format(volume, symbol, price))
    return True
     

def doSell(symbol, volume):
    '''
    Sells given amount of selected stock. 
    
    Args:
        symbol: Stock to sell.
        volume: Number of shares to sell.
    Returns: 
        TRUE if successful and FALSE otherwise.
    '''
    global cash
    global blotter
    global pl
    global db
    
    # Check that it's a valid symbol
    if symbol not in symbols:
        print ('Sell unsuccessful. Not a valid symbol ({:s}).\n'.format(symbol))
        return False
    
    # Check that have any shares
    if symbol not in pl.index:
        print ('Sell unsuccessful. Not holding ({:s}).\n'.format(symbol))
        return False
    
    # Check that have enough shares
    if volume>pl.loc[symbol]['Position']:
        print ('Sell unsuccessful. Not enough shares.\n')
        return False
    
    # Refresh price to get most up to date information
    price = getPrice(symbol)
    if price<0:
        print ('Sell unsuccessful. Could not get valid market price.\n')
        return False
    
    # Perform sell
    pl.at[symbol,'RPL'] += getPL(volume, price, pl.loc[symbol]['WAP'])
    pl.at[symbol,'Position'] -= volume
    cash += volume*price
    saveCash()
    # Reset WAP if closing the position
    if pl.loc[symbol]['Position']==0:
        pl.at[symbol,'WAP']=0
    savePL()
    # Add to blotter
    entry = pd.DataFrame([['Sell',symbol,volume,price,datetime.now(),cash]], 
                           columns=['Side','Ticker','Volume','Price','Date','Cash'])
    blotter = blotter.append(entry, ignore_index=True)
    db.blotter.insert_one(entry.to_dict('records')[0])
    
    # Output status
    print ('Sell successful. Sold {:,d} shares of {:s} at ${:,.2f}.\n'.format(volume, symbol, price))
    return True


def showMenu():
    '''Displays main menu and prompts for choice. Returns valid choice.'''
    while True:
        print(' - ', end='')
        for i in menu:
            print(i, end=' - ')
        print('')
        option = input('Select option: ').upper()
        if option in ['1','2','3','4','5','B','S','P','R','Q','1929']:
            return option
        print('Invalid choice. Please try again.\n')


def connectDB():
    '''Connects to database.'''
    global db
    
    client = MongoClient("mongodb://trader:traderpw@data602-shard-00-00-thsko.mongodb.net:27017,data602-shard-00-01-thsko.mongodb.net:27017,data602-shard-00-02-thsko.mongodb.net:27017/test?ssl=true&replicaSet=Data602-shard-0&authSource=admin")
    db = client.web_trader

def retrievePL():
    '''Retrieves full P/L information from the database.'''
    global pl
    global db

    if db.pl.count()==0:
        initializePL()
    else:
        pl = pd.DataFrame(list(db.pl.find({})))
        del pl['_id']
        pl.index = pl['Ticker']


def savePL():
    '''Saves full P/L information to the database.'''
    global pl
    global db
    
    if db.pl.count()>0:
        db.pl.delete_many({})
    if not pl.empty:
        db.pl.insert_many(pl.to_dict('records'))
  

def retrieveBlotter():
    '''Retrieves full Blotter information from the database.'''
    global blotter
    global db

    if db.blotter.count()==0:
        blotter = blotter.iloc[0:0]
    else:
        blotter = pd.DataFrame(list(db.blotter.find({})))
        del blotter['_id']

def initializePL():
    '''Resets P/L.'''
    global pl
    pl = pl.iloc[0:0]


def saveCash():
    '''Saves cash value in the database.'''
    global cash
    global db
    
    if db.cash.count()==0:
        db.cash.insert_one(dict([('position',cash)]))
    else:
        db.cash.update_one({},{'$set':dict([('position',cash)])},
                           upsert=False)
    

def retrieveCash():
    '''Retrieves cash value from the database.'''
    global cash
    global db
    
    if db.cash.count()==0:
        cash = initial_cash
        saveCash()
    else:
        cash = db.cash.find_one()['position']


def main():
    pass

    print('************************************************')
    print('*  LITTLE WEB CONSOLE EQUITIES TRADING SYSTEM  *')
    print('*       Data 602               Ilya Kats       *')
    print('************************************************')
    print('\nInformation is provided for illustrative purposes only.')
    print('Market price from Yahoo! Finance is delayed.\n')
    
    # Initialize environment
    global cash
    global blotter
    global pl
    
    # Connect to database and 
    connectDB()
    retrievePL()
    retrieveBlotter()
    retrieveCash()
    
    choice = ''
    while choice!='5' and choice!='Q':
        choice = showMenu()
        if choice=='B' or choice=='1':
            symbol = getSymbol('buy')
            if symbol!='':
                shares = getShares('buy')
                if shares>0:            
                    doBuy(symbol, shares)
        elif choice=='S' or choice=='2':
            symbol = getSymbol('sell')
            if symbol!='':
                shares = getShares('sell')
                if shares>0:            
                    doSell(symbol, shares)
        elif choice=='P' or choice=='3':
            showPL()
        elif choice=='R' or choice=='4':
            showBlotter()
    print('\nThank you for using Little Console Equities Trading System!')

if __name__ == '__main__':
  main()