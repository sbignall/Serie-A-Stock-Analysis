#!/usr/bin/env python
# coding: utf-8

# In[1]:




###                 Creating CSV files of dataframes containing match results, match dates and competitions                 ###


# In[1]:


#   Importing necessary libraries and setting working directory


import pandas as pd
import numpy as np
from datetime import datetime
from pandas_datareader import data as pdr
import requests as req
from dateutil.parser import parse
import datetime
import re
import os


# In[2]:


#   Getting urls. Note: need to pretend to be using browser to scrape data here


urljuve1718 = "https://www.transfermarkt.co.uk/juventus-fc/spielplan/verein/506/plus/0?saison_id=2017"
urljuve1819 = "https://www.transfermarkt.co.uk/juventus-fc/spielplan/verein/506/plus/0?saison_id=2018"
urlroma1718 = "https://www.transfermarkt.co.uk/as-rom/spielplan/verein/12/saison_id/2017"
urlroma1819 = "https://www.transfermarkt.co.uk/as-rom/spielplan/verein/12/saison_id/2018"
urllazio1718 = "https://www.transfermarkt.co.uk/lazio-rom/spielplan/verein/398/saison_id/2017"
urllazio1819 = "https://www.transfermarkt.co.uk/lazio-rom/spielplan/verein/398/saison_id/2018"

hdr = {'User-Agent': 'Mozilla/5.0'}


# In[3]:


#   Downloading data, checking status codes

pagejuve1718 = req.get(urljuve1718, headers = hdr)
print("Status code: ", pagejuve1718)
pagejuve1819 = req.get(urljuve1819, headers = hdr)
print("Status code: ", pagejuve1819)
pageroma1718 = req.get(urlroma1718, headers = hdr)
print("Status code: ", pageroma1718)
pageroma1819 = req.get(urlroma1819, headers = hdr)
print("Status code: ", pageroma1819)
pagelazio1718 = req.get(urllazio1718, headers = hdr)
print("Status code: ", pagelazio1718)
pagelazio1819 = req.get(urllazio1819, headers = hdr)
print("Status code: ", pagelazio1819)


# In[4]:


#   Creating lists of results tables using pandas read_html


juvetables1819 = pd.read_html(pagejuve1819.content)
juvetables1718 = pd.read_html(pagejuve1718.content)
romatables1819 = pd.read_html(pageroma1819.content)
romatables1718 = pd.read_html(pageroma1718.content)
laziotables1819 = pd.read_html(pagelazio1819.content)
laziotables1718 = pd.read_html(pagelazio1718.content)


# In[5]:


#   Creating function to check which tables have column 'Matchday' in them, as these will include results

def matchday(list):
    for i, item in enumerate(list):
        for i2, column in enumerate(item.columns):
            if item.columns[i2] == 'Matchday':
                print('Matchday in Indices:', i)


# In[6]:


#   Results of function show which tables are necessary and check that the competition column has been added


matchday(juvetables1819)   #   Indices 2,3,4,5
print('---------------------')
matchday(juvetables1718)   #   Indices 2,3,4,5
print('---------------------')
matchday(romatables1819)   #   Indices 2,3,4
print('---------------------')
matchday(romatables1718)   #   Indices 2,3,4
print('---------------------')
matchday(laziotables1819)   #   Indices 2,3,4
print('---------------------')
matchday(laziotables1718)   #   Indices 2,3,4,5


# In[7]:


#   Getting rid of unnecessary tables from lists


juvetables1819 = juvetables1819[2:6]
juvetables1718 = juvetables1718[2:6]
romatables1819 = romatables1819[2:5]
romatables1718 = romatables1718[2:5]
laziotables1819 = laziotables1819[2:5]
laziotables1718 = laziotables1718[2:6]


# In[8]:


#   Creating new competition column in dataframes

def competitioncl(list):
    for i, item in enumerate(list):
        list[i]['Competition'] = ""
    return list


# In[9]:


#   Filling competition depending on keywords 
#   Keywords are visible on first column and row in tables on website

def competitioncl2(list):
    for i, item in enumerate(list):
        w = isinstance(list[i].iloc[0,0], np.int64)
        if w == True:
            for i2, row in item.iterrows():
                list[i].loc[i2, 'Competition'] = 'League'
        else:
            x = list[i].iloc[0,0].startswith('Group')
            y = list[i].iloc[0,0].startswith('Round')
            z = list[i].iloc[0,0].startswith('Final')
            n = list[i].iloc[0,0].startswith('group')
            for i2, row in item.iterrows():
                if x == True:
                    list[i].loc[i2, 'Competition'] = 'European'
                elif y == True: 
                    list[i].loc[i2, 'Competition'] = 'Acup'
                elif z == True:
                    list[i].loc[i2, 'Competition'] = 'Acup'
                elif n == True:
                    list[i].loc[i2, 'Competition'] = 'European'
                    
    return list


# In[10]:


#   Applying both functions to lists


juvetables1819 = competitioncl(juvetables1819)
juvetables1819 = competitioncl2(juvetables1819)

juvetables1718 = competitioncl(juvetables1718)
juvetables1718 = competitioncl2(juvetables1718)

romatables1819 = competitioncl(romatables1819)
romatables1819 = competitioncl2(romatables1819)

romatables1718 = competitioncl(romatables1718)
romatables1718 = competitioncl2(romatables1718)

laziotables1819 = competitioncl(laziotables1819)
laziotables1819 = competitioncl2(laziotables1819)

laziotables1718 = competitioncl(laziotables1718)
laziotables1718 = competitioncl2(laziotables1718)


# In[11]:


#   Creating function to trim down to only necessary columns


def unnecessary(xs):
    for idx, x in enumerate(xs):
        xs[idx] = xs[idx].filter(items = ['Date', 'Ranking', 'Venue', 'Result', 'Competition'])
    return xs


# In[12]:


#   Still keeping lists separate so as to more easily work out individual data points later


juvetables1819 = unnecessary(juvetables1819)
juvetables1718 = unnecessary(juvetables1718)
romatables1819 = unnecessary(romatables1819)
romatables1718 = unnecessary(romatables1718)
laziotables1819 = unnecessary(laziotables1819)
laziotables1718 = unnecessary(laziotables1718)


# In[14]:


#   Creating function for concatting dataframes together

def concatting(list):
    for i, item in enumerate(list):
        if i == 0:
            pass                                                                   # No need to concatenate first dataframe
        elif i > 0:
            list[i] = pd.concat([list[i], list[i-1]], ignore_index = True)         # Concat each dataframe with previous
    return list[-1]                                                                # Only output last dataframe


# In[15]:


juveres1819 = concatting(juvetables1819)
juveres1718 = concatting(juvetables1718)
romares1819 = concatting(romatables1819)
romares1718 = concatting(romatables1718)
laziores1819 = concatting(laziotables1819)
laziores1718 = concatting(laziotables1718)


# In[16]:


#   Checking each one for incorrectly formatted results, dates, etc


def format_check(df):
    for i, row in df.iterrows():
        is_matched3 = re.match("[0-9][:][0-9]$", df.iloc[i, 3])
        if not is_matched3:
            print('Check score at:', i)
        try: checkformat = pd.to_datetime(pd.Series(df.iloc[i,0]))
        except:
            print('Check date at:', i)
            pass


# In[17]:


format_check(juveres1819)
format_check(juveres1718)       
format_check(romares1819)       #   Index 47 needs score checked   (Formatted as '3:1 AET')
format_check(romares1718)
format_check(laziores1819)      #   Index 1 needs score checked    (Formatted as '4:5 on pens')
format_check(laziores1718)


# In[18]:


#   Scores manually entered as they are small in number



romares1819.loc[47, 'Result'] = '3:1'

laziores1819.loc[1, 'Result'] = '4:5'

laziores1718.loc[3, 'Result'] = '4:5'


# In[19]:


#   Creating empty column 'results' to fit results (converted to W, D or L)
#   Re-adding 'Matchday' column, this time including all competitions, for later statistical testing


juveres1819[['results', 'Matchday']] = ""
juveres1718[['results', 'Matchday']] = ""
romares1819[['results', 'Matchday']] = ""
romares1718[['results', 'Matchday']] = ""
laziores1819[['results', 'Matchday']] = ""
laziores1718[['results', 'Matchday']] = ""


# In[20]:


#   'Result' column is split into two separate columns for score, 
#   W L D calculated through mathematical comparison between columns, taking into consideration Venue (home or away) 
#   'results' column kept, 'Result' and comparison columns dropped, 'Ranking' column strings cleaned up a bit


def resultsandranking(df):
    df[['1', '2']] =  df['Result'].str.split(':', expand=True).astype('int64')
    for i, row in df.iterrows():
        if df.iloc[i, 2] == 'H':
            if df.iloc[i, 7] > df.iloc[i, 8]:
                df.iloc[i, 5] = 'W'
            elif df.iloc[i, 7] < df.iloc[i, 8]:
                 df.iloc[i, 5] = 'L'
            elif df.iloc[i, 7] == df.iloc[i, 8]:
                 df.iloc[i, 5] = 'D'
        elif df.iloc[i, 2] == 'A':
            if df.iloc[i, 7] > df.iloc[i, 8]:
                 df.iloc[i, 5] = 'L'
            elif df.iloc[i, 7] < df.iloc[i, 8]:
                 df.iloc[i, 5] = 'W'
            elif df.iloc[i, 7] == df.iloc[i,8]:
                 df.iloc[i, 5] = 'D'
    df = df.filter(items = ['Date', 'Ranking', 'results', 'Competition', 'Matchday'])
    df['Ranking'] = df['Ranking'].str.extract('(\d+)', expand=False)
    
    return df


# In[21]:


#   Applying results function


juveres1819 = resultsandranking(juveres1819)
juveres1718 = resultsandranking(juveres1718)
romares1819 = resultsandranking(romares1819)
romares1718 = resultsandranking(romares1718)
laziores1819 = resultsandranking(laziores1819)
laziores1718 = resultsandranking(laziores1718)


# In[22]:


#   Setting values in 'Date' column to datetime format, then sorting dataframe by date


def dates(df):
    for index, row in df.iterrows():
        df.loc[index, 'Date'] = parse(df.loc[index, 'Date']).date()
    df['Date'] = pd.to_datetime(df['Date'])    
    df = df.sort_values(by = 'Date')
    df = df.reset_index(drop = True)
    return df


# In[23]:


#   Applying dates function


juveres1819 = dates(juveres1819)
juveres1718 = dates(juveres1718)
romares1819 = dates(romares1819)
romares1718 = dates(romares1718)
laziores1819 = dates(laziores1819)
laziores1718 = dates(laziores1718)


# In[24]:


#  Setting matchday to indices 


juveres1819['Matchday'] = juveres1819.index
juveres1718['Matchday'] = juveres1718.index
romares1819['Matchday'] = romares1819.index
romares1718['Matchday'] = romares1718.index
laziores1819['Matchday'] = laziores1819.index
laziores1718['Matchday'] = laziores1718.index


# In[38]:


#   These results were recorded as wins, but due to the two-leg system of the Champions league, resulted in an exit from
#   the competition regardless, so should be recorded as losses.


juveres1718.loc[juveres1718['Date'] == '2018-04-11', 'results'] = 'L'
romares1718.loc[romares1718['Date'] == '2018-05-02', 'results'] = 'L'


# In[40]:


#   Exporting finalized dataframes to csv format


juveres1819.to_csv('juve_res1819.csv', index = False)
juveres1718.to_csv('juve_res1718.csv', index = False)
romares1819.to_csv('roma_res1819.csv', index = False)
romares1718.to_csv('roma_res1718.csv', index = False)
laziores1819.to_csv('lazio_res1819.csv', index = False)
laziores1718.to_csv('lazio_res1718.csv', index = False)


# In[ ]:




