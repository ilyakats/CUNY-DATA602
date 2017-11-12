# -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 13:49:42 2017

@author: ikats
"""
import pandas as pd
import numpy as np
from re import sub
from decimal import Decimal
from datetime import datetime

from bokeh.layouts import gridplot
from bokeh.plotting import figure, show, output_file
from bokeh.models import Range1d
from bokeh.sampledata.stocks import AAPL, GOOG, IBM, MSFT

def timeconv(x):
    return np.array(x, dtype=np.datetime64)

def currency(x):
    return Decimal(sub(r'[^\d.]', '', x))

trades2 = pd.read_html('http://www.nasdaq.com/symbol/snap/time-sales?pageno=2')
trades1 = pd.read_html('http://www.nasdaq.com/symbol/snap/time-sales?pageno=1')
if len(trades1[5])!=50 and len(trades2[5])!=50:
    # Bad tables
    temp = 1

trades = trades1[5].append(trades2[5], ignore_index=True)
trades.columns = ['time','price','volume']
trades['price'] = trades['price'].apply(currency)

p1 = figure(title="Price of Last 100 Trades (SNAP)")
p1.grid.grid_line_alpha=0.3
#p1.xaxis.axis_label = 'Time'
p1.yaxis.axis_label = 'Price'
p1.x_range = Range1d(100, 0)
p1.line(list(trades.index), list(trades['price']), color='#A6CEE3')
#p1.line(list(trades.index), list(trades['volume']), color='#A6CEE3', legend='Volume')
#p1.line(datetime(IBM['date']), IBM['adj_close'], color='#33A02C', legend='IBM')
#p1.line(datetime(MSFT['date']), MSFT['adj_close'], color='#FB9A99', legend='MSFT')
p1.legend.location = "top_left"

#aapl = np.array(AAPL['adj_close'])
#aapl_dates = np.array(AAPL['date'], dtype=np.datetime64)

#window_size = 30
#window = np.ones(window_size)/float(window_size)
#aapl_avg = np.convolve(aapl, window, 'same')

p2 = figure(title="Volume of Last 100 Trades (SNAP)")
p2.grid.grid_line_alpha = 0
#p2.xaxis.axis_label = 'Date'
p2.yaxis.axis_label = 'Volume'
#p2.ygrid.band_fill_color = "olive"
#p2.ygrid.band_fill_alpha = 0.1
p2.x_range = Range1d(100, 0)

#p2.circle(aapl_dates, aapl, size=4, legend='close',
#          color='darkgrey', alpha=0.2)
p2.line(list(trades.index), list(trades['volume']), color='#33A02C')

#p2.line(aapl_dates, aapl_avg, legend='avg', color='navy')
p2.legend.location = "top_left"



output_file("stocks.html", title="stocks.py example")

show(gridplot([[p1],[p2]], plot_width=400, plot_height=200))  # open a browser