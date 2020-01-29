import discord
import requests
import cassiopeia
import json
import spotipy
from apikeys import *

client = discord.Client()
auth = spotipy.oauth2.SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
spotify = spotipy.Spotify(client_credentials_manager=auth)
location = "https://na1.api.riotgames.com/" #change this for other regions
cassiopeia.set_riot_api_key(RIOT_APIKEY)
cassiopeia.set_default_region("NA")


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('~hello'):
        await message.channel.send('Hello!')
    elif message.content.startswith('~lol'):
        xs = message.content.split(' ')
        if len(xs) < 2:
            await message.channel.send('Improper syntax!')
        if (xs[1] == "level"):
            summoner = cassiopeia.get_summoner(name=' '.join(xs[2:]))
            name = cassiopeia.get_summoner(account_id=summoner.account_id).name
            opgg = "https://na.op.gg/summoner/userName="
            icon = summoner.profile_icon.url
            rsf = cassiopeia.Queue.ranked_solo_fives
            rank = (str(summoner.ranks[rsf].tier) + " " + str(summoner.ranks[rsf].division)) if rsf in summoner.ranks else 'Unranked'
            embedded = discord.Embed(title=rank,
            description=f'Level {summoner.level}', color=discord.Colour.blue())
            embedded.set_author(name=name)
            embedded.set_image(url=icon)
            await message.channel.send(embed=embedded)
        
        elif (xs[1] == "mastery"):
            summoner = cassiopeia.get_summoner(name=' '.join(xs[2:]))
            name = cassiopeia.get_summoner(account_id=summoner.account_id).name
            level7 = summoner.champion_masteries.filter(lambda x: x.level == 7)
            level7 = [m.champion.name for m in level7]
            s = ""
            for i in range(len(level7)):
                s += level7[i]
                if i == len(level7) - 2:
                    s+= " and "
                elif i < len(level7) - 2:
                    s+= ", "
            await message.channel.send(name + " is Mastery 7 on: " + s)
    
    
    elif message.content.startswith('~react'):
        emojis = client.emojis
        eDict = {'A' : '🇦', 'B' : '🇧', 'C' : '🇨', 'D' : '🇩', 'E' : '🇪', 
        'F' : '🇫', 'G' : '🇬', 'H' : '🇭', 'I' : '🇮', 'J' : '🇯', 'K' : '🇰', 
        'L' : '🇱', 'M' : '🇲', 'N' : '🇳', 'O' : '🇴', 'P' : '🇵', 'Q' : '🇶', 
        'R' : '🇷', 'S' : '🇸', 'T' : '🇹', 'U' : '🇺', 'V' : '🇻', 'W' : '🇼',
        'x' : '🇽', 'Y' : '🇾', 'Z' : '🇿'}
        xs =  message.content.upper().split(' ')
        if len(xs) != 2:
            await message.channel.send('Improper syntax!')
        else:
            msg = await message.channel.history(limit=2).flatten()
            #await delete(xs[1])
            for c in xs[1]:
                await msg[1].add_reaction(eDict[c])
    
    
    elif message.content.startswith('~spotify'):
        xs = message.content
        results = (spotify.search(q=xs[9:], limit=1, type="track"))
        for idx, track in enumerate(results['tracks']['items']):
            await message.channel.send(track['external_urls']['spotify'])
    
    
    elif message.content.startswith('~w2g'):
        await message.channel.send("https://www.watch2gether.com/rooms/4gsijtdvlmrererx8b?lang=en")


client.run(TOKEN)