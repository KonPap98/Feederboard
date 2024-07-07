import discord
from discord.ext import commands
import sqlite3
from discord import app_commands
import DeathCommands
from discord import ui        
    
class FeederBoard(commands.Cog):
        def __innit__(self, Client):
            self.Client = Client    

        @commands.Cog.listener()
        async def on_ready(self):
            print("FeederBoard Commands ready")

        @app_commands.command(name="feederboard", description="Shows the feeder")
        async def feederboard(self, interaction: discord.Interaction):

            guild_id = interaction.guild_id

            print(guild_id)

            #conenct db and get data
            conn = sqlite3.connect('RiotIDs.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            #create embed
            feeder_embed = discord.Embed(title = "Server Ranking", description = "Shows the server feeders", colour = discord.Colour.dark_purple())
    
            rows = cursor.execute("SELECT NAME, DEATHS FROM DEATH_COUNTER WHERE SERVER_ID = ? Order by Deaths DESC", (str(guild_id),)) 
            #leaderboard index
            leaderboard_place = 1

            #loops rows and adds fields to embed
            for row in rows:
                feeder_embed.add_field(name = f"Rank: {leaderboard_place}", value =f"{row["name"]}", inline=True)
                feeder_embed.add_field(name = "Deaths", value =row["deaths"], inline=True)
                feeder_embed.add_field(name = "", value = "", inline=True)
                leaderboard_place += 1

            feeder_embed.set_footer(text = f"{interaction.user} made this embed")        
            await interaction.response.send_message(embed = feeder_embed)

            conn.commit    
            conn.close

        @app_commands.command(name ="update_deaths")
        async def update_deaths(self, interaction: discord.Interaction):

            conn = sqlite3.connect('RiotIDs.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            user_id_string = str(interaction.user.id)

            server = cursor.execute("SELECT SERVER_ID FROM DEATH_COUNTER WHERE ID = ?", (user_id_string,))
            server_id = server.fetchone()

            server_id_string = str(server_id["SERVER_ID"])

            account_id = cursor.execute("SELECT ID FROM Riot_Accounts WHERE ID = ?", (user_id_string,))
            id = account_id.fetchone()

            if id:
                rows = cursor.execute("SELECT * FROM RIOT_ACCOUNTS WHERE ID = ?", (user_id_string,))
        
                for row in rows:
                    discord_id = row["ID"]
                    username = row["USERNAME"]
                    AccountID = row["ACCOUNT_ID"]
                    region_lowercase = row["REGION"]

                await interaction.response.send_message("Stats Updated", ephemeral=True)
                await DeathCommands.DeathCalc(discord_id=discord_id, username=username, AccountID=AccountID, region_lowercase=region_lowercase, server_id=server_id_string)
            else:
                await interaction.response.send_message("Discord account not linked\n Run 'Register' first.", ephemeral=True)

            conn.commit
            conn.close

          
        @app_commands.command(name="feeder_match")
        async def feeder_match(self, interaction: discord.Interaction):
                
                guid_id = str(interaction.guild_id)
                discord_id = str(interaction.user.id)

                match_embed = discord.Embed(title = "Feeder Match!!!", description = "Compare Feeders", colour = discord.Colour.dark_purple())

                feeder_select = ui.Select(placeholder= "Select feeder")                              
                
                view = ui.View()

                #conenct db and get data
                conn = sqlite3.connect('RiotIDs.db')
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
               
                rows = cursor.execute("SELECT NAME, ID FROM DEATH_COUNTER WHERE SERVER_ID = ? Order by Deaths DESC", (guid_id,))
                
                for row in rows:
                    feeder_select.add_option(label=row["name"], value=row["ID"])

                async def my_callback(interaction: discord.Interaction):
                    stats = cursor.execute("SELECT NAME, DEATHS FROM DEATH_COUNTER WHERE ID = ? OR ID = ?", (discord_id, feeder_select.values[0],))

                    for stat in stats:
                        match_embed.add_field(name = f"Name: {stat["Name"]}", value =f"Deaths: {stat["Deaths"]}", inline=True)

                    match_embed.set_footer(text = f"{interaction.user} made this embed")

                    await interaction.response.send_message(embed=match_embed)    

                feeder_select.callback = my_callback

                view.add_item(feeder_select)
                await interaction.response.send_message("Select a feeder", view=view, ephemeral=True, delete_after=10)

                conn.commit
                conn.close
        

async def setup(Client):
    await Client.add_cog(FeederBoard(Client))              