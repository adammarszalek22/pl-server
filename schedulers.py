import requests
import json

from flask_apscheduler import APScheduler

from db import db
from models import MatchesModel, UserModel, GroupsModel

def initialize_schedulers(app):

    matches_scheduler = APScheduler()
    scheduler = APScheduler()
    group_pos_scheduler = APScheduler()

    scheduler_time = 200
    matches_scheduler.add_job(id = 'Updating matches',
                      func = get_matches,
                      args = [app],
                      trigger = 'interval',
                      seconds = scheduler_time)
    scheduler.add_job(id = 'Comparing scores',
                      func = compare_scores,
                      args = [app],
                      trigger = 'interval',
                      seconds = scheduler_time)
    group_pos_scheduler.add_job(id = 'Group positions',
                      func = groups_positions,
                      args = [app],
                      trigger = 'interval',
                      seconds = scheduler_time)
    
    matches_scheduler.start()
    scheduler.start()
    group_pos_scheduler.start()


def get_matches(app):

    # getting match info from the fantasy premier league API
    with app.app_context():
        url = 'https://fantasy.premierleague.com/api/fixtures/'
        request = requests.get(url)
        response = json.loads(request.content)

        for i in response:
            match = MatchesModel.query.filter(
                MatchesModel.match_id == str(i["code"])
                ).first()
            
            if match:
                # if match is already in database, update match info
                match.start_time = i["kickoff_time"]
                match.finished = i["finished"]
                match.goal1 = i["team_h_score"]
                match.goal2 = i["team_a_score"]
                db.session.add(match)
                db.session.commit()
            else:
                # otherwise add match to the database
                # (usually all matches are added at the start of the season)
                match = MatchesModel(
                    match_id = i["code"],
                    goal1 = i["team_h_score"],
                    goal2 = i["team_a_score"],
                    start_time = i["kickoff_time"],
                    finished = i["finished"]
                )
                db.session.add(match)
                db.session.commit()

def compare_scores(app):

    # this function compares users' scores to actual scores and awards points
    with app.app_context():
        users = UserModel.query.all()

        for user in users:
            # for every match score prediction made by user

            for bet in user.bets:
                match = MatchesModel.query.filter(MatchesModel.match_id == bet.match_id).first()

                if match and match.finished == True and bet.done == "no":
                    points = compare(bet.goal1, bet.goal2, match.goal1, match.goal2)
                    # adding points
                    user.points += points
                    if points == 3:
                        user.three_pointers += 1
                    elif points == 1:
                        user.one_pointers += 1
                    # changing to 'yes' so that next time this game is skipped 
                    bet.done = "yes"
                    db.session.add(user)
                    db.session.commit()

        # positions function is run at the end of this function and not in the scheduler
        # this is to avoid functions executing at the same time as they both interact with the UserModel
        positions(app)
    
def positions(app):

    # this function decides users' standings in the main league
    with app.app_context():

        # creating a dict with all users
        positions = {}
        users = UserModel.query.all()

        for user in users:
            positions[user.id] = {}
            positions[user.id]["points"] = int(user.points)
            positions[user.id]["three_pointers"] = int(user.three_pointers)
            positions[user.id]["one_pointers"] = int(user.one_pointers)

        # sorting the dict by points, if 2 users have the same amount of points then whoever has more three pointers is higher
        positions = {k: v for k, v in sorted(positions.items(), key=lambda item: (item[1]["points"], item[1]["three_pointers"]), reverse=True)}

        standing = 1
        for player_id in positions.keys():
            # assigning the standings to the users
            user = UserModel.query.get_or_404(player_id)
            user.position = standing
            db.session.add(user)
            db.session.commit()
            standing += 1

def groups_positions(app):

    # same as the positions() function but for each small league 
    with app.app_context():
        groups = GroupsModel.query.all()

        for group in groups: 
            positions = {}
            
            for user in group.user:
                positions[user.id] = {}
                positions[user.id]["points"] = int(user.points)
                positions[user.id]["three_pointers"] = int(user.three_pointers)
                positions[user.id]["one_pointers"] = int(user.one_pointers)
                
            positions = {k: v for k, v in sorted(positions.items(), key=lambda item: (item[1]["points"], item[1]["three_pointers"]), reverse=True)}
            pos = []
            for i in positions.keys():
                pos.append(i)
            pos_string = ' '.join(map(str, pos))
            group.positions = pos_string
            db.session.add(group)
            db.session.commit()

def compare(a, b, c, d):
    
    # a, b - predicted score; c, d - actual score
    if a == c and b == d:
        # 3 points for guessing the exact score
        return 3
    # 1 point for guessing the winner or draw ↓
    if a > b and c > d:
        return 1
    if b > a and d > c:
        return 1
    if a == b and c == d:
        return 1
    # else 0 points
    return 0