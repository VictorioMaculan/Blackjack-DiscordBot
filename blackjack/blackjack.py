from random import randint
import utils as ut
import discord

active_tables = ut.Alist()


class Table():
    def __init__(self, channel: discord.TextChannel, master: discord.Member):
        self.id = randint(100, 999)
        self.channel = channel
        
        self.players = ut.Alist([master])
        self.ingame = False
        
        
    async def add_player(self, player):
        if not self.ingame:
            await self.players.append(player)
    
        
    async def remove_player(self, player):
        if not self.ingame:
            await self.players.remove(player)
    
    
    def start_game(self):
        self.ingame = True
    
        
    async def show_table(self):
        msg = discord.Embed(title=f'**Blackjack Table N° {self.id}**',  colour=discord.Colour.gold(),
                            description='* ``Blackjack! (Dealer)``\n')
        
        async for player in self.players:
            msg.description += f'* ``{player.name} (Player)``\n'
        msg.set_footer(text='Made By: MestreDosPATUS')
        
        await self.channel.send(embed=msg)
        