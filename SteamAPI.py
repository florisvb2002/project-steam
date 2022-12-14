import requests

from collections import Counter

steamid = input('Voer uw SteamID in: ')


def display_naam(steamid):
    apikey = f'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=F443712EFA1E4CDA7FFF50E2A251C972&steamids={steamid}'
    name = requests.get(apikey).json()['response']['players']
    for data in name:
        gamename = data['personaname']

    return gamename


print(f'Welkom {display_naam(steamid)}, hierbij een overzicht: ')


def vrienden(steamid: str):
    apikey = f'http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key=F443712EFA1E4CDA7FFF50E2A251C972&steamid={steamid}&format=json'
    friendlist = requests.get(apikey).json()['friendslist']['friends']

    vrienden_ID = []
    for friend in friendlist:
        steamid = friend['steamid']
        vrienden_ID.append(steamid)
    return vrienden_ID


def online_status(steamid: str):
    api_online = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key=A032CA9A0E764870A78DC2E2FCC1412F&format=json&steamids={steamid}"
    online_response = requests.get(api_online)
    onl = online_response.json()
    online = onl['response']['players'][0]['personastate']

    return online


def aantal_vrienden_online(steamid: str):
    aantal = 0
    aantal_online = 0

    # First we need to fetch the users in the friendlist
    friends = f"http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key=A032CA9A0E764870A78DC2E2FCC1412F&steamid={steamid}&relationship=friend"
    friends_response = requests.get(friends)
    data = friends_response.json()

    # Now we can make an array with the steamids of the friends
    friendids = list(map(lambda x: x['steamid'], data['friendslist']['friends']))

    # Finally we can loop through the ids and check if they're online
    for friend in friendids:
        if online_status(friend) > 0:
            aantal_online += 1

    return aantal_online


def findGame(appid):
    res = requests.get(f'https://api.steampowered.com/ISteamApps/GetAppList/v2/').json()
    for app in res['applist']['apps']:
        if app['appid'] == int(appid):
            return app['name']


def vrienden_gespeeld():
    playtime_forever = {}
    for vriend in vrienden(steamid):
        apikey = f'http://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/?key=F443712EFA1E4CDA7FFF50E2A251C972&steamid={vriend}&format=json'
        response = requests.get(apikey).json()['response']

        apikey1 = f'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=F443712EFA1E4CDA7FFF50E2A251C972&steamid=76561198164973706&format=json'
        aantal_games = requests.get(apikey1).json()['response']['game_count']

        # response.keys = ['game_count', 'games']
        # OF response.keys = [] :(
        if ('games' in response.keys()):
            for game in response['games']:
                # check of we informatie hebben voor deze speler
                id = game['appid']
                minuten = game['playtime_2weeks']

                if id in playtime_forever:
                    playtime_forever[id] += minuten

                else:
                    # Hoe vaak staat het getal al in de lijst tot nu?
                    playtime_forever[id] = minuten

    volgorde = dict(sorted(playtime_forever.items(), key=lambda x: x[1]))
    high = Counter(volgorde)

    top_games = high.most_common(aantal_games)
    top__games = {}
    for game in top_games:
        index = game[0]
        index1 = round(game[1] / 60, 1)
        naamgame = findGame(index)
        top__games[naamgame] = index1
    return top__games


def top_5_games():
    topgames = vrienden_gespeeld()
    top_5_games = list(topgames.items())[:5]
    dict_1 = dict(top_5_games)
    return dict_1


def aanbevolen_games():
    apikey = f'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=F443712EFA1E4CDA7FFF50E2A251C972&steamid={steamid}&format=json'
    response = requests.get(apikey).json()['response']['games']

    aanbevolen = vrienden_gespeeld()

    for games in response:
        appid = games['appid']
        gamenaam = findGame(appid)
        if gamenaam in aanbevolen:
            del aanbevolen[gamenaam]
            aanbevolen1 = list(aanbevolen.items())[:5]
            aanbevolen_5 = dict(aanbevolen1)
            keys = list(aanbevolen_5.keys())
    return keys


'''

Menu voor keuze wat te zien

'''

print('Optie 1: Hoeveel vrienden zijn er online.')
print('Optie 2: Wat zijn de top 5 meest gespeelde spellen van je vrienden.')
print('Optie 3: Aanbevolen games.')
input = int(input('Kies 1 van de 3 opties die hierboven worden weergegeven: '))

if input == 1:
    print(aantal_vrienden_online(steamid))
elif input == 2:
    print(top_5_games())
elif input == 3:
    print(aanbevolen_games())