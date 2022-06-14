#!/usr/bin/env python
# coding: utf-8

# In[28]:


#   Importing required libraries


import plotly.express as px
import os
import pandas as pd
import numpy as np
from pandas_datareader import data as pdr
import requests as req
from dateutil.parser import parse
import datetime
from scipy import stats
import plotly.graph_objects as go


# In[29]:


#   Reading results and ranking data in


laziores1718 = pd.read_csv('lazio_res1718.csv')
laziores1819 = pd.read_csv('lazio_res1819.csv')


# In[30]:


#   Reading extended date and stock data in


seriea1718 = pd.read_csv('seriea1718.csv')
seriea1819 = pd.read_csv('seriea1819.csv')


# In[31]:


#   Creating merged dataframes with stock, results and ranking over entire season
#   results and ranking missing values are filled with previous values


lazio1718 = pd.merge(seriea1718[['Date', 'lazio']], laziores1718[['Date','results', 'Ranking', 'Competition', 'Matchday']],on='Date', how='left')
lazio1718 = lazio1718.fillna(method = 'ffill')

lazio1819 = pd.merge(seriea1819[['Date', 'lazio']], laziores1819[['Date','results', 'Ranking', 'Competition', 'Matchday']],on='Date', how='left') 
lazio1819 = lazio1819.fillna(method = 'ffill')


# In[21]:


#   Checking heads to see the date of first result of the season


print('\n', lazio1718.head(40), '\n' '--------------------------------------------\n', 
            lazio1819.head(40))


# In[32]:


#   Cleaning up 'Matchday' column for 18/19 to start at game 1 and get rid of NaNs.

lazio1718 = lazio1718.dropna(subset = ['Matchday'])
lazio1819 = lazio1819.dropna(subset = ['Matchday'])

for i, row in lazio1819.iterrows():
    lazio1819.loc[i, 'Matchday'] = lazio1819.loc[i, 'Matchday'] + 1    


lazio1819 = lazio1819.reset_index(drop=True)


# In[23]:




################################################################################################################################
################################################################################################################################

#   Preliminary Graphing

################################################################################################################################
################################################################################################################################


# In[33]:


#   Plotting results and stock data. The results on the face of it do not appear to make a difference


fig1 = px.scatter(lazio1718.iloc[5::], x='Date', y = 'lazio', color = 'results')
fig1.show()


# In[25]:


#   Plotting table ranking and stock data

lazio1718['Ranking'] = lazio1718['Ranking'].astype(str)
fig2 = px.scatter(lazio1718.iloc[5::], x='Date', y = 'lazio', color = 'Ranking')
fig2.show()


# In[34]:


#   Season 2 appears to be similar in terms of the effect of results on stock price to season 1 


fig3 = px.scatter(lazio1819.iloc[5::], x='Date', y = 'lazio', color = 'results')
fig3.show()


# In[35]:


#   Plotting table rank for season 2


lazio1819['Ranking'] = lazio1819['Ranking'].astype(str)
fig4 = px.scatter(lazio1819.iloc[5::], x='Date', y = 'lazio', color = 'Ranking')
fig4.show()


# In[36]:


#  Creating markers for different competitions for plotly. 'European' here refers to european competitions, 'League'
#  to Serie A, and 'Acup' to domestic cup competitions


def markerset(df): 
    for i, row in df.iterrows():
        if df.loc[i, 'Competition'] == 'European':
            df.loc[i, 'Markers'] = 0.5
        elif df.loc[i, 'Competition'] == 'League':
            df.loc[i, 'Markers'] = 0.1
        elif df.loc[i, 'Competition'] == 'Acup':
            df.loc[i, 'Markers'] = 0.1
    df['Markers'] = pd.to_numeric(df['Markers'])
    return df


# In[37]:


#   Looking into the European results, it appears there may be some affect of these results on the stock price
#   in the 2017/18 season


lazio1718 = markerset(lazio1718)
    
cdict = {'Acup': 'rgb(0,0,255)', 'League': 'rgb(0,0,255)', 'European': 'rgb(0,255,0)'}

fig5 = px.scatter(lazio1718.iloc[5::], 
                  x='Date', 
                  y = 'lazio', 
                  color = 'Competition',
                  color_discrete_map = cdict,
                  size = 'Markers'
                  )
fig5.update_layout(width=2200, height = 800)
fig5.show()


# In[38]:


#   For season 2 this may also be the case.


lazio1819 = markerset(lazio1819)
    
cdict = {'Acup': 'rgb(0,0,255)', 'League': 'rgb(0,0,255)', 'European': 'rgb(0,255,0)'}

fig6 = px.scatter(lazio1819.iloc[5::], 
                  x='Date', 
                  y = 'lazio', 
                  color = 'Competition',
                  color_discrete_map = cdict,
                  size = 'Markers'
                  )
fig6.update_layout(width=2200, height = 800)
fig6.show()


# In[31]:




################################################################################################################################
################################################################################################################################

#   Preparation of Results for Statistical Analysis

################################################################################################################################
################################################################################################################################


# In[39]:


#   Creating new columns to measure the percentage change between close each day


lazio1718['pctchange'] = ""
lazio1819['pctchange'] = ""


# In[40]:


#   Calculating change from last working day before game to last working day before next game 


def pctchangegtg(df):
    for i, row in df.iterrows():
        if i == 0:
            pass
        elif i < df['Matchday'].max() + 1:
            a = df.loc[df['Matchday'] == i, 'lazio'].dropna().tolist()
            df.loc[df['Matchday'] == i, 'pctchange'] = (a[-1]-a[0])/a[0]
        else:break
    return df



#   Calculating change from working day before game to next working day


def pctchangenwd(df):
    for i, row in df.iterrows():
        if i == 0:
            pass
        elif i == 1:
            a = df.loc[df['Matchday'] == i, 'lazio'].dropna().tolist()
            df.loc[df['Matchday'] == i, 'pctchange'] = a[0]
        elif i <= df['Matchday'].max():
            a = df.loc[df['Matchday'] == i, 'lazio'].dropna().drop_duplicates().tolist()
            b = df.loc[df['Matchday'] == i-1, 'lazio'].dropna().drop_duplicates().tolist()
            if len(a) == 1:
                df.loc[df['Matchday'] == i, 'pctchange'] = 0
            else:
                df.loc[df['Matchday'] == i, 'pctchange'] = (a[1] - b[-1])/a[1]
        else:break
    return df


# In[41]:


#   Creating lists of these stock value changes to apply statistical testing to. 


adf = pctchangegtg(lazio1718).drop_duplicates(subset = ['Matchday'])
bdf = pctchangegtg(lazio1819).drop_duplicates(subset = ['Matchday'])


#   Creating lists of game-game stock change for all competitions

AC_W1718_GTG = adf.loc[adf['results'] == 'W', 'pctchange'].dropna().tolist()
AC_D1718_GTG = adf.loc[adf['results'] == 'D', 'pctchange'].dropna().tolist()
AC_L1718_GTG = adf.loc[adf['results'] == 'L', 'pctchange'].dropna().tolist()

AC_W1819_GTG = bdf.loc[bdf['results'] == 'W', 'pctchange'].dropna().tolist()
AC_D1819_GTG = bdf.loc[bdf['results'] == 'D', 'pctchange'].dropna().tolist()
AC_L1819_GTG = bdf.loc[bdf['results'] == 'L', 'pctchange'].dropna().tolist()


#   Extracting just UEFA European results

eul1718_GTG = adf.loc[adf['Competition'] == 'European', ['results', 'pctchange']]
eul1819_GTG = bdf.loc[bdf['Competition'] == 'European', ['results', 'pctchange']]

EL_W1718_GTG = eul1718_GTG.loc[eul1718_GTG['results'] == 'W', 'pctchange'].dropna().to_list()
EL_D1718_GTG = eul1718_GTG.loc[eul1718_GTG['results'] == 'D', 'pctchange'].dropna().to_list()
EL_L1718_GTG = eul1718_GTG.loc[eul1718_GTG['results'] == 'L', 'pctchange'].dropna().to_list()

EL_W1819_GTG = eul1819_GTG.loc[eul1819_GTG['results'] == 'W', 'pctchange'].dropna().to_list()
EL_D1819_GTG = eul1819_GTG.loc[eul1819_GTG['results'] == 'D', 'pctchange'].dropna().to_list()
EL_L1819_GTG = eul1819_GTG.loc[eul1819_GTG['results'] == 'L', 'pctchange'].dropna().to_list()

#   List of combined seasons for European Matches due to lack of data for one season.

EL_WSVS_GTG = EL_W1718_GTG + EL_W1819_GTG
EL_DSVS_GTG = EL_D1718_GTG + EL_D1819_GTG
EL_LSVS_GTG = EL_L1718_GTG + EL_L1819_GTG


#   Extracting just domestic results

dom1718_GTG = adf.loc[adf['Competition'] != 'European', ['results', 'pctchange']]
dom1819_GTG = bdf.loc[bdf['Competition'] != 'European', ['results', 'pctchange']]

DO_W1718_GTG = dom1718_GTG.loc[dom1718_GTG['results'] == 'W', 'pctchange'].dropna().to_list()
DO_D1718_GTG = dom1718_GTG.loc[dom1718_GTG['results'] == 'D', 'pctchange'].dropna().to_list()
DO_L1718_GTG = dom1718_GTG.loc[dom1718_GTG['results'] == 'L', 'pctchange'].dropna().to_list()

DO_W1819_GTG = dom1819_GTG.loc[dom1819_GTG['results'] == 'W', 'pctchange'].dropna().to_list()
DO_D1819_GTG = dom1819_GTG.loc[dom1819_GTG['results'] == 'D', 'pctchange'].dropna().to_list()
DO_L1819_GTG = dom1819_GTG.loc[dom1819_GTG['results'] == 'L', 'pctchange'].dropna().to_list()


# In[42]:


#   Record means and median of groups. After establishing means are different later on, these will be analyzed
#   to see in what sense e.g. determining if winning causes a positive change or losing causes a decline.
#   Statistical testing here is limited by the number of results required for accuracy of an applied statistical test, so
#   length of lists is important to note


def maininfo(x):
        print('Mean:', np.asarray(x).mean(), 'median:', np.median(np.asarray(x)), 'Length:', len(x),
             '\n------------------------------------------------------------------','\n')


print('AC_W1718_GTG:')
maininfo(AC_W1718_GTG)
print('AC_L1718_GTG:') 
maininfo(AC_L1718_GTG)
print('AC_D1718_GTG:')
maininfo(AC_D1718_GTG)

print('AC_W1819_GTG:')
maininfo (AC_W1819_GTG)
print('AC_L1819_GTG:') 
maininfo(AC_L1819_GTG)
print('AC_D1819_GTG:') 
maininfo(AC_D1819_GTG)

print('EL_W1718_GTG:')
maininfo(EL_W1718_GTG)
print('EL_L1718_GTG:')
maininfo(EL_L1718_GTG)
print('EL_D1718_GTG:')
maininfo(EL_D1718_GTG)

print('EL_W1819_GTG:')
maininfo(EL_W1819_GTG)
print('EL_L1819_GTG:')
maininfo(EL_L1819_GTG)
print('EL_D1819_GTG:')
maininfo(EL_D1819_GTG)

print('DO_W1718_GTG:') 
maininfo(DO_W1718_GTG)
print('DO_L1718_GTG:')
maininfo(DO_L1718_GTG)
print('DO_D1718_GTG:')
maininfo(DO_D1718_GTG)

print('DO_W1819_GTG:')
maininfo(DO_W1819_GTG)
print('DO_L1819_GTG;')
maininfo(DO_L1819_GTG) 
print('DO_D1819_GTG;')
maininfo(DO_D1819_GTG) 

print('EL_WSVS_GTG:')
maininfo(EL_WSVS_GTG)
print('EL_LSVS_GTG;')
maininfo(EL_LSVS_GTG) 
print('EL_DSVS_GTG;')
maininfo(EL_DSVS_GTG) 


# In[43]:


#   Setting marker colour based on result


def SetColor(x):
        if x == 'W':
            return "green"
        elif x == 'L':
            return "red"
        elif x == 'D':
            return "blue"


# In[44]:


#   Graphing percentage change over time in the lazio stock for the 2017/18 season. Losses may be negatively skewed



fig7 = go.Figure(go.Scatter(y=adf['pctchange'], 
                          x=adf['Date'],
                          mode='markers',
                          marker=dict(size=8, color=list(map(SetColor, adf['results'])))))

fig7.show()


# In[45]:


#   Setting marker colour based on competition


def SetColor2(x):
        if x == 'European':
            return "green"
        elif x == 'League':
            return "red"
        elif x == 'Acup':
            return "blue"


# In[46]:


#   Graphing stock change by competition for the 201718 season. There appears to be no difference between the competitions


fig8 = go.Figure(go.Scatter(y=adf['pctchange'], 
                          x=adf['Date'],
                          mode='markers',
                          marker=dict(size=8, color=list(map(SetColor2, adf['Competition'])))))

fig8.show()


# In[47]:


#   For season 2018/19, losses at first glance may negatively impact stock price


fig9 = go.Figure(go.Scatter(y=bdf['pctchange'], 
                          x=bdf['Date'],
                          mode='markers', 
                          marker=dict(size=8, color=list(map(SetColor, bdf['results'])))))

fig9.show()


# In[48]:


#   Domestic and European results seem to be fairly evenly distributed in the 2018/19 season



fig10 = go.Figure(go.Scatter(y=bdf['pctchange'], 
                          x=bdf['Date'],
                          mode='markers',
                          marker=dict(size=8, color=list(map(SetColor2, bdf['Competition'])))))

fig10.show()


# In[49]:


#   Creating the same groups, but applying the next-working-day function. This means getting rid of the first Matchday as this
#   just ends up as an extremely high outlier




cdf = pctchangenwd(lazio1718).drop_duplicates(subset = ['Matchday']).reset_index(drop=True)
cdf = cdf.iloc[1:,]
ddf = pctchangenwd(lazio1819).drop_duplicates(subset = ['Matchday']).reset_index(drop = True)
ddf = ddf.iloc[1:,]


#   Creating lists of next-working-day stock change for all competitions

AC_W1718_NWD = cdf.loc[cdf['results'] == 'W', 'pctchange'].dropna().tolist()
AC_D1718_NWD = cdf.loc[cdf['results'] == 'D', 'pctchange'].dropna().tolist()
AC_L1718_NWD = cdf.loc[cdf['results'] == 'L', 'pctchange'].dropna().tolist()

AC_W1819_NWD = ddf.loc[ddf['results'] == 'W', 'pctchange'].dropna().tolist()
AC_D1819_NWD = ddf.loc[ddf['results'] == 'D', 'pctchange'].dropna().tolist()
AC_L1819_NWD = ddf.loc[ddf['results'] == 'L', 'pctchange'].dropna().tolist()


#   Extracting just UEFA European results

eul1718_NWD = cdf.loc[cdf['Competition'] == 'European', ['results', 'pctchange']]
eul1819_NWD = ddf.loc[ddf['Competition'] == 'European', ['results', 'pctchange']]

EL_W1718_NWD = eul1718_NWD.loc[eul1718_NWD['results'] == 'W', 'pctchange'].dropna().to_list()
EL_D1718_NWD = eul1718_NWD.loc[eul1718_NWD['results'] == 'D', 'pctchange'].dropna().to_list()
EL_L1718_NWD = eul1718_NWD.loc[eul1718_NWD['results'] == 'L', 'pctchange'].dropna().to_list()

EL_W1819_NWD = eul1819_NWD.loc[eul1819_NWD['results'] == 'W', 'pctchange'].dropna().to_list()
EL_D1819_NWD = eul1819_NWD.loc[eul1819_NWD['results'] == 'D', 'pctchange'].dropna().to_list()
EL_L1819_NWD = eul1819_NWD.loc[eul1819_NWD['results'] == 'L', 'pctchange'].dropna().to_list()


#   List of combined seasons for European matches due to lack of data for one season.

EL_WSVS_NWD = EL_W1718_NWD + EL_W1819_NWD
EL_DSVS_NWD = EL_D1718_NWD + EL_D1819_NWD
EL_LSVS_NWD = EL_L1718_NWD + EL_L1819_NWD


#   Extracting just domestic results

dom1718_NWD = cdf.loc[cdf['Competition'] != 'European', ['results', 'pctchange']]
dom1819_NWD = ddf.loc[ddf['Competition'] != 'European', ['results', 'pctchange']]

DO_W1718_NWD = dom1718_NWD.loc[dom1718_NWD['results'] == 'W', 'pctchange'].dropna().to_list()
DO_D1718_NWD = dom1718_NWD.loc[dom1718_NWD['results'] == 'D', 'pctchange'].dropna().to_list()
DO_L1718_NWD = dom1718_NWD.loc[dom1718_NWD['results'] == 'L', 'pctchange'].dropna().to_list()

DO_W1819_NWD = dom1819_NWD.loc[dom1819_NWD['results'] == 'W', 'pctchange'].dropna().to_list()
DO_D1819_NWD = dom1819_NWD.loc[dom1819_NWD['results'] == 'D', 'pctchange'].dropna().to_list()
DO_L1819_NWD = dom1819_NWD.loc[dom1819_NWD['results'] == 'L', 'pctchange'].dropna().to_list()


# In[50]:


#   Record means and median of groups. After establishing means are different later on, these will be analyzed
#   to see in what sense e.g. determining if winning causes a positive change or losing causes a decline.
#   Statistical testing here is limited by the number of results required for accuracy of an applied statistical test, so
#   length of lists is important to note


print('AC_W1718_NWD:')
maininfo(AC_W1718_NWD)
print('AC_L1718_NWD:') 
maininfo(AC_L1718_NWD)
print('AC_D1718_NWD:')
maininfo(AC_D1718_NWD)

print('AC_W1819_NWD:')
maininfo (AC_W1819_NWD)
print('AC_L1819_NWD:') 
maininfo(AC_L1819_NWD)
print('AC_D1819_NWD:') 
maininfo(AC_D1819_NWD)

print('EL_W1718_NWD:')
maininfo(EL_W1718_NWD)
print('EL_L1718_NWD:')
maininfo(EL_L1718_NWD)
print('EL_D1718_NWD:')
maininfo(EL_D1718_NWD)

print('EL_W1819_NWD:')
maininfo(EL_W1819_NWD)
print('EL_L1819_NWD:')
maininfo(EL_L1819_NWD)
print('EL_D1819_NWD:')
maininfo(EL_D1819_NWD)

print('DO_W1718_NWD:') 
maininfo(DO_W1718_NWD)
print('DO_L1718_NWD:')
maininfo(DO_L1718_NWD)
print('DO_D1718_NWD:')
maininfo(DO_D1718_NWD)

print('DO_W1819_NWD:')
maininfo(DO_W1819_NWD)
print('DO_L1819_NWD;')
maininfo(DO_L1819_NWD) 
print('DO_D1819_NWD;')
maininfo(DO_D1819_NWD) 

print('EL_WSVS_NWD:')
maininfo(EL_WSVS_NWD)
print('EL_LSVS_NWD;')
maininfo(EL_LSVS_NWD) 
print('EL_DSVS_NWD;')
maininfo(EL_DSVS_NWD) 


# In[51]:


#   Graphing next-working-day change in lazio stock for the 2017/18 season. When coloring by results 
#   losing appears to result in a stock decline.


fig11 = go.Figure(go.Scatter(y=cdf['pctchange'], 
                          x=cdf['Date'],
                          mode='markers',
                          marker=dict(size=8, color=list(map(SetColor, cdf['results'])))))

fig11.show()


# In[52]:


#   Graphing next-working-day change in lazio stock for the 2017/18 season. When coloring by competition 
#   (in all competitions) there does not appear to be a difference


fig12 = go.Figure(go.Scatter(y=cdf['pctchange'], 
                          x=cdf['Date'],
                          mode='markers',
                          marker=dict(size=8, color=list(map(SetColor2, cdf['Competition'])))))

fig12.show()


# In[53]:


#   When analyzing stock change based on results in 2018/19 there may be a slight negative skew to draws.


fig13 = go.Figure(go.Scatter(y=ddf['pctchange'], 
                          x=ddf['Date'],
                          mode='markers',
                          marker=dict(size=8, color=list(map(SetColor, ddf['results'])))))

fig13.show()


# In[54]:


#   Analyzing by competition, domestic cups may have a slight positive skew in 2018/19


fig14 = go.Figure(go.Scatter(y=ddf['pctchange'], 
                          x=ddf['Date'],
                          mode='markers',
                          marker=dict(size=8, color=list(map(SetColor2, ddf['Competition'])))))

fig14.show()


# In[55]:


all_1718_gtg = adf['pctchange'].to_list()
ucl_1718_gtg = adf.loc[adf['Competition'] == 'European', 'pctchange'].tolist()
dom_1718_gtg = adf.loc[adf['Competition'] != 'European', 'pctchange'].tolist()

all_1819_gtg = bdf['pctchange'].to_list()
ucl_1819_gtg = bdf.loc[bdf['Competition'] == 'European', 'pctchange'].tolist()
dom_1819_gtg = bdf.loc[bdf['Competition'] != 'European', 'pctchange'].tolist()

all_1718_nwd = cdf['pctchange'].to_list()
ucl_1718_nwd = cdf.loc[cdf['Competition'] == 'European', 'pctchange'].tolist()
dom_1718_nwd = cdf.loc[cdf['Competition'] != 'European', 'pctchange'].tolist()

all_1819_nwd = ddf['pctchange'].to_list()
ucl_1819_nwd = ddf.loc[cdf['Competition'] == 'European', 'pctchange'].tolist()
dom_1819_nwd = ddf.loc[cdf['Competition'] != 'European', 'pctchange'].tolist()


# In[57]:




################################################################################################################################
################################################################################################################################




#   Statistical analysis of results




################################################################################################################################
################################################################################################################################


# In[56]:


#   Creating lists of results for analysis

#   European 17-18 and 19/20 NWD and GTG do not have enough results to include
#   Domestic competitions 2017/18 NWD and GTG both do not have enough losses to include


GTG_AC_results1718 = [AC_W1718_GTG, AC_D1718_GTG, AC_L1718_NWD]
GTG_DO_results1718 = [DO_W1718_GTG, DO_D1718_GTG, DO_L1718_GTG]
GTG_AC_results1819 = [AC_W1819_GTG, AC_D1819_GTG, AC_L1819_GTG]
GTG_DO_results1819 = [DO_W1819_GTG, DO_D1819_GTG, DO_L1819_GTG]


NWD_AC_results1718 = [AC_W1718_NWD, AC_D1718_NWD, AC_L1718_NWD]
NWD_DO_results1718 = [DO_W1718_NWD, DO_D1718_NWD, DO_L1718_NWD]
NWD_AC_results1819 = [AC_W1819_NWD, AC_D1819_NWD, AC_L1819_NWD]
NWD_DO_results1819 = [DO_W1819_NWD, DO_D1819_NWD, DO_L1819_NWD]

GTG_SVS_results = [EL_WSVS_GTG,EL_LSVS_GTG]
NWD_SVS_results = [EL_WSVS_NWD,EL_LSVS_NWD]


# In[57]:


#   Creating a function to run through the appropriate test with each result set. First, the Shapiro-Wilk test is used
#   to test for normality. 'Normal' groups will be tested using the Students T-Test or Welch T-Test according to 
#   non-significant or significant Levene result (testing for homogeneity of variance). The Kruskal-Wallis test is used
#   on all groups regardless of Shapiro-Wilk result.
#   The non-parametric results are likely more accurate, as I cannot be confident it is actually possible these 
#   groups could be normally distributed, though as the parametric tests are more powerful it is perhaps worth keeping them

 

def statstest1(list):
    
    if len(list) == 2:
        d, a = stats.shapiro(list[0])
        d, b = stats.shapiro(list[1])
        d, c = stats.kruskal(list[0], list[1])
        d, e = stats.levene(list[0], list[1])
        if b > 0.05:
            if c > 0.05:
                if e < 0.05:
                    dd, aa = stats.ttest_ind(list[0], list[1], equal_var = False)
                    print("Win vs Draw WELCH T-TEST:", aa)
                    if aa < 0.05:
                        print("These groups are different")
                    else:
                        print("Could not find a difference")
            else:
                dd, aa = stats.ttest_ind(list[0], list[1])
                print("Win vs Draw STUDENTS T-TEST", aa)
                if aa < 0.05:
                    print("These groups are different")
                else:
                        print("Could not find a difference")
        print("Win vs Draw Kruskal:", c)
        if c < 0.05:
            print("These groups are different")
        else:
            print("Could not find a difference")
            
        
           
    if len(list) == 3:
        d, a = stats.shapiro(list[0])
        d, b = stats.shapiro(list[1])
        d, c = stats.shapiro(list[2])
        d, e = stats.kruskal(list[0], list[1])
        d, f = stats.kruskal(list[0], list[2])
        d, g = stats.kruskal(list[1], list[2])
        d, h = stats.levene(list[0], list[1])
        d, i = stats.levene(list[0], list[2])
        d, j = stats.levene(list[1], list[2])
                
        if a > 0.05:
            if b > 0.05:
                if h < 0.05:
                    dd, aa = stats.ttest_ind(list[0], list[1], equal_var = False)
                    print("Win vs Draw WELCH T-TEST:", aa)
                    if aa < 0.05:
                        print("These groups are different")
                    else:
                        print("Could not find a difference")
                else:
                    dd, aa = stats.ttest_ind(list[0], list[1])
                    print("Win vs Draw STUDENTS T-TEST", aa)
                    if aa < 0.05:
                        print("These groups are different")
                    else:
                        print("Could not find a difference")
            if c > 0.05:
                if i < 0.05:
                    dd, aa = stats.ttest_ind(list[0], list[2], equal_var = False)
                    print("Win vs Loss WELCH T-TEST:", aa)
                    if aa < 0.05:
                        print("These groups are different")
                    else:
                        print("Could not find a difference")
                else:
                    dd, aa = stats.ttest_ind(list[0], list[2])
                    print("Win vs Loss STUDENTS T-TEST", aa)
                    if aa < 0.05:
                        print("These groups are different")
                    else:
                        print("Could not find a difference")
                                
        else:
            if b > 0.05:
                if c > 0.05:
                    if j < 0.05:
                        dd, aa = stats.ttest_ind(list[1], list[2], equal_var = False)
                        print("Draw vs Loss WELCH T-TEST:", aa)
                        if aa < 0.05:
                            print("These groups are different")
                        else:
                            print("Could not find a difference")
                    else:
                        dd, aa = stats.ttest_ind(list[1], list[2])
                        print("Draw vs Loss STUDENTS T-TEST", aa)
                        if aa < 0.05:
                            print("These groups are different")
                        else:
                            print("Could not find a difference")

        print("Win vs Draw Kruskal:", e)
        if e < 0.05:
            print("These groups are different")
        else:
            print("Could not find a difference")
        print("Win vs Loss Kruskal:", f)
        if f < 0.05:
            print("These groups are different")
        else:
            print("Could not find a difference")
        
        print("Draw vs Loss Kruskal:", g)
        if g < 0.05:
            print("These groups are different")
        else:
            print("Could not find a difference")


# In[58]:


#   Printing results of analyses


print('\nGTG 17/18 All Competition Results: -------------------------------------\n')
statstest1(GTG_AC_results1718)
print('\nGTG 17/18 Domestic Results: -------------------------------------\n')
statstest1(GTG_DO_results1718)
print('\nGTG 18/19 All Competition Results: -------------------------------------\n')
statstest1(GTG_AC_results1819)
print('\nGTG 18/19 Domestic Results: -------------------------------------\n')
statstest1(GTG_DO_results1819)

print('\nNWD 17/18 All Competition Results: -------------------------------------\n')
statstest1(NWD_AC_results1718)
print('\nNWD 17/18 Domestic Results: -------------------------------------\n','\n')
statstest1(NWD_DO_results1718)
print('\nNWD 18/19 All Competition Results: -------------------------------------\n')
statstest1(NWD_AC_results1819)
print('\nNWD 18/19 Domestic Results: -------------------------------------\n')
statstest1(NWD_DO_results1819)

print('\nGTG European Leagues across all years Domestic Results: -------------------------------------\n')
statstest1(GTG_SVS_results)
print('\nNWD European Leagues across all years Domestic Results: -------------------------------------\n')
statstest1(NWD_SVS_results)


# In[59]:


################################################################################################################################
################################################################################################################################


#   A second testing function is used to determine if there are significant differences between results (as a whole)
#   in the champions league, all competitions, and domestic competitions.  
 


# In[60]:


def statstest2(list):
    
    d, a = stats.shapiro(list[0])
    d, b = stats.shapiro(list[1])
    d, c = stats.shapiro(list[2]) 
    d, e = stats.kruskal(list[0], list[1])
    d, f = stats.kruskal(list[0], list[2])
    d, g = stats.kruskal(list[1], list[2])
    d, h = stats.levene(list[0], list[1])
    d, i = stats.levene(list[0], list[2])
    d, j = stats.levene(list[1], list[2])
    
    if a > 0.05:
        if b > 0.05:
            if h < 0.05:
                dd, aa = stats.ttest_ind(list[0], list[1], equal_var = False)
                print("All vs UEL WELCH T-TEST:", aa)
                if aa < 0.05:
                        print("These groups are different")
                else:
                    print("Could not find a difference")
            else:
                dd, aa = stats.ttest_ind(list[0], list[1])
                print("All vs UEL STUDENTS T-TEST", aa)
                if aa < 0.05:
                        print("These groups are different")
                else:
                    print("Could not find a difference")
        if c > 0.05:
            if i < 0.05:
                dd, aa = stats.ttest_ind(list[0], list[2], equal_var = False)
                print("All vs Domestic WELCH T-TEST:", aa)
                if aa < 0.05:
                        print("These groups are different")
                else:
                    print("Could not find a difference")
            else:
                dd, aa = stats.ttest_ind(list[0], list[2])
                print("All vs Domestic STUDENTS T-TEST", aa)
                if aa < 0.05:
                        print("These groups are different")
                else:
                    print("Could not find a difference")
                    
    else:
        if b > 0.05:
            if c > 0.05:
                if j < 0.05:
                    dd, aa = stats.ttest_ind(list[1], list[2], equal_var = False)
                    print("UEL vs Domestic WELCH T-TEST:", aa)
                    if aa < 0.05:
                        print("These groups are different")
                    else:
                        print("Could not find a difference")
                else:
                    dd, aa = stats.ttest_ind(list[1], list[2])
                    print("UEL vs Domestic STUDENTS T-TEST", aa)
                    if aa < 0.05:
                        print("These groups are different")
                    else:
                        print("Could not find a difference")
                        
    print("All vs UEL Kruskal:", e)
    if e < 0.05:
        print("These groups are different")
    else:
        print("Could not find a difference")
    
    print("All vs Domestic, Kruskal:", f)
    if f < 0.05:
        print("These groups are different")
    else:
        print("Could not find a difference")
        
    print("UEL vs Domestic Kruskal:", g)
    if g < 0.05:
        print("These groups are different")
    else:
        print("Could not find a difference")


# In[61]:


#   Creating lists for this function


gtg_comp1718 = [all_1718_gtg, ucl_1718_gtg, dom_1718_gtg] 
gtg_comp1819 = [all_1819_gtg, ucl_1819_gtg, dom_1819_gtg]


nwd_comp1718 = [all_1718_nwd, ucl_1718_nwd, dom_1718_nwd]
nwd_comp1819 = [all_1819_nwd, ucl_1819_nwd, dom_1819_nwd]


# In[62]:


#   Record means and median of groups. After establishing means are different later on, these will be analyzed
#   to see in what sense e.g. determining if winning causes a positive change or losing causes a decline.


print('all_1718_gtg:')
maininfo(all_1718_gtg)
print('ucl_1718_gtg:') 
maininfo(ucl_1718_gtg)
print('dom_1718_gtg:')
maininfo(dom_1718_gtg)

print('all_1819_gtg:')
maininfo (all_1819_gtg)
print('ucl_1819_gtg:') 
maininfo(ucl_1819_gtg)
print('dom_1819_gtg:') 
maininfo(dom_1819_gtg)

print('all_1718_nwd:')
maininfo(all_1718_nwd)
print('ucl_1718_nwd:')
maininfo(ucl_1718_nwd)
print('dom_1718_nwd:')
maininfo(dom_1718_nwd)

print('all_1819_nwd:')
maininfo(all_1819_nwd)
print('ucl_1819_nwd:')
maininfo(ucl_1819_nwd)
print('dom_1819_nwd:')
maininfo(dom_1819_nwd)


# In[63]:


#   Printing results


print('GTG 17/18:\n')
stats_gtg_comp1819 = statstest2(gtg_comp1718)
print('\n', '\nGTG 18/19:\n')
stats_gtg_comp1819 = statstest2(gtg_comp1819)
print('\n', '\nNWD 17/18:\n')
stats_nwd_comp1718 = statstest2(nwd_comp1718)
print('\n', '\nNWD 18/19:\n')
stats_nwd_comp1819 = statstest2(nwd_comp1819)


# In[ ]:




