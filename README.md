# A server side of a Premier League score prediction app

This is a server app that allows users to post their Premier League score predictions. Every user get awarded 3 points (three_pointer) for guessing the exact score or 1 point (one_pointer) for guessing the right winner (or draw).

The server is live and can be connected to with this link 'https://pl-server.onrender.com' (append the desired routes from resources files, for example 'https://pl-server.onrender.com/register')

# How it works

Once a user registers they are added to the global league where their scores are compared with everyone else's scores. They can also create smaller leagues and invite friends to join.

Every user can post or update their match predictions before the particular gameweek starts. Once the gameweek starts, no changes are possible. A scheduler runs every few minutes that calculates users points and updates their leagues standings (both global and small leagues).

I have developed a mobile app that will interact with the server. You can view it at https://github.com/adammarszalek22/pl.
I am also creating a website for this. You can view the progress here - https://github.com/adammarszalek22/pl-website.

# Running the app

The current version of this app can be run with 'flask run' or by using Docker. The modules from requirements.txt need to be installed using the command 'pip install -r requirements.txt'.
(.env file is needed with DATABASE_URL)

# TODOS (DONE)
- clean up the code - main file - done

# TODOS
- add routes documentation
- make registration return access_tokens
- clean up the code
- to research stuff like pagination, sorting, etc. in the routes. I have learnt that in node.js but need to implement it here too, especially for when there is lots of users (that would be much more efficient than doing '/get_all', etc.)
- some of the database tables aren't setup in the most efficient way or are lacking certain columns, to be looked into
- MOVE THE DATABASE BY JAN 2025 AS ELEPHANTSQL WILL STOP WORKING