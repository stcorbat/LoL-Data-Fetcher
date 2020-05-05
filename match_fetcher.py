import time

from riotwatcher import ApiError


def collect_match_data(region, summoner_name, game_id, lol_watcher):
    response = get_match_json(region, game_id, lol_watcher)

    # dictionary to hold all the data values of interest from the MatchDto
    data = {}

    data.update({'duration': response['gameDuration']})

    # rest of the stats are found in the participants section
    participant_id = get_participant_id(response, summoner_name)
    # this shouldn't ever run but a -1 represents that the summoner was not in the match
    if participant_id == -1:
        print(game_id)
        return None

    # riot orders participants in the section 1-10, so can be indexed by subtracting one from the id
    participant_json = response['participants'][participant_id - 1]
    stats = participant_json['stats']

    data.update({
        'champion': participant_json['championId'],
        'win': stats['win'],
        'kills': stats['kills'],
        'deaths': stats['deaths'],
        'assists': stats['assists'],
        'gold_earned': stats['goldEarned'],
        'champion_damage': stats['totalDamageDealtToChampions'],
        'objective_damage': stats['damageDealtToObjectives'],
        'damage_healed': stats['totalHeal'],
        'vision_score': stats['visionScore'],
        'minions_killed': stats['totalMinionsKilled'],
        'neutral_monsters_killed': stats['neutralMinionsKilled'],
        'control_wards_purchased': stats['visionWardsBoughtInGame']
    })

    return data


# parses the participant ID based on the given summoner name
def get_participant_id(match_json, summoner_name):
    participants = match_json['participantIdentities']
    for summoner in participants:
        if summoner['player']['summonerName'] == summoner_name.lower():
            return summoner['participantId']

    return -1


def get_match_json(region, game_id, lol_watcher):
    try:
        return lol_watcher.match.by_id(region, game_id)
    except ApiError as err:
        if err.response.status_code == 429:
            print('We should retry in {} seconds.'.format(err.headers['Retry-After']))
        elif err.response.status_code == 404:
            print('Match not found for game ID: {}'.format(game_id))
        elif err.response.status_code == 504:
            # 504 happens randomly, wait a couple seconds then try again
            time.sleep(2)
            return get_match_json(region, game_id, lol_watcher)
        else:
            raise
