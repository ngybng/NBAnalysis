import pandas as pd
import datetime as dt
import math
import requests
from bs4 import BeautifulSoup

pg_1112 = pd.read_csv("pg_1112.csv", index_col = False)
pg_1213 = pd.read_csv("pg_1213.csv", index_col = False)
pg_1314 = pd.read_csv("pg_1314.csv", index_col = False)
pg_1415 = pd.read_csv("pg_1415.csv", index_col = False)
pg_1516 = pd.read_csv("pg_1516.csv", index_col = False)
pg_1617 = pd.read_csv("pg_1617.csv", index_col = False)
pg_1718 = pd.read_csv("pg_1718.csv", index_col = False)
pg_1819 = pd.read_csv("pg_1819.csv", index_col = False)
pg_1920 = pd.read_csv("pg_1920.csv", index_col = False)

#Add new column 'Season' for filtering later 
pg_1112['Season'] = 2011
pg_1213['Season'] = 2012
pg_1314['Season'] = 2013
pg_1415['Season'] = 2014
pg_1516['Season'] = 2015
pg_1617['Season'] = 2016
pg_1718['Season'] = 2017
pg_1819['Season'] = 2018
pg_1920['Season'] = 2019

#Stack datasets on top of each other into one whole dataset
pg = pd.concat([pg_1112, pg_1213, pg_1314, pg_1415, pg_1516, pg_1617, pg_1718, pg_1819, pg_1920 ], axis=0)

#Filter out any games in which he did not play
pg['MP'].value_counts() #to determine labels for when he did not play
pg = pg[~(pg['MP'] == 'Inactive') & ~(pg['MP'] == 'Did Not Dress') & ~(pg['MP'] == 'Did Not Play')]
pg['Date'] = pd.to_datetime(pg['Date'], format = '%d/%m/%Y').dt.date #convert date columns into date format to split table into before and after all-star game
float_cols = ['FG%','3P%', 'FT%', 'GmSc']
int_cols = ['FG', 'FGA',  '3P', '3PA', 'FT', 'FTA',  'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS',  '+/-',]
pg[float_cols] = pg[float_cols].astype(float) #convert object type columns to float
pg[int_cols] = pg[int_cols].astype(int) #convert object type columns to integer
pg.info()


def comparison(category, year):  
    allstaryear = year + 1 #All star year begins in year after the year in which season starts e.g. 2011-2012 season will have 2012 all-star game
    
    #Define function that takes year input and extracts All-Star Game date from corresponding Wikipedia article
    def asg_date(allstaryear):
        if year < 2010:
            return("Haven't made debut yet")
        elif  year > 2019:
            return("Hasn't taken place yet")
    
        else:
            url = "https://en.wikipedia.org/wiki/{}_NBA_All-Star_Game".format(allstaryear)
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'html.parser')
            tb = soup.find('table', class_='infobox vevent')
            tb_1 = tb.find('tbody')
            date = tb_1.find_all('tr')[5]
            date = date.find('td').get_text()
            date = dt.datetime.strptime(date,  '%B %d, %Y').date()
            return date
    
    #Filters relevant data from combined dataset based on year input
    pg_season = pg.loc[pg['Season'] == year]
    bfasg = pg_season.loc[pg_season['Date'] < asg_date(allstaryear)] #Splits dataset into before and after all-star game (date extracted in previous function)
    afasg = pg_season.loc[pg_season['Date'] > asg_date(allstaryear)]
    
    
    import matplotlib.pyplot as plt
    fig, ax1 = plt.subplots()
    ax2 = ax1.twiny()

    bfasg_plot, = ax1.plot(bfasg['G'], bfasg[category] ,  label = '{} per game before All-Star break'.format(category), c = 'red') #need comma in front of variable name
    afasg_plot, = ax2.plot(afasg['G'], afasg[category], label = '{} per game after All-Star break'.format(category), c = 'black') #need comma in front of variable name
    curves = [bfasg_plot, afasg_plot]

    ax1.set_xlabel("Game # (before All-Star)", c = 'red')
    ax2.set_xlabel("Game # (after All-Star)", c = 'black')
    ax1.set_ylabel("{} per game".format(category))
    ax1.legend(curves, [curve.get_label() for curve in curves])
    plt.title("Paul George")
    print(bfasg[category].describe())
    print(afasg[category].describe())
    return plt.show()






