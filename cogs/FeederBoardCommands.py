import discord
from discord.ext import commands
import sqlite3
from discord import app_commands
import DeathCommands

class FeederBoard(commands.Cog):
        def __innit__(self, Client):
            self.Client = Client    

        @commands.Cog.listener()
        async def on_ready(self):
            print("FeederBoard Commands ready")

        @app_commands.command(name="feederboard", description="Shows the feeder")
        async def feederboard(self, interaction: discord.Interaction):

            guild_id = interaction.guild.id
            
            #create embed
            embed = discord.Embed(title = "Server Ranking", description = "Shows the server feeders", colour = discord.Colour.dark_purple())
             
            #conenct db and get data
            conn = sqlite3.connect('RiotIDs.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            rows = cursor.execute("SELECT NAME, DEATHS FROM DEATH_COUNTER WHERE SERVER_ID = ? Order by Deaths DESC", (guild_id,)) 
            
            #leaderboard index
            leaderboard_place = 1

            #loops rows and adds fields to embed
            for row in rows:
                embed.add_field(name = f"Rank: {leaderboard_place}", value =f"{row["name"]}", inline=True)
                embed.add_field(name = "Deaths", value =row["deaths"], inline=True)
                embed.add_field(name = "", value = "", inline=True)
                leaderboard_place += 1
                    
            embed.set_footer(text = f"{interaction.user} made this embed")        
            await interaction.response.send_message(embed = embed)
                 
            conn.close

        @app_commands.command(name = "update_deaths")
        async def update_deaths(self, interaction: discord.Interaction):

            user_id_string = str(interaction.user.id)
            server_id = interaction.guild_id

            #conenct db and get data
            conn = sqlite3.connect('RiotIDs.db')
            cursor = conn.cursor()
            cursor.execute("SELECT ID FROM Riot_Accounts WHERE ID = ?", (user_id_string,))
            id = cursor.fetchone()

            #checks if user exists else error
            if id:
                rows = cursor.execute("SELECT * FROM RIOT_ACCOUNTS WHERE ID = ?", (user_id_string,))
                print(rows)
                discord_id = rows["ID"]
                print(discord_id)
                username = rows["USERNAME"]
                print(username)
                AccountID = rows["ACCOUNT_ID"]
                print(AccountID)
                region_lowercase = rows["REGION"]
                print(region_lowercase)

                await DeathCommands.DeathCalc(discord_id=discord_id, username=username, AccountID=AccountID, region_lowercase=region_lowercase, server_id=server_id)
                await interaction.response.send_message("Stats Updated", ephemeral=True)
            else:
                await interaction.response.send_message("Discord account not linked\n Run 'Register' first.", ephemeral=True)   

            conn.commit
            conn.close  

async def setup(Client):
    await Client.add_cog(FeederBoard(Client))              