# LoL-Data-Fetcher
Uses Riot Game's API to collect my data for my League of Legends games and submit them to a personal MySQL database.

### Python Script
The script uses [RiotWatcher](https://github.com/pseudonym117/Riot-Watcher), a small Python wrapper for the Riot Games API. It's main use in my application is to handle rate limit errors. In order to preserve security and API agreements, the database login and API key are stored in a seperate JSON file not uploaded to GitHub.

#### Usage:
Updating games for all the current summoners in the DB:   
`python api_grabber.py`

Adding a summoner to the database:    
`python api_grabber.py add_summoner <summoner_name> <region code>`
### MySQL
The database server runs on my local server machine, and the schema for the database is defined in the `league db.sql` file. Python interacts with the database through the `mysql-connector` library.
