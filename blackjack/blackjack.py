from random import randint, choices, choice
import asyncstdlib as a
import discord
import os.path
from time import time
import utils as ut

active_tables = ut.Alist()
cards = ut.Alist()

class Table():
    def __init__(self, channel: discord.TextChannel, master: discord.Member | discord.User):
        self.channel = channel
        self.players = ut.Alist([Player(master)])
        
        self.created_at = time()
        self.last_game = None
        self.deck = None
        self.ingame = False
        
        
    def __eq__(self, other: object) -> bool:
        if isinstance(other, Table):
            return self.channel == other.channel
        elif isinstance(other, discord.TextChannel):
            return self.channel == other
        elif isinstance(other, (discord.Member, discord.User)):
            return other in self.players
        return self == other

        
    async def add_player(self, player: discord.Member | discord.User):
        if not self.ingame:
            self.players.append(Player(player))
    
        
    async def remove_player(self, player: discord.Member | discord.User):
        if not self.ingame:
            self.players.remove(player)
    
    
    async def start_game(self):
        self.ingame = True
        self.last_game = time()
        self.deck = ut.Alist(cards)
        
        dealer = Hand(player='Dealer')
        dealer.draw_hand(self.deck)
        dealer.show_hand(self.channel)
        '''async for player in self.players:
            player.hand.draw_hand()'''
        
        
    async def show_table(self):
        msg = discord.Embed(title=f'**Blackjack Table N° {randint(100, 999)}**',  colour=discord.Colour.gold(),
                            description='* ``Blackjack! (Dealer)``\n')
        
        async for player in self.players:
            msg.description += f'* ``{player.profile.name} (Player)``\n'
        msg.set_footer(text='Made By: MestreDosPATUS')
        
        await self.channel.send(embed=msg)
        

class Hand():
    def __init__(self, player: discord.Member | discord.User | str):
        self.player = player
        self.hand = ut.Alist()
        self.total = 0
    
    
    async def eval_hand(self):
        aces = 0
        
        async for card in self.hand:
            if card is None:
                continue
            if cards.value == 11:
                aces += 1
            self.total += card.value
            
        async for ace in ut.Alist(range(aces)):
            if self.total <= 21:
                break
            self.total -= 10


    def draw_card(self, deck: ut.Alist | list):
        card = choice(deck)
        self.hand.append(card)
        deck.remove(card)
        self.eval_hand()
        
        
    def draw_hand(self, deck: ut.Alist | list):
        cards = choices(deck, k=2) # TODO: fix
        self.hand.extend(cards)
        for card in cards:
            deck.remove(card)
        self.eval_hand()
        
        
    async def show_hand(self, channel: discord.TextChannel):
        name = self.player if isinstance(self.player, str) else self.player.name
        cards_img = ut.generateCards(self.hand)
        
        msg = discord.Embed(title=f'**{name}\'s Hand**',  colour=discord.Colour.green(),
                            description=f'``Total = {self.total}``')
        msg.set_footer('Made By: MestreDosPATUS')
        
        await channel.send(embed=msg, file=cards_img.tobytes())


class Card():
    def __init__(self, image: str, value: str | int):
        self.image = image
        self.value = value
        
        
class Player():
    def __init__(self, profile: discord.Member | discord.User):
        self.profile = profile
        self.hand = Hand(player=profile)
    
    
    def __eq__(self, other:object) -> bool:
        if isinstance(other, Player):
            return self.profile.id == other.profile.id
        elif isinstance(other, (discord.User, discord.Member)):
            return self.profile == other
        elif isinstance(other, int):
            return self.profile.id == other
        return self == other    
            
            
# Generating a list with the cards
for rep in os.listdir('blackjack/cards'):
    if not os.path.isdir(rep):
        continue
    for card in os.listdir(f'blackjack/cards/{rep}'):
        if card.endswith('.png'):

            if card.split('_')[0].upper() in ['JACK', 'KING', 'QUEEN']:
                value = 10
            elif card.split('_')[0].upper() == 'ACE':
                value = 11
            else:
                value = int(card.split('_')[0])

            cards.append(Card(image=os.path.abspath(f'blackjack/cards/{rep}/{card}'), value=value))
