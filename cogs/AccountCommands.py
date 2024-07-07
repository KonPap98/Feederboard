import discord
from discord.ext import commands
from discord import ui
import Register_Unlink
from discord import app_commands

class Register_User(commands.Cog):
        def __innit__(self, Client):
            self.Client = Client    

        @commands.Cog.listener()
        async def on_ready(self):
            print("Account Commands ready")
            
           
        @app_commands.command()
        async def register(self, interaction: discord.Interaction):
                
                #Create modal
                class RegisterModal(ui.Modal, title = "Register form"):
                    riot_id = ui.TextInput(label="Username", placeholder="Insert your Username...", style=discord.TextStyle.short)
                    hashtag = ui.TextInput(label="Tag", placeholder="Insert your Tag...", style=discord.TextStyle.short)
                    region = ui.TextInput(label = "Region", placeholder="Insert your region(Europe,Americas,Asia)", style=discord.TextStyle.short)

                    #runs when they click submit
                    async def on_submit(self, interaction: discord.Interaction):    
                          
                        discord_id = interaction.user.id
                        username = self.riot_id
                        tag = self.hashtag
                        region = str(self.region)
                        
                        #checks if region is valid
                        if region.lower() != "europe" and region.lower() != "asia" and region.lower() != "americas":
                            await interaction.response.send_message("Ivalid region", ephemeral=True)
                            return 0     
                        else:
                            await interaction.response.send_message("Loading your stats...", ephemeral=True)
                            await Register_Unlink.trigger_register(interaction=interaction, discord_id=discord_id, username=username, tag=tag, region=region)
                              

                await interaction.response.send_modal(RegisterModal())
            
        @app_commands.command()
        async def unlink(self, interaction: discord.Interaction):
            
            discord_id = interaction.user.id
            await interaction.response.send_message(":saluting_face: You will be missed :saluting_face:")
            await Register_Unlink.trigger_unlink(discord_id)
            
            
async def setup(Client):
    await Client.add_cog(Register_User(Client))