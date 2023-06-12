from random import randint, choices
import asyncstdlib as a
import discord
import os.path
import utils as ut

active_tables = ut.Alist()
cards = ut.Alist()


class Table():
    def __init__(self, channel: discord.TextChannel, master: discord.Member):
        self.id = randint(100, 999)
        self.channel = channel
        
        self.players = ut.Alist([master])
        self.hand = None
        
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
        

class Hand():
    def __init__(self):
        self.hand = ut.Alist([Card('', 'Ace'), Card('', 'Ace')])
        self.total = 0
    
    
    async def eval_hand(self):
        aces = 0
        async for card in self.hand:
            if card.value == 'Ace':
                aces += 1
                self.total += 11
                continue
            self.total += card.value
        async for ace in ut.Alist(range(aces)):
            if self.total <= 21:
                break
            self.total -= 10

        
class Card():
    def __init__(self, image, value):
        self.image = image
        self.value = value
                
                
for rep in os.listdir('blackjack/cards'):
    for card in os.listdir(f'blackjack/cards/{rep}'):
        if card.endswith('.png'):
            value = card.split('_')[0]
            if value in ['Jack', 'King', 'Queen']:
                value = 10
            elif value != 'Ace':
                value = int(value)
            cards.append(Card(image=card, value=value))
