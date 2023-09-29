# A server side of a Premier League score prediction app

This is a server app that allows users to post their Premier League score predictions. Every user get awarded 3 points (three_pointer) for guessing the exact score or 1 point (one_pointer) for guessing the right winner (or draw). 

# How it works

Once a user registers they are added to the global league where their scores are compared with everyone else's scores. They can also create smaller leagues and invite friends to join.

Every user can post or update their match predictions before the particular gameweek starts. Once the gameweek starts, no changes are possible. A scheduler runs every few minutes that calculates users points and updates their leagues standings (both global and small leagues).

I am currently developing a mobile app that will interact with the server. You can view it at https://github.com/adammarszalek22/pl.

# Running the app

The current version of this app can be run with 'flask run' or by using Docker. The modules from requirements.txt need to be installed using the command 'pip install -r requirements.txt'.
(.env file is needed with DATABASE_URL)
