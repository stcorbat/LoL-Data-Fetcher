import sys
import time
import json

from riotwatcher import LolWatcher, ApiError
import mysql.connector

import match_fetcher


def progress_bar(current, total, bar_length=25):
    percent = float(current) * 100 / total
    arrow = '-' * int(percent / 100 * bar_length - 1) + '>'
    spaces = ' ' * (bar_length - len(arrow))

    print('[%s%s] %d %%' % (arrow, spaces, percent), end='\r')
    if percent == 100:
        print()


# queries the summoner's matchlist and returns a list containing matches after the specified time
def matchlist_query_by_time(region, account_id, lol_watcher, begin_time):
    try:
        response = lol_watcher.match.matchlist_by_account(region, account_id, begin_time=begin_time)
    except ApiError as err:
        if err.response.status_code == 429:
            print('API Rate limit reached')
        elif err.response.status_code == 404:
            print('No new matches found for Account ID: {}'.format(account_id))
            return None
        else:
            raise

    matchlist = response['matches']
    return matchlist


def get_all_summoner_matches(region, account_id, lol_watcher):
    # maximum range of indices for match lists can only be 100
    index = 0
    matches = []
    while True:
        try:
            response = lol_watcher.match.matchlist_by_account(region, account_id, begin_index=index)
        except ApiError as err:
            if err.response.status_code == 429:
                print('API Rate limit reached')
                time.sleep(10)
                continue
            elif err.response.status_code == 404:
                print('No  matches found for Account ID: {}'.format(account_id))
                return None
            else:
                raise

        if response['matches'].__len__() == 0:
            break

        matches.extend(response['matches'])
        index += 100

    print('Found', len(matches), 'to add for Account ID:', account_id)
    return matches


def commit_new_games(db, vals, summoner_name):
    cursor = db.cursor(buffered=True)
    sql_format = "INSERT INTO SummonerMatches VALUES (" \
                 "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s" \
                 ")"

    cursor.executemany(sql_format, vals)
    db.commit()
    print(cursor.rowcount, " games added for ", summoner_name)


def update_games(summoner_json, lol_watcher, db):
    account_id = summoner_json[0]
    name = summoner_json[1]
    region = summoner_json[2]

    cursor = db.cursor(buffered=True)

    cursor.execute(
        "SELECT COUNT(*) FROM SummonerMatches WHERE account_id = '" + account_id + "'"
    )
    count = cursor.fetchone()[0]
    # if there are already matches in the db, only fetch new matches, else start from 0
    if count == 0:
        matchlist = get_all_summoner_matches(region, account_id, lol_watcher)
        print("Initializing all matches for ", name)
    else:
        cursor.execute(
            "SELECT match_timestamp FROM SummonerMatches WHERE account_id = '" + account_id +
            "' ORDER BY match_timestamp DESC"
        )
        # add one here so the match query doesn't include the most recent match
        begin_time = cursor.fetchone()[0] + 1
        # retrieves matchlist according to starting time
        matchlist = matchlist_query_by_time(region, account_id, lol_watcher, begin_time)

    if matchlist is None:
        return

    # holds game data for the summoner like champion, kills, deaths, etc.
    vals = []

    for index, match in enumerate(matchlist):
        game_id = match['gameId']
        timestamp = match['timestamp']
        queue = match['queue']
        season = match['season']

        progress_bar(index + 1, len(matchlist))
        match_data = match_fetcher.collect_match_data(region, account_id, game_id, lol_watcher)
        if match_data is None:
            print("Invalid match data!")
            return

        if match_data['duration'] <= 300:
            continue

        vals.append((
            account_id, game_id, timestamp, queue, season, match_data['duration'], match_data['win'],
            match_data['champion'], match_data['kills'], match_data['deaths'], match_data['assists'],
            match_data['gold_earned'], match_data['champion_damage'], match_data['objective_damage'],
            match_data['damage_healed'], match_data['vision_score'], match_data['control_wards_purchased'],
            match_data['minions_killed'], match_data['neutral_monsters_killed']
        ))

    commit_new_games(db, vals, name)


def main():
    config = json.load(open('config.json'))

    db = mysql.connector.connect(
        host=config['host'],
        user=config['username'],
        passwd=config['password'],
        database=config['database']
    )

    cursor = db.cursor(buffered=True)

    cursor.execute('SELECT * FROM Summoners')
    summoners = cursor.fetchall()

    watcher = LolWatcher(config['api_key'])

    if len(sys.argv) > 1 and sys.argv[1] == 'add_summoner':
        if len(sys.argv) < 4:
            print('Expected more arguments.  Format: add_summoner <summoner_name> <region>')
            return
        # adds a summoner to the db instead of running the normal updates
        region = sys.argv[3]
        name = sys.argv[2]
        summoner = watcher.summoner.by_name(region, name)

        sql = 'INSERT INTO Summoners VALUES (%s, %s, %s)'
        val = (summoner['accountId'], name, region)

        cursor.execute(sql, val)
        db.commit()

        print('Summoner ', name, ' added with account ID: ', summoner['accountId'])
        return

    for summoner in summoners:
        # db schema for summoner goes in order of account_id, summoner_name, region
        update_games(summoner, watcher, db)


if __name__ == "__main__":
    main()
