import discord
import requests
import cassiopeia
import json
TOKEN = 'NjI5MDI4OTM3MTU0MDM1NzI1.XZT3yg.t1-E53ZYdOq6IpGiKO2S_LUXuy8'

client = discord.Client()

location = "https://na1.api.riotgames.com/" #change this for other regions
apk = "?api_key=RGAPI-c210fd93-8d11-4311-93ea-30ec0b9e5e43" #put your api key here

cassiopeia.set_riot_api_key("RGAPI-c210fd93-8d11-4311-93ea-30ec0b9e5e43")  # This overrides the value set in your configuration/settings.
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
            summoner = cassiopeia.get_summoner(name=xs[2])
            await message.channel.send(summoner.name + " is level " + str(summoner.level))
        elif (xs[1] == "mastery"):
            summoner = cassiopeia.get_summoner(name=xs[2])
            level7 = summoner.champion_masteries.filter(lambda x: x.level == 7)
            level7 = [m.champion.name for m in level7]
            s = ""
            for i in range(len(level7)):
                s += level7[i]
                if i == len(level7) - 2:
                    s+= " and "
                elif i < len(level7) - 2:
                    s+= ", "
            await message.channel.send(summoner.name + " is Mastery 7 on: " + s)
client.run(TOKEN)