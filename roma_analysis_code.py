#!/usr/bin/env python
# coding: utf-8

# In[15]:


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


# In[16]:


#   Reading results and ranking data in


romares1718 = pd.read_csv('roma_res1718.csv')
romares1819 = pd.read_csv('roma_res1819.csv')


# In[17]:


#   Reading extended date and stock data in


seriea1718 = pd.read_csv('seriea1718.csv')
seriea1819 = pd.read_csv('seriea1819.csv')


# In[18]:


#   Creating merged dataframes with stock, results and ranking over entire season
#   results and ranking missing values are filled with previous values


roma1718 = pd.merge(seriea1718[['Date', 'roma']], romares1718[['Date','results', 'Ranking', 'Competition', 'Matchday']],on='Date', how='left')
roma1718 = roma1718.fillna(method = 'ffill')

roma1819 = pd.merge(seriea1819[['Date', 'roma']], romares1819[['Date','results', 'Ranking', 'Competition', 'Matchday']],on='Date', how='left') 
roma1819 = roma1819.fillna(method = 'ffill')


# In[5]:


#   Checking heads to see the date of first result of the season


print('\n', roma1718.head(40), '\n' '--------------------------------------------\n', 
            roma1819.head(40))


# In[19]:


#   Cleaning up 'Matchday' column in both seasons to start at game 1, and get rid of NaNs.

roma1718 = roma1718.dropna(subset = ['Matchday'])
roma1819 = roma1819.dropna(subset = ['Matchday'])


for i, row in roma1718.iterrows():
    roma1718.loc[i, 'Matchday'] = roma1718.loc[i, 'Matchday'] + 1
    
for i, row in roma1819.iterrows():
    roma1819.loc[i, 'Matchday'] = roma1819.loc[i, 'Matchday'] + 1    

roma1718 = roma1718.reset_index(drop=True)
roma1819 = roma1819.reset_index(drop=True)


# In[13]:




################################################################################################################################
################################################################################################################################

#   Preliminary Graphing

################################################################################################################################
################################################################################################################################


# In[20]:


#   Plotting results and stock data. The results on the face of it do not appear to make  a difference

fig1 = px.scatter(roma1718.iloc[5::], x='Date', y = 'roma', color = 'results')
fig1.show()


# In[7]:


#   Plotting table ranking and stock data. Really it appears there is no true correlation


roma1718['Ranking'] = roma1718['Ranking'].astype(str)
fig2 = px.scatter(roma1718.iloc[5::], x='Date', y = 'roma', color = 'Ranking')
fig2.show()


# In[8]:


#   In Season 2 it appears losses may negatively impact stock


fig3 = px.scatter(roma1819.iloc[5::], x='Date', y = 'roma', color = 'results')
fig3.show()


# In[9]:


#   In season 2, ranking is all over the place, as is stock price


fig4 = px.scatter(roma1819.iloc[5::], x='Date', y = 'roma', color = 'Ranking')
fig4.show()


# In[21]:


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


# In[22]:


#   Looking into the champions league results, it does not appear these impact stock price

roma1718 = markerset(roma1718)
    
cdict = {'Acup': 'rgb(0,0,255)', 'League': 'rgb(0,0,255)', 'European': 'rgb(0,255,0)'}

fig5 = px.scatter(roma1718.iloc[5::], 
                  x='Date', 
                  y = 'roma', 
                  color = 'Competition',
                  color_discrete_map = cdict,
                  size = 'Markers'
                  )
fig5.update_layout(width=2200, height = 800)
fig5.show()


# In[13]:


#   For season 2 this may also be the case.


roma1819 = markerset(roma1819)
    
cdict = {'Acup': 'rgb(0,0,255)', 'League': 'rgb(0,0,255)', 'European': 'rgb(0,255,0)'}

fig6 = px.scatter(roma1819.iloc[5::], 
                  x='Date', 
                  y = 'roma', 
                  color = 'Competition',
                  color_discrete_map = cdict,
                  size = 'Markers'
                  )
fig6.update_layout(width=2200, height = 800)
fig6.show()


# In[23]:




################################################################################################################################
################################################################################################################################

#   Preparation of Results for Statistical Analysis

################################################################################################################################
################################################################################################################################


# In[23]:


#   Creating new columns to measure the percentage change between close each day


roma1718['pctchange'] = ""
roma1819['pctchange'] = ""


# In[24]:


#   Calculating change from last working day before game to last working day before next game 


def pctchangegtg(df):
    for i, row in df.iterrows():
        if i == 0:
            pass
        elif i < df['Matchday'].max() + 1:
            a = df.loc[df['Matchday'] == i, 'roma'].dropna().tolist()
            df.loc[df['Matchday'] == i, 'pctchange'] = (a[-1]-a[0])/a[0]
        else:break
    return df



#   Calculating change from working day before game to next working day


def pctchangenwd(df):
    for i, row in df.iterrows():
        if i == 0:
            pass
        elif i == 1:
            a = df.loc[df['Matchday'] == i, 'roma'].dropna().tolist()
            df.loc[df['Matchday'] == i, 'pctchange'] = a[0]
        elif i <= df['Matchday'].max():
            a = df.loc[df['Matchday'] == i, 'roma'].dropna().drop_duplicates().tolist()
            b = df.loc[df['Matchday'] == i-1, 'roma'].dropna().drop_duplicates().tolist()
            if len(a) == 1:
                df.loc[df['Matchday'] == i, 'pctchange'] = 0
            else:
                df.loc[df['Matchday'] == i, 'pctchange'] = (a[1] - b[-1])/a[1]
        else:break
    return df


# In[25]:


#   Creating lists of these stock value changes to apply statistical testing to. 


adf = pctchangegtg(roma1718).drop_duplicates(subset = ['Matchday'])
bdf = pctchangegtg(roma1819).drop_duplicates(subset = ['Matchday'])


#   Creating lists of game-game stock change for all competitions

AC_W1718_GTG = adf.loc[adf['results'] == 'W', 'pctchange'].dropna().tolist()
AC_D1718_GTG = adf.loc[adf['results'] == 'D', 'pctchange'].dropna().tolist()
AC_L1718_GTG = adf.loc[adf['results'] == 'L', 'pctchange'].dropna().tolist()

AC_W1819_GTG = bdf.loc[bdf['results'] == 'W', 'pctchange'].dropna().tolist()
AC_D1819_GTG = bdf.loc[bdf['results'] == 'D', 'pctchange'].dropna().tolist()
AC_L1819_GTG = bdf.loc[bdf['results'] == 'L', 'pctchange'].dropna().tolist()


#   Extracting just UEFA Champions League results

ucl1718_GTG = adf.loc[adf['Competition'] == 'European', ['results', 'pctchange']]
ucl1819_GTG = bdf.loc[bdf['Competition'] == 'European', ['results', 'pctchange']]

CL_W1718_GTG = ucl1718_GTG.loc[ucl1718_GTG['results'] == 'W', 'pctchange'].dropna().to_list()
CL_D1718_GTG = ucl1718_GTG.loc[ucl1718_GTG['results'] == 'D', 'pctchange'].dropna().to_list()
CL_L1718_GTG = ucl1718_GTG.loc[ucl1718_GTG['results'] == 'L', 'pctchange'].dropna().to_list()

CL_W1819_GTG = ucl1819_GTG.loc[ucl1819_GTG['results'] == 'W', 'pctchange'].dropna().to_list()
CL_D1819_GTG = ucl1819_GTG.loc[ucl1819_GTG['results'] == 'D', 'pctchange'].dropna().to_list()
CL_L1819_GTG = ucl1819_GTG.loc[ucl1819_GTG['results'] == 'L', 'pctchange'].dropna().to_list()

#   List of combined seasons for Champions League due to lack of data for one season.

CL_WSVS_GTG = CL_W1718_GTG + CL_W1819_GTG
CL_DSVS_GTG = CL_D1718_GTG + CL_D1819_GTG
CL_LSVS_GTG = CL_L1718_GTG + CL_L1819_GTG


#   Extracting just domestic results

dom1718_GTG = adf.loc[adf['Competition'] != 'European', ['results', 'pctchange']]
dom1819_GTG = bdf.loc[bdf['Competition'] != 'European', ['results', 'pctchange']]

DO_W1718_GTG = dom1718_GTG.loc[dom1718_GTG['results'] == 'W', 'pctchange'].dropna().to_list()
DO_D1718_GTG = dom1718_GTG.loc[dom1718_GTG['results'] == 'D', 'pctchange'].dropna().to_list()
DO_L1718_GTG = dom1718_GTG.loc[dom1718_GTG['results'] == 'L', 'pctchange'].dropna().to_list()

DO_W1819_GTG = dom1819_GTG.loc[dom1819_GTG['results'] == 'W', 'pctchange'].dropna().to_list()
DO_D1819_GTG = dom1819_GTG.loc[dom1819_GTG['results'] == 'D', 'pctchange'].dropna().to_list()
DO_L1819_GTG = dom1819_GTG.loc[dom1819_GTG['results'] == 'L', 'pctchange'].dropna().to_list()


# In[26]:


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

print('CL_W1718_GTG:')
maininfo(CL_W1718_GTG)
print('CL_L1718_GTG:')
maininfo(CL_L1718_GTG)
print('CL_D1718_GTG:')
maininfo(CL_D1718_GTG)

print('CL_W1819_GTG:')
maininfo(CL_W1819_GTG)
print('CL_L1819_GTG:')
maininfo(CL_L1819_GTG)
print('CL_D1819_GTG:')
maininfo(CL_D1819_GTG)

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

print('CL_WSVS_GTG:')
maininfo(CL_WSVS_GTG)
print('CL_LSVS_GTG;')
maininfo(CL_LSVS_GTG) 
print('CL_DSVS_GTG;')
maininfo(CL_DSVS_GTG) 


# In[27]:


#   Setting marker colour based on result


def SetColor(x):
        if x == 'W':
            return "green"
        elif x == 'L':
            return "red"
        elif x == 'D':
            return "blue"


# In[28]:


#   Graphing percentage change over time in the roma stock for the 2017/18 season. Coloring by results 
#   perhaps shows a negative skew to losses



fig7 = go.Figure(go.Scatter(y=adf['pctchange'], 
                          x=adf['Date'],
                          mode='markers',
                          marker=dict(size=8, color=list(map(SetColor, adf['results'])))))

fig7.show()


# In[29]:


#   Setting marker colour based on competition


def SetColor2(x):
        if x == 'European':
            return "green"
        elif x == 'League':
            return "red"
        elif x == 'Acup':
            return "blue"


# In[30]:


#   Champions league results may have overall affected roma's stock negatively in 2017/18


fig8 = go.Figure(go.Scatter(y=adf['pctchange'], 
                          x=adf['Date'],
                          mode='markers',
                          marker=dict(size=8, color=list(map(SetColor2, adf['Competition'])))))

fig8.show()


# In[32]:


#   For season 2018/19, likewise losses at first glance may negatively impact stock price. 


fig9 = go.Figure(go.Scatter(y=bdf['pctchange'], 
                          x=bdf['Date'],
                          mode='markers', 
                          marker=dict(size=8, color=list(map(SetColor, bdf['results'])))))

fig9.show()


# In[34]:


#   Domestic results seem to be fairly evenly distributed. Champions league results seem slightly negatively skewed.



fig10 = go.Figure(go.Scatter(y=bdf['pctchange'], 
                          x=bdf['Date'],
                          mode='markers',
                          marker=dict(size=8, color=list(map(SetColor2, bdf['Competition'])))))

fig10.show()


# In[36]:


#   Creating the same groups, but applying the next-working-day function. This means getting rid of the first Matchday as this
#   just ends up as an extremely high outlier




cdf = pctchangenwd(roma1718).drop_duplicates(subset = ['Matchday']).reset_index(drop=True)
cdf = cdf.iloc[1:,]
ddf = pctchangenwd(roma1819).drop_duplicates(subset = ['Matchday']).reset_index(drop = True)
ddf = ddf.iloc[1:,]


#   Creating lists of next-working-day stock change for all competitions

AC_W1718_NWD = cdf.loc[cdf['results'] == 'W', 'pctchange'].dropna().tolist()
AC_D1718_NWD = cdf.loc[cdf['results'] == 'D', 'pctchange'].dropna().tolist()
AC_L1718_NWD = cdf.loc[cdf['results'] == 'L', 'pctchange'].dropna().tolist()

AC_W1819_NWD = ddf.loc[ddf['results'] == 'W', 'pctchange'].dropna().tolist()
AC_D1819_NWD = ddf.loc[ddf['results'] == 'D', 'pctchange'].dropna().tolist()
AC_L1819_NWD = ddf.loc[ddf['results'] == 'L', 'pctchange'].dropna().tolist()


#   Extracting just UEFA Champions League results

ucl1718_NWD = cdf.loc[cdf['Competition'] == 'European', ['results', 'pctchange']]
ucl1819_NWD = ddf.loc[ddf['Competition'] == 'European', ['results', 'pctchange']]

CL_W1718_NWD = ucl1718_NWD.loc[ucl1718_NWD['results'] == 'W', 'pctchange'].dropna().to_list()
CL_D1718_NWD = ucl1718_NWD.loc[ucl1718_NWD['results'] == 'D', 'pctchange'].dropna().to_list()
CL_L1718_NWD = ucl1718_NWD.loc[ucl1718_NWD['results'] == 'L', 'pctchange'].dropna().to_list()

CL_W1819_NWD = ucl1819_NWD.loc[ucl1819_NWD['results'] == 'W', 'pctchange'].dropna().to_list()
CL_D1819_NWD = ucl1819_NWD.loc[ucl1819_NWD['results'] == 'D', 'pctchange'].dropna().to_list()
CL_L1819_NWD = ucl1819_NWD.loc[ucl1819_NWD['results'] == 'L', 'pctchange'].dropna().to_list()

#   List of combined seasons for Champions League due to lack of data for one season.

CL_WSVS_NWD = CL_W1718_NWD + CL_W1819_NWD
CL_DSVS_NWD = CL_D1718_NWD + CL_D1819_NWD
CL_LSVS_NWD = CL_L1718_NWD + CL_L1819_NWD


#   Extracting just domestic results

dom1718_NWD = cdf.loc[cdf['Competition'] != 'European', ['results', 'pctchange']]
dom1819_NWD = ddf.loc[ddf['Competition'] != 'European', ['results', 'pctchange']]

DO_W1718_NWD = dom1718_NWD.loc[dom1718_NWD['results'] == 'W', 'pctchange'].dropna().to_list()
DO_D1718_NWD = dom1718_NWD.loc[dom1718_NWD['results'] == 'D', 'pctchange'].dropna().to_list()
DO_L1718_NWD = dom1718_NWD.loc[dom1718_NWD['results'] == 'L', 'pctchange'].dropna().to_list()

DO_W1819_NWD = dom1819_NWD.loc[dom1819_NWD['results'] == 'W', 'pctchange'].dropna().to_list()
DO_D1819_NWD = dom1819_NWD.loc[dom1819_NWD['results'] == 'D', 'pctchange'].dropna().to_list()
DO_L1819_NWD = dom1819_NWD.loc[dom1819_NWD['results'] == 'L', 'pctchange'].dropna().to_list()


# In[37]:


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

print('CL_W1718_NWD:')
maininfo(CL_W1718_NWD)
print('CL_L1718_NWD:')
maininfo(CL_L1718_NWD)
print('CL_D1718_NWD:')
maininfo(CL_D1718_NWD)

print('CL_W1819_NWD:')
maininfo(CL_W1819_NWD)
print('CL_L1819_NWD:')
maininfo(CL_L1819_NWD)
print('CL_D1819_NWD:')
maininfo(CL_D1819_NWD)

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

print('CL_WSVS_NWD:')
maininfo(CL_WSVS_NWD)
print('CL_LSVS_NWD;')
maininfo(CL_LSVS_NWD) 
print('CL_DSVS_NWD;')
maininfo(CL_DSVS_NWD) 


# In[38]:


#   Losses may cause slight declines in stock in the 2017/18 season


fig11 = go.Figure(go.Scatter(y=cdf['pctchange'], 
                          x=cdf['Date'],
                          mode='markers',
                          marker=dict(size=8, color=list(map(SetColor, cdf['results'])))))

fig11.show()


# In[43]:


#   Stock change after results seems fairly similar across competitions


fig12 = go.Figure(go.Scatter(y=cdf['pctchange'], 
                          x=cdf['Date'],
                          mode='markers',
                          marker=dict(size=8, color=list(map(SetColor2, cdf['Competition'])))))

fig12.show()


# In[40]:


#   Setting marker colour based on competition


def SetColor2(x):
        if x == 'European':
            return "green"
        elif x == 'League':
            return "red"
        elif x == 'Acup':
            return "red"


# In[44]:


#   Stock value changes based on result seems fairly similarly distributed in the 2018/19 season 


fig13 = go.Figure(go.Scatter(y=ddf['pctchange'], 
                          x=ddf['Date'],
                          mode='markers',
                          marker=dict(size=8, color=list(map(SetColor, ddf['results'])))))

fig13.show()


# In[45]:


#   Champions league results in this season may cause slight stock declines


fig14 = go.Figure(go.Scatter(y=ddf['pctchange'], 
                          x=ddf['Date'],
                          mode='markers',
                          marker=dict(size=8, color=list(map(SetColor2, ddf['Competition'])))))

fig14.show()


# In[46]:




################################################################################################################################
################################################################################################################################




#   Statistical analysis of results




################################################################################################################################
################################################################################################################################


# In[47]:


#   Getting all results together by competition


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


# In[48]:


#   Creating lists of results for analysis


GTG_AC_results1718 = [AC_W1718_GTG, AC_D1718_GTG, AC_L1718_NWD]
GTG_DO_results1718 = [DO_W1718_GTG, DO_D1718_GTG, DO_L1718_GTG]
GTG_AC_results1819 = [AC_W1819_GTG, AC_D1819_GTG, AC_L1819_GTG]
GTG_DO_results1819 = [DO_W1819_GTG, DO_D1819_GTG, DO_L1819_GTG]


NWD_AC_results1718 = [AC_W1718_NWD, AC_D1718_NWD, AC_L1718_NWD]
NWD_DO_results1718 = [DO_W1718_NWD, DO_D1718_NWD, DO_L1718_NWD]
NWD_AC_results1819 = [AC_W1819_NWD, AC_D1819_NWD, AC_L1819_NWD]
NWD_DO_results1819 = [DO_W1819_NWD, DO_D1819_NWD, DO_L1819_NWD]

GTG_SVS_results = [CL_WSVS_GTG,CL_LSVS_GTG]
NWD_SVS_results = [CL_WSVS_NWD,CL_LSVS_NWD]


# In[49]:


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


# In[50]:


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

print('\nGTG Champions league across all years Domestic Results: -------------------------------------\n')
statstest1(GTG_SVS_results)
print('\nNWD Champions league across all years Domestic Results: -------------------------------------\n')
statstest1(NWD_SVS_results)


# In[52]:


################################################################################################################################
################################################################################################################################


#   A second testing function is used to determine if there are significant differences between results (as a whole)
#   in the champions league, all competitions, and domestic competitions.  



# In[53]:


#   The same statistical tests are used here as earlier.


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
                print("All vs UCL WELCH T-TEST:", aa)
                if aa < 0.05:
                        print("These groups are different")
                else:
                    print("Could not find a difference")
            else:
                dd, aa = stats.ttest_ind(list[0], list[1])
                print("All vs UCL STUDENTS T-TEST", aa)
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
                    print("UCL vs Domestic WELCH T-TEST:", aa)
                    if aa < 0.05:
                        print("These groups are different")
                    else:
                        print("Could not find a difference")
                else:
                    dd, aa = stats.ttest_ind(list[1], list[2])
                    print("UCL vs Domestic STUDENTS T-TEST", aa)
                    if aa < 0.05:
                        print("These groups are different")
                    else:
                        print("Could not find a difference")
                        
    print("All vs UCL Kruskal:", e)
    if e < 0.05:
        print("These groups are different")
    else:
        print("Could not find a difference")
    
    print("All vs Domestic, Kruskal:", f)
    if f < 0.05:
        print("These groups are different")
    else:
        print("Could not find a difference")
        
    print("UCL vs Domestic Kruskal:", g)
    if g < 0.05:
        print("These groups are different")
    else:
        print("Could not find a difference")


# In[54]:


#   Creating lists of all results by competition


gtg_comp1718 = [all_1718_gtg, ucl_1718_gtg, dom_1718_gtg] 
gtg_comp1819 = [all_1819_gtg, ucl_1819_gtg, dom_1819_gtg]


nwd_comp1718 = [all_1718_nwd, ucl_1718_nwd, dom_1718_nwd]
nwd_comp1819 = [all_1819_nwd, ucl_1819_nwd, dom_1819_nwd]


# In[55]:


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


# In[56]:


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




