import pandas as pd
import datetime as dt
#import math
import requests
from bs4 import BeautifulSoup


#Extracting required data straight from basketball-reference
def extract_pg_stats(lower_bound, upper_bound):
    span = list(range(lower_bound +1, upper_bound + 2))
    df = pd.DataFrame()
    for year in span:
            url = "https://www.basketball-reference.com/players/g/georgpa01/gamelog/{}/".format(year)
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'html.parser')
            table_div = soup.find('div' , {'id': 'div_pgl_basic', 'class': 'overthrow table_container' })
            tb = table_div.find('tr')
            rows = tb.findAll('th')[1:] #Ignore 'Rk' column first
            headers = [rows[i].get_text() for i in range(len(rows))] #Extracting header name for each column

            tbody = table_div.find('tbody')
            selected_rows = tbody.findAll('tr')
            player_stats = [[td.getText() for td in selected_rows[i].findAll('td')] for i in range(len(selected_rows))]

            df1 = pd.DataFrame(player_stats, columns = headers)
            
            df1['Season'] = year-1
            df = pd.concat([df, df1])
            
    return df


pg = extract_pg_stats(2011,2011) #Example

#Filter out any games in which he did not play
pg = pg.loc[~(pg['MP'].isnull())]
#pg['GS'].value_counts() #to determine labels for when he did not play
#pg = pg[~(pg['GS'] == 'Inactive') & ~(pg['GS'] == 'Did Not Dress') & ~(pg['GS'] == 'Did Not Play')]

#Add for indexing purposes
pg['Rk'] = range(pg.shape[0])




pg['Date'] = pd.to_datetime(pg['Date'], format = '%Y-%m-%d').dt.date #convert date columns into date format to split table into before and after all-star game
float_cols = ['FG%','3P%', 'FT%', 'GmSc']
int_cols = ['FG', 'FGA',  '3P', '3PA', 'FT', 'FTA',  'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS',  '+/-',]
for col in float_cols:
    pg[col] = pd.to_numeric(pg[col], errors = 'coerce') #need to write for loop as cannot coerce dataframe into numeric type, need do as list
pg[int_cols] = pg[int_cols].astype(int)
pg.info()

#Convert MP column to time format
#pg['MP'][pg['MP'].str.count(":") == 1] += ":00" #some time formats do not have microseconds, therefore add them to those that don't have so can convert all to time format
#pg['MP'] = pg['MP'].str.replace(":00$","")
#seconds_played = (pd.to_datetime(pg['MP'], format = '%M:%S').dt.minute)*60 + (pd.to_datetime(pg['MP'], format = '%M:%S').dt.second)
#mean_seconds_played = (seconds_played.sum())/543
#mean_minutes_played = mean_seconds_played/60
#mean_duration_played = dt.datetime.strptime(str(int(math.modf(mean_minutes_played)[1])) + ":" + str(round(math.modf(mean_minutes_played)[0]*60)), '%M:%S').strftime('%M:%S')
#(pd.to_datetime(pg['MP'], format = '%M:%S').dt.time > mean_duration_played.time()).sum()


def comparison(category, year):  #year input is the season in which the all-star game belongs to. Therefore if want all-star game in 2011-2012 season, enter 2011
    allstaryear = year + 1 #All star year begins in year after the year in which season starts e.g. 2011-2012 season will have 2012 all-star game
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
    
    pg_season = pg.loc[pg['Season'] == year]
    bfasg = pg_season.loc[pg_season['Date'] < asg_date(allstaryear)]
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




comparison('FG%', 2011) 


#make bar chart of mean fg%, pts, +/- for before and after all-star game for each season
