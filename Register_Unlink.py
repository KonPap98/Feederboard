import discord
from discord.ext import commands
import sqlite3
import requests
import DeathCommands
import os

ApiKey = (os.getenv("RiotApiKey"))

async def trigger_register(interaction: discord.Interaction, discord_id, username, tag, region):

    server_id = interaction.guild_id

    #connect db
    conn = sqlite3.connect('RiotIDs.db')
    cursor = conn.cursor()
    
    #get id from DB
    cursor.execute('SELECT ID FROM Riot_Accounts WHERE id = ?', (discord_id,))
    user = cursor.fetchone()
    
    region_str = str(region)
    region_lowercase = region_str.lower()

    #Calls API to get account ID
    ApiUrlAccount = "https://" + region_lowercase + ".api.riotgames.com/riot/account/v1/accounts/by-riot-id/" + str(username) + "/" + str(tag) + "?api_key=" + str(ApiKey)
    ApiAccountResponse = requests.get(ApiUrlAccount)
    
    #checks if api got proper response
    if (ApiAccountResponse.ok):
        AccountInfo = ApiAccountResponse.json()
        AccountID = AccountInfo["puuid"]
    else:
        await interaction.followup.send(content="Invalid username/tag combination.", ephemeral=True)
        return 0
    
    #if user exists update table else create entry 
    if user == None:
        cursor.execute('''
            INSERT INTO Riot_Accounts
                VALUES (?, ?, ?, ?, ?)
            ''',(str(discord_id), str(username), str(tag), str(AccountID), region_lowercase,))
        
    else:
        cursor.execute('''UPDATE Riot_Accounts
                       SET ACCOUNT_ID = ?
                       WHERE ID = ?
                       ''',(str(AccountID), discord_id,))

    conn.commit()
    conn.close() 

    await interaction.followup.send(f"Linked Riot ID {username}#{tag} to your account", ephemeral=True) 
    
    await DeathCommands.DeathCalc(discord_id=discord_id, username=username, AccountID=AccountID, region_lowercase=region_lowercase, server_id=server_id)


async def trigger_unlink(discord_id):
        
        #connect db
        conn = sqlite3.connect('RiotIDs.db')
        cursor = conn.cursor()

        cursor.execute("DELETE FROM Riot_Accounts where ID = ?", (discord_id,))
        cursor.execute("DELETE FROM Death_Counter where ID = ?", (discord_id,))

        conn.commit()
        conn.close()