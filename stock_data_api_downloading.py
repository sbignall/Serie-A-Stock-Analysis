#!/usr/bin/env python
# coding: utf-8

# In[2]:


#   Necessary imports


import os
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
from pandas_datareader import data as pdr
from datetime import date


# In[15]:


#   Downloading stock data throughout serie a seasons 2018/19 and 2019/2020


start_sa1 = datetime(2017,8,10 )       
end_sa1 = datetime(2018,5,26)           
start_sa2 = datetime(2018,8,13)         
end_sa2 = datetime(2019,6,4)           


juvedata1718 = yf.download('JUVE.MI', start = start_sa1, end = end_sa1)
juvedata1819 = yf.download('JUVE.MI', start = start_sa2, end = end_sa2)
romdata1718 = yf.download('ASR.MI', start = start_sa1, end = end_sa1)
romdata1819 = yf.download('ASR.MI', start = start_sa2, end = end_sa2)
lazdata1718 = yf.download('SSL.MI', start = start_sa1, end = end_sa1)
lazdata1819 = yf.download('SSL.MI', start = start_sa2, end = end_sa2)


# In[16]:


#   Creating function removing unnecessary columns and querying for missing values


def drop(df):
    df = df.drop(columns = ['Open','High','Low','Adj Close', 'Volume'])
    print(df.isna().sum())
    return df


# In[17]:


#   Calling the function


juvedata1718 = drop(juvedata1718)
juvedata1819 = drop(juvedata1819)
romdata1718 = drop(romdata1718)
romdata1819 = drop(romdata1819)
lazdata1718 = drop(lazdata1718)
lazdata1819 = drop(lazdata1819)


# In[18]:


#   Creating lists of stock data for the two different seasons


seriea11 = [juvedata1718, romdata1718, lazdata1718]
seriea22 = [juvedata1819, romdata1819, lazdata1819]


# In[19]:


#   Checking that the indexes match


for serie1 in seriea11:
    print(len(serie1.index.difference(juvedata1718.index)))


# In[20]:


for serie2 in seriea22:
    print(len(serie2.index.difference(juvedata1819.index)))


# In[21]:


def formatstock(df):
    df.columns.values[0:3] = ['juve', 'roma', 'lazio']
    df = df.reset_index()
    df['Date'] = pd.to_datetime(df['Date'])
    return df


# In[22]:


#   Concatting resultant lists and then applying formatting


seriea1718_stock = formatstock(pd.concat(seriea11, axis=1))
seriea1819_stock = formatstock(pd.concat(seriea22, axis=1))


# In[23]:


#   Creating new dataframes of all dates from the start - end of season (stock data does not cover the whole week of course)


date1819 = pd.DataFrame({'Date':pd.date_range(start='2018-08-13', end='2019-06-04')})
date1718 = pd.DataFrame({'Date':pd.date_range(start='2017-08-19', end='2018-05-26')})


# In[24]:


#   Creating another two new dataframes, merging stock data from the stock dataframe to the continuous date dataframe 


seriea1819 = pd.merge(date1819['Date'],seriea1819_stock[['Date','juve', 'roma', 'lazio']],on='Date', how='left')

seriea1718 = pd.merge(date1718['Date'],seriea1718_stock[['Date','juve', 'roma', 'lazio']],on='Date', how='left')


# In[25]:


#   Filling missing stock values for inactive market days with previous days data

seriea1819 = seriea1819.fillna(method='ffill')
seriea1718 = seriea1718.fillna(method='ffill')


# In[26]:


#   Exporting final datasets to csv's


seriea1819.to_csv('seriea1819.csv', index = False)
seriea1718.to_csv('seriea1718.csv', index = False)


# In[ ]:




