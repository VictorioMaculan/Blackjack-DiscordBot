from random import randint
import discord

active_tables = list()

class Table():
    def __init__(self, channel: discord.TextChannel, master: discord.User):
        self.id = randint(100, 999)
        self.channel = channel
        
        self.players = [master]
        self.ingame = False
    
    
    def __eq__(self, other):
        return self.channel == other.channel
    
        
    def add_player(self, player):
        if not self.ingame:
            self.players.append(player)
    
        
    def remove_player(self, player):
        if not self.ingame:
            self.players.remove(player)
    
    
    def start_game(self):
        self.ingame = True
    
        
    async def show_table(self):
        msg = discord.Embed(title=f'**Blackjack Table N° {self.id}**',  colour=discord.Colour.gold(),
                            description='* Blackjack! (Dealer)\n')
        
        for player in self.players:
            msg.description += f'* {player.name} (Player)\n'
        msg.set_footer(text='Made By: MestreDosPATUS')
        
        await self.channel.send(embed=msg)
        