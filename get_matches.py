import requests
import json
from db import db
from models import MatchesModel

'''
IN PROGRESS. THIS IS NOT IN THE FLASK APP FOR NOW.
'''

def get(url):
    response = requests.get(url)
    return json.loads(response.content)



def matches():

    url = 'https://fantasy.premierleague.com/api/fixtures/'

    response = get(url)

    for i in response:

        if MatchesModel.query.filter(MatchesModel.match_id == i["code"]).first():
            pass
        else:
            #if i["finished"] == True:
            match = MatchesModel(
                match_id = i["code"],
                goal1 = i["team_h_score"],
                goal2 = i["team_a_score"],
                done = "no"
            )
            db.session.add(match)
            db.session.commit()

