import requests
from bs4 import BeautifulSoup
import json
import sqlite3


DBNAME = 'tennis.db'
CACHE_FNAME = 'cache.json'

try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()

except:
    CACHE_DICTION = {}

def get_unique_key(url):
    return url

def make_request_using_cache(url):
    unique_ident = get_unique_key(url)

    if unique_ident in CACHE_DICTION:
        return CACHE_DICTION[unique_ident]
    else:
        resp = requests.get(url)
        CACHE_DICTION[unique_ident] = resp.text
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME, "w")
        fw.write(dumped_json_cache)
        fw.close()
        return CACHE_DICTION

class MatchInfo:
    def __init__(self, winningPlayer, losingPlayer, tournamentName, year):
        self.winner = winningPlayer
        self.loser = losingPlayer
        self.tournament = tournamentName
        self.year = year

    def __str__(self):
        return "Winner:" + self.winner + " and Loser:" + self.loser + " at " + self.tournament + " in " + self.year

class TennisRankings:
    def __init__(self, playerName, currentRanking, playerCountry = None):
        self.name = playerName
        self.ranking = currentRanking
        self.country = playerCountry

    def __str__(self):
        return self.ranking + " " + self.name + " " + self.country

    def get_name(self):
        return self.name

    def get_ranking(self):
        return self.ranking

    def get_country(self):
        return self.country




def get_rankings(year, type):
    base_url = 'http://www.espn.com/tennis/rankings/_/'
    if type == 'ATP':
        rankings_url = base_url + 'year/' + year
    if type == 'WTA':
        rankings_url = base_url + 'type/2/year/' + year
    rankings_text = make_request_using_cache(rankings_url)
    rankings_soup = BeautifulSoup(rankings_text, 'html.parser')
    table_content = rankings_soup.find(class_= 'tablehead')
    odd_players = table_content.find_all("tr")
    odd_number = len(odd_players)
    players = []
    garbage = []
    for i in range(odd_number):
        if i == 0 or i == 1:
            garbage = odd_players[i]
        else:
            player = odd_players[i]
            ranking = player.find('td').text.strip()
            playerName = player.find('a').text.strip()
            playerCountry = player.find('img')['title']
            single_player = TennisRankings(playerName, ranking, playerCountry)
            players.append(single_player)
    return players

def crawl_records(yearStart, yearEnd, tournament, player, matchType):
    matches = []
    base_url = 'http://www.espn.com/tennis/dailyResults'
    add = "?date=" + yearStart + '0915'
    year = yearStart
    while int(year) <= int(yearEnd):
        full_url = base_url + add
        print(full_url)
        scores_text = make_request_using_cache(full_url)
        scores_soup = BeautifulSoup(scores_text, 'html.parser')
        week_view = scores_soup.find(class_= 'view')
        current_day = week_view.find(class_= 'current')
        allDays = week_view.find("ul")
        realAllDays = allDays.find_all('li')
        indexToday = realAllDays.index(current_day)
        if (indexToday == 6):
            return
        tomorrow = realAllDays[indexToday + 1]
        add = tomorrow.find("a")['href']
        num_matches = current_day.find(class_= 'num-games').text.strip()
        num_matches = num_matches.split()[0]
        if (num_matches > 0):
            headline = scores_soup.find(class_= 'scoreHeadline')
            tournament_name = headline.find('a').text.strip()
            year = tournament_name[:4]
            correct_tournament = False
            for i in range(4):
                if tournaments[i] in tournament_name:
                    correct_tournament = True
                    finalTournamentName = tournaments[i]
                    break
            if correct_tournament == True:
                matchContainer = scores_soup.find_all(class_= "matchContainer")
                for i in range (len(matchContainer)):
                    player1 = matchContainer[i].find(class_= 'teamLine')
                    player1name = player1.find("a").text.strip()
                    player2 = matchContainer[i].find(class_='teamLine2')
                    player2name = player2.find("a").text.strip()
                    if player == player1name or player == player2name:
                        try:
                            player1Won = player1.find(class_= 'arrowWrapper')
                        except:
                            pass
                        try:
                            player2Won = player2.find(class_= 'arrowWrapper')
                        except:
                            pass
                    if (player1Won):
                        WinningPlayer = player1name
                        LosingPlayer = player2name
                    elif (player2Won):
                        WinningPlayer = player2name
                        LosingPlayer = player1name
                    singleMatch = MatchInfo(WinningPlayer, LosingPlayer, finalTournamentName, year)
                    matches.append(singleMatch)
        if year == yearEnd:
            return
    for i in matches:
        print(i)







def get_tournament_details():
    full_url = 'https://en.wikipedia.org/w/api.php?action=parse&prop=wikitext&format=json&rvprop=content&page=Grand_Slam_(tennis)&section=3'
    grand_slam_text = make_request_using_cache(full_url)
    print(grand_slam_text)


def init_rankings_db():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    statement = '''
    DROP TABLE IF EXISTS 'Rankings'
    '''

    cur.execute(statement)



    statement1 = '''
    CREATE TABLE `Rankings` (
	  `PlayerId`INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	  `Ranking`	INTEGER NOT NULL,
	  'PlayerName' TEXT NOT NULL,
      'PlayerCountry'
     );
    '''

    cur.execute(statement1)
    conn.commit()
    conn.close()

def populate_db(playersNames, playersRankings, playersCountries):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    length = len(playersNames)
    for x in range (0, length):
        insertion = (None, playersRankings[x], playersNames[x], playersCountries[x])
        statement = 'INSERT INTO "Rankings"'
        statement += 'VALUES (?, ?, ?, ?)'
        cur.execute(statement, insertion)

    conn.commit()
    conn.close()

def init_tournament_db():
    conn = sqlite.connect(DBNAME)
    cur = conn.cursor
    statement = '''
        DROP TABLE IF EXISTS 'GrandSlams'
    '''

    cur.execute(statement)

    statement1 = '''
        CREATE TABLE 'GrandSlams'(
            'Id' INTEGER NOT NULL PRIMARY KEY,
            'Name' TEXT NOT NULL,
            'Location' TEXT NOT NULL,
            'Surface' TEXT NOT NULL,
            'Date' TEXT NOT NULL,
            'Venue' TEXT NOT NULL
        );
    '''
    cur.execute(statement)
    conn.commit()
    conn.close()

def populate_gs_db(names, locations, surfaces, dates, venues):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    length = len(names)
    for x in range (0, length):
            insertion = (None, names[x], locations[x], surfaces[x], dates[x], venues[x])
            statement = 'INSERT INTO "GrandSlams"'
            statement += 'VALUES (?, ?, ?, ?, ?, ?)'
            cur.execute(statement, insertion)
    conn.commit()
    conn.close()


def init_matches_db():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    statement = '''
    DROP TABLE IF EXISTS 'Matches'
    '''

    cur.execute(statement)


    statement2 = '''
    CREATE TABLE `Matches` (
	  `PlayerWinId`INTEGER NOT NULL FOREIGN KEY,
      'PlayerLossId' INTEGER NOT NULL FOREIGN KEY,
      'PlayerWinName' TEXT NOT NULL,
      'PlayerLossName' TEXT NOT NULL,
      'Tournament' TEXT NOT NULL
      'Tournament Id' INTEGER NOT NULL FOREIGN KEY,
      'Year' INTEGER NOT NULL
     );
    '''

    cur.execute(statement2)
    conn.commit()
    conn.close()


if __name__=="__main__":
    tournaments = ['US Open', 'French Open', 'Australian Open', 'Wimbledon']
    players = []
    names = []
    countries = []
    rankings = []
    players = get_rankings('2018', 'ATP')
    for i in range(0, len(players)):
        print(players[i])
        names.append(players[i].get_name())
        rankings.append(players[i].get_ranking())
        countries.append(players[i].get_country())
    init_rankings_db()
    populate_db(names, rankings, countries)
    crawl_records('2015','2015', tournaments, 'Stan Wawrinka', 'ATP')
