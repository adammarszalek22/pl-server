import requests
import json
from db import db
from models import BetsModel, UserModel

'''
IN PROGRESS. THIS IS NOT IMPLEMENTED IN THE FLASK APP FOR NOW.
'''

def get(url):
    response = requests.get(url)
    return json.loads(response.content)

url = 'https://fantasy.premierleague.com/api/bootstrap-static/'

url_1 = 'https://fantasy.premierleague.com/api/fixtures/'

response = get(url)

response_1 = get(url_1)

#teams - id, name, matches_played, wins, draws, losses,
#goals_scored, goals_conceded, goal balance, points

#matches - gameweek, team1, team2, score1, score2,
#kickoff_date, kickoff_time, finished, code

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
    
positions = {k: v for k, v in sorted(teams.items(), key=lambda item: (item[1]['points'], item[1]['goals_scored'], item[1]['goals_balance']), reverse=True)}


def get(user_id, match_id):
    #Retrieves the bets from database
    bet = BetsModel.query.filter(
        BetsModel.user_id == user_id,
        BetsModel.match_id == match_id
    ).first()
    return bet

def compare1(gameweek, match_id, user_id):
    #Compares bets and actual scores
    db_bet = get(user_id, match_id)
    score1 = matches['Gameweek ' + str(gameweek)][match_id]['goals1']
    score2 = matches['Gameweek ' + str(gameweek)][match_id]['goals2']
    if db_bet:
        print(score1, score2, db_bet.goal1, db_bet.goal2)
    try:
        if db_bet.goal1 == score1 and db_bet.goal2 == score2:
            return 3
        elif score1 > score2 and db_bet.goal1 > db_bet.goal2:
            return 1
        elif score1 == score2 and db_bet.goal1 == db_bet.goal2:
            return 1
        elif score1 < score2 and db_bet.goal1 < db_bet.goal2:
            return 1
        else:
            return 0
    except AttributeError:
        return 0

def add_points(user_id, points):
    #Adds points to users account
    user = UserModel.query.filter(
        UserModel.id == user_id
    ).first()
    user.points = points
    print(points, 'added')
    db.session.add(user)
    db.session.commit()

def compare(user_id=1):
    points = 0
    for i in range(1, 39):
        for i2 in matches['Gameweek ' + str(i)].keys():
            a = int(compare1(i, i2, 1))
            points += a
    add_points(user_id, points)



    




