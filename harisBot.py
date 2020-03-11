import discord
import requests
import cassiopeia
import json
import spotipy
import re
import datetime
import arrow
from apikeys import *

client = discord.Client()
auth = spotipy.oauth2.SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
spotify = spotipy.Spotify(client_credentials_manager=auth)
location = "https://na1.api.riotgames.com/" #change this for other regions
cassiopeia.set_riot_api_key(RIOT_APIKEY)
cassiopeia.set_default_region("NA")
champs = cassiopeia.get_champions()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('~help'):
        embed = discord.Embed(title="BOT Haris Commands")
        embed.add_field(name="~lol skills CHAMPION_NAME", value="Shows the skills and cooldowns of a given champion")
        embed.add_field(name="~lol level SUMMONER_NAME", value="Shows a summoners icon, level and rank")
        embed.add_field(name="~lol mastery SUMMONER_NAME", value="Shows all mastery 7 champions")
        embed.add_field(name="~lol nicelife SUMMONER_NAME", value="Shows how much league of legends was played in the last 24h")
        embed.add_field(name="~lol livegame SUMMONER_NAME", value="LOL XD")
        embed.add_field(name="~react WORD", value="Attempts to add the word as a reaction to the above message")
        embed.add_field(name="~spotify SEARCH_QUERY", value="Searches spotify for a song")
        await message.channel.send(embed=embed)
    elif message.content.startswith('~lol'):
        xs = message.content.split(' ')
        if len(xs) < 2:
            await message.channel.send('Improper syntax!')
        if (xs[1] == "level"):
            summoner = cassiopeia.get_summoner(name=' '.join(xs[2:]))
            name = cassiopeia.get_summoner(account_id=summoner.account_id).name
            opgg = f'https://na.op.gg/summoner/userName={name.replace(" ", "%20")}'
            icon = summoner.profile_icon.url
            rsf = cassiopeia.Queue.ranked_solo_fives
            clrD = {'iron' : discord.Colour.from_rgb(88, 92, 80),
                   'bronze' : discord.Colour.from_rgb(139,69,19),
                   'silver' : discord.Colour.from_rgb(255,255,255),
                   'gold' : discord.Colour.gold(),
                   'platinum' : discord.Color.from_rgb(0, 163, 204),
                   'diamond' : discord.Color.from_rgb(153, 235, 255),
                   'master' : discord.Color.red(),
                   'grandmaster' : discord.Color.dark_red(),
                   'challenger' : discord.Color.from_rgb(0,0,0)}
            rank = str(summoner.ranks[rsf].tier) + " " + str(summoner.ranks[rsf].division) if rsf in summoner.ranks else 'Unranked'
            clr = clrD[summoner.ranks[rsf].tier.name] if rank != 'Unranked' else discord.Color.blurple()
            embedded = discord.Embed(title=rank,
            description=f'Level {summoner.level}', color=clr)
            embedded.set_author(name=name,url=opgg)
            embedded.set_thumbnail(url=icon)
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
        elif (xs[1] == "skills"):
            found = False
            for chmp in champs:
                if chmp.name.lower() == ' '.join([str(x) for x in xs[2:]]).lower():
                    champ = chmp
                    found = True
                    break
            if not found:
                await message.channel.send("Couldn't find a champion with that name")
            else:
                embedded = discord.Embed(title=champ.name,
                description=champ.title, color=discord.Colour.red())
                embedded.set_thumbnail(url=champ.image.url)
                for skill in champ.spells:
                    s = "\n\nCooldowns: "+("/").join([str(x) for x in skill.cooldowns])
                    fixedText = re.sub(r'<br>','\n', skill.description)
                    fixedText = re.sub(r'<.*?>','', skill.description)
                    embedded.add_field(name=f'{skill.keyboard_key.name}: {skill.name}',value=f'{fixedText} {s}')
                embedded.add_field(name='Passive: '+champ.passive.name,value=re.sub(r'<.*?>','',champ.passive.description))
                await message.channel.send(embed=embedded)
        elif (xs[1] == "nicelife"):
            summoner = cassiopeia.get_summoner(name=' '.join(xs[2:]))
            name = cassiopeia.get_summoner(account_id=summoner.account_id).name
            time = datetime.timedelta()
            rn = arrow.Arrow.utcnow()
            for match in summoner.match_history(begin_time=rn.shift(days=-1), end_time=rn):
                time += match.duration
                print(match.duration)
            secs = time.total_seconds()
            print(secs)
            secs, mins = secs%60, secs//60
            mins, hours = mins%60, mins//60
            await message.channel.send(f'{name} did work for {int(hours)} hours, {int(mins)} minutes and {int(secs)} seconds yesterday')
        elif (xs[1] == "mmr"):
            summoner = cassiopeia.get_summoner(name=' '.join(xs[2:]))
            total, count = 0, 45
            mapper = {'IRON': 0, 'BRONZE': 4,
                      'SILVER' : 8, 'GOLD' : 12,
                      'PLATINUM' : 16, 'DIAMOND' : 20,
                      'MASTER' : 24, 'GRANDMASTER' : 28,
                      'CHALLENGER': 32, 'IV' : 0, 'III':1,'II':2,'I':3}
            for match in summoner.match_history(seasons=[cassiopeia.Season.season_9],queues=[cassiopeia.Queue.ranked_solo_fives],begin_index=0,end_index=5):
                for p in match.participants:
                    rsf = cassiopeia.Queue.ranked_solo_fives
                    psr = p.summoner.ranks
                    if rsf in psr:
                        total += mapper[psr[rsf].tier.value] + mapper[psr[rsf].division.value]
                    else:
                        count-=1
            name = cassiopeia.get_summoner(account_id=summoner.account_id).name
            other = ['Iron', 'Bronze', 'Silver', 'Gold', 'Platinum', 'Diamond', 'Master', 'Grandmaster', 'Challenger']
            other2 = ['IV','III','II','I']
            print(total, count)
            rank = other[round(total/count)//4] + " " + other2[round(total/count)%4] 
            await message.channel.send(f'{name} played in an average of {rank} in their past 5 games')
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
            for c in xs[1]:
                await msg[1].add_reaction(eDict[c])
    

    elif message.content.startswith('~spotify'):
        xs = message.content
        results = (spotify.search(q=xs[9:], limit=1, type="track"))
        for idx, track in enumerate(results['tracks']['items']):
            await message.channel.send(track['external_urls']['spotify'])
    

    elif message.content.startswith('~w2g'):
        await message.channel.send("https://www.watch2gether.com/rooms/4gsijtdvlmrererx8b?lang=en")
    if message.content.endswith('-d'):
        await message.delete()

client.run(TOKEN)