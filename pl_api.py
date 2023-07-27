import requests
import json
from db import db
from models import BetsModel, UserModel

'''
THIS WILL NOT BE USED
'''

def get(url):
    response = requests.get(url)
    return json.loads(response.content)

url = 'https://fantasy.premierleague.com/api/bootstrap-static/'

url_1 = 'https://fantasy.premierleague.com/api/fixtures/'

response = get(url)

response_1 = get(url_1)

teams = {}
for i in response["teams"]:
    teams[i['id']] = {}
    teams[i['id']]['id'] = i['id']
    teams[i['id']]['name'] = i['name']
    teams[i['id']]['matches_played'] = 0
    teams[i['id']]['wins'] = 0
    teams[i['id']]['draws'] = 0
    teams[i['id']]['losses'] = 0
    teams[i['id']]['goals_scored'] = 0
    teams[i['id']]['goals_conceded'] = 0
    teams[i['id']]['goals_balance'] = 0
    teams[i['id']]['points'] = 0

matches = {}
for i in range(1, 39):
    matches['Gameweek ' + str(i)] = {}

for i in response_1:
    matches['Gameweek ' + str(i['event'])][str(i['code'])] = {}
    matches['Gameweek ' + str(i['event'])][str(i['code'])]['team1'] = i['team_h']
    matches['Gameweek ' + str(i['event'])][str(i['code'])]['team2'] = i['team_a']
    matches['Gameweek ' + str(i['event'])][str(i['code'])]['goals1'] = i['team_h_score']
    matches['Gameweek ' + str(i['event'])][str(i['code'])]['goals2'] = i['team_a_score']
    matches['Gameweek ' + str(i['event'])][str(i['code'])]['kickoff_date'] = i['kickoff_time'][0:10]
    matches['Gameweek ' + str(i['event'])][str(i['code'])]['kickoff_time'] = i['kickoff_time'][11:19]
    matches['Gameweek ' + str(i['event'])][str(i['code'])]['finished'] = i['finished']
    matches['Gameweek ' + str(i['event'])][str(i['code'])]['started'] = i['started']

    if i['team_h_score'] != None:

        if i['team_h_score'] > i['team_a_score']:
            teams[i['team_h']]['points'] += 3
            teams[i['team_h']]['wins'] += 1
            teams[i['team_a']]['losses'] += 1
        elif i['team_h_score'] < i['team_a_score']:
            teams[i['team_a']]['points'] += 3
            teams[i['team_a']]['wins'] += 1
            teams[i['team_h']]['losses'] += 1
        else:
            teams[i['team_h']]['points'] += 1
            teams[i['team_a']]['points'] += 1
            teams[i['team_h']]['draws'] += 1
            teams[i['team_a']]['draws'] += 1

        teams[i['team_h']]['matches_played'] += 1
        teams[i['team_a']]['matches_played'] += 1

        teams[i['team_h']]['goals_scored'] += i['team_h_score']
        teams[i['team_a']]['goals_scored'] += i['team_a_score']

        teams[i['team_h']]['goals_conceded'] += i['team_a_score']
        teams[i['team_a']]['goals_conceded'] += i['team_h_score']

        teams[i['team_h']]['goals_balance'] += i['team_h_score'] - i['team_a_score']
        teams[i['team_a']]['goals_balance'] += i['team_a_score'] - i['team_h_score']

print(teams)
    
positions = {k: v for k, v in sorted(teams.items(), key=lambda item: (item[1]['points'], item[1]['goals_balance'], item[1]['goals_scored']), reverse=True)}

print(positions)




