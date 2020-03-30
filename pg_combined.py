import pandas as pd
import datetime as dt
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
    
    df = df.loc[~(df['MP'].isnull())]
    df['Date'] = pd.to_datetime(df['Date'], format = '%Y-%m-%d').dt.date #convert date columns into date format to split table into before and after all-star game
    float_cols = ['FG%','3P%', 'FT%', 'GmSc']
    int_cols = ['FG', 'FGA',  '3P', '3PA', 'FT', 'FTA',  'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS',  '+/-',]
    for col in float_cols:
        df[col] = pd.to_numeric(df[col], errors = 'coerce') #need to write for loop as cannot coerce dataframe into numeric type, need do as list
    df[int_cols] = df[int_cols].astype(int)    
    
    return df


pg = extract_pg_stats(2011,2012) #Extract stats from 2011-2012 season and 2012-2013 season and combine them together into 1 dataset



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
    plt.title("Paul George {year}-{year1}".format(year = year, year1 = year + 1))
    print(bfasg[category].describe())
    print(afasg[category].describe())
    return plt.show()


comparison('FG%', 2012) #Show performance before and after 2013 All-Star game (2012-2013 Season)

#Generate bar chart for each season comparing mean of desired category before and after all-star break
def bar_chart_comparison(category, start_year, end_year):

    def afasg_mean(category, year):  #year input is the season in which the all-star game belongs to. Therefore if want all-star game in 2011-2012 season, enter 2011
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
        afasg = pg_season.loc[pg_season['Date'] > asg_date(allstaryear)]
        afasg_dist = afasg[category].describe().values[1]
        return afasg_dist
    
    def bfasg_mean(category, year):  #year input is the season in which the all-star game belongs to. Therefore if want all-star game in 2011-2012 season, enter 2011
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
        bfasg_dist = bfasg[category].describe().values[1]
        return bfasg_dist

    pg_mean = pd.DataFrame()
    bfasg_list = []
    afasg_list = []
    for i in range(start_year,end_year+1):
        bfasg_list.append(bfasg_mean(category, i))
        afasg_list.append(afasg_mean(category, i))
    
    pg_mean['Before All Star Game Mean'] = bfasg_list
    pg_mean['After All Star Game Mean'] = afasg_list
    #https://python-graph-gallery.com/11-grouped-barplot/

    barWidth = 0.25
    bars1 = pg_mean['Before All Star Game Mean']
    bars2 = pg_mean['After All Star Game Mean']

    r1 = np.arange(len(bars1)) #arange(len(bars1)) + barWidth
    r2 = [x + barWidth for x in r1]

    plt.bar(r1, bars1, color='yellow', width=barWidth, edgecolor='white', label='Before All Star Game mean {}'.format(category))
    plt.bar(r2, bars2, color='blue', width=barWidth, edgecolor='white', label='After All Star Game mean {}'.format(category))
    plt.xlabel('Season', fontweight='bold')
    plt.xticks([r + barWidth for r in range(len(bars1))], list(range(start_year,end_year+1)))
    
    plt.legend()
    return plt.show()


