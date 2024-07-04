import discord
from discord.ext import commands
import sqlite3
import requests
import os

ApiKey = (os.getenv("RiotApiKey"))

async def DeathCalc(discord_id, username, AccountID, region_lowercase, server_id):

    #get account id for API call
    AccountIDString = str(AccountID)

    HistoryUrl = "https://" + region_lowercase + ".api.riotgames.com/lol/match/v5/matches/by-puuid/" + AccountIDString + "/ids?start=0&count=20&api_key=" + ApiKey
    response = requests.get(HistoryUrl)
    History = response.json()

    #must be declared outside(use x += y NOT x = x + y)
    final_deaths = 0

    #Loop thorugh matches
    for match in History:
        MatchUrl = "https://europe.api.riotgames.com/lol/match/v5/matches/" + match + "?api_key=" + ApiKey
        response = requests.get(MatchUrl)
        match_data = response.json()
        player_index = match_data['metadata']['participants'].index(AccountID)
        matchDeaths = match_data['info']['participants'][player_index]['deaths']
        final_deaths += matchDeaths


    await UpdateDeathTable(discord_id, final_deaths, username, server_id)
    
async def UpdateDeathTable(discord_id, final_deaths, username, server_id):

        #connect to DB
        conn = sqlite3.connect('RiotIDs.db')
        cursor = conn.cursor()

        #select id and check if user is registered
        cursor.execute ("SELECT ID FROM Death_Counter WHERE ID = ?", (discord_id,))
        id = cursor.fetchone()

        #if user exists update table else create entry
        if id:
            cursor.execute(''' UPDATE Death_Counter 
                        SET DEATHS = ?
                        WHERE ID = ?''',
                        (str(final_deaths), str(id)))  
        else:
            cursor.execute(''' INSERT INTO Death_Counter 
                        (ID, NAME, DEATHS, SERVER_ID)
                        VALUES (?, ?, ?, ?)''',
                        (str(discord_id), str(username), str(final_deaths), str(server_id)))    
            
        conn.commit()
        conn.close()