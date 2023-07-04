from random import randint
import asyncio
import discord
import database.DBlib as db
from time import time, sleep
import threading
import utils as ut

from .player import Player
from .cards import Card, cards
from .hand import Hand

active_tables = ut.Alist()


# Handling Inactive Tables
def check_tables_activity():
    while True:
        for table in active_tables[:]:
            if table.last_game+(60*10) > time(): # 10 Minutes
                active_tables.remove(table)
        sleep(60) # Checking every one minute
tablechecking_thread = threading.Thread(target=check_tables_activity)
tablechecking_thread.start()



class Table():
    def __init__(self, channel: discord.TextChannel, master: discord.Member | discord.User):
        self.channel = channel
        self.players = ut.Alist([Player(master)])
        
        self.last_game = time()
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


    def allPlayersLost(self):
        return all([(hand.total > 21) for player in self.players for hand in player.hands])


    def allPlayersBlackjacked(self):
        return all([(hand.total == 21) for player in self.players for hand in player.hands])
     
        
    async def add_player(self, player: discord.Member | discord.User):
        if len(self.players) >= 8:
            await ut.error_msg(self.channel, 'The table is full!')
            return
        if not self.ingame:
            self.players.append(Player(player))
        
    
    async def remove_player(self, player: discord.Member | discord.User):
        if len(self.players) >= 8:
            await ut.error_msg(self.channel, 'The table is full!')
            return
        if not self.ingame:
            self.players.remove(player)
    
    
    async def start_game(self, client: discord.Client):
        self.ingame = True
        self.last_game = time()
        self.deck = ut.Alist(cards)
        dealer = Hand(player='Dealer')
        
        
        def check(reaction, user):
                return reaction.emoji in ('🎯', '🛑', '💸', '✂️') and player.profile.id == user.id 
        
                
        # Match
        async for round in ut.Alist(range(1, 3)):
            # Checking if all players blackjacked/lost
            if self.allPlayersLost():
                async for player in self.players:
                    player.result = player.bet*-1
                break
            if self.allPlayersBlackjacked():
                async for player in self.players:
                    player.result = player.bet
                break    
                        
            # Dealer's Turn
            if round == 1:
                dealer.draw_cards(self.deck)
                dealer.hand.append(Card(image='blackjack/cards/back.png', value=None)) # Hidden Card
                await dealer.show_hand(self.channel)
            else:
                # Revealing the hidden card
                dealer.hand.pop()
                dealer.draw_cards(self.deck)
                await dealer.show_hand(self.channel)
                
                while True:
                    await asyncio.sleep(3)
                    
                    if dealer.total <= 16: # Dealer hits
                        await self.channel.send(f'The dealer chose **hit**!')
                        dealer.draw_cards(self.deck)
                        await dealer.show_hand(self.channel)
                        continue
                    
                    if dealer.total == 21: # Dealer got a Blackjack (Game Ends)
                        await self.channel.send(embed=discord.Embed(title=f'**The Dealer got a Blackjack!**',  colour=discord.Colour.dark_purple(),
                                description=f'``Total = 21``'))
                        async for player in self.players:
                            async for hand in player.hands:
                                player.result += 0 if hand.total == 21 else player.bet*-1
                        break
                    
                    if dealer.total > 21: # Dealer lost (Game Ends)
                        await self.channel.send(embed=discord.Embed(title=f'**The Dealer lost!**',  colour=discord.Colour.dark_red(),
                                    description=f'``Total = {dealer.total}``'))
                        async for player in self.players:
                            async for hand in player.hands:
                                player.result += player.bet if hand.total <= 21 else player.bet*-1
                        break
                    
                    # Dealer stops (Game Ends)
                    await self.channel.send(f'The dealer stoped!')
                    async for player in self.players:
                        async for hand in player.hands:
                            if hand.total == dealer.total:
                                break
                            player.result += player.bet if (hand.total > dealer.total and hand.total <= 21) else player.bet*-1
                    break
                
            if round == 2: # Checking if the game is over
                break
                
            # Players' Turn
            async for player in self.players:
                player: Player
                
                # Player's Hands
                hand_num = 0
                while abs(hand_num) != len(player.hands)+1:
                    hand: Hand = player.hands[hand_num]
                    
                    if hand_num == 0: # Main Hand Gets Two Cards
                        await asyncio.sleep(3)
                        hand.draw_cards(self.deck, amount=2)
                    
                    if hand.total == 21: # Player got a Blackjack
                        await self.channel.send(embed=discord.Embed(title=f'**{player.profile.name} got a Blackjack!**',  colour=discord.Colour.dark_purple(),
                                description=f'``Total = 21``'))
                        continue
                    
                    # Specific Hand Action
                    try:
                        while True:
                            await hand.show_turn(self.channel)
                            output = await client.wait_for('reaction_add', timeout=30, check=check)
                            
                            if output[0].emoji == '🎯':
                                await self.channel.send(f'{player.profile.name} chose **hit**!')
                                hand.draw_cards(self.deck)
                            
                            if output[0].emoji == '🛑':
                                await self.channel.send(f'{player.profile.name} chose **stand**!')
                                break
                            
                            if output[0].emoji == '💸' and hand.canDouble():
                                await self.channel.send(f'{player.profile.name} chose **double**!')
                                hand.draw_cards(self.deck)
                                player.bet *= 2
                                await hand.show_hand(self.channel)
                            
                            if output[0].emoji == '✂️':
                                await self.channel.send(f'{player.profile.name} chose **split**!')
                                player.split_hand(hand_to_split=hand)
                                break
                            
                            # Checking if something happened
                            if hand.total == 21: # Player got a Blackjack
                                await self.channel.send(embed=discord.Embed(title=f'**{player.profile.name} got a Blackjack!**',  colour=discord.Colour.dark_purple(),
                                                    description=f'``Total = 21``'))
                                break
                            
                            if hand.total > 21: # Player lost the match
                                await self.channel.send(embed=discord.Embed(title=f'**{player.profile.name} lost!**',  colour=discord.Colour.dark_red(),
                                    description=f'``Total = {hand.total}``'))
                                break
                            
                            if output[0].emoji == '💸': # Ending the turn because the player doubled
                                break
                    except asyncio.TimeoutError:
                        await ut.error_msg(self.channel, f'{player.profile.name} took too long! Skipping his/her turn...')
                    hand_num -= 1
                    
        # Match Summary and "Win Points"
        msg = discord.Embed(title='Match Summary', colour=discord.Colour.gold(), description='')
        async for player in self.players:
            msg.description += f'* **{player.profile.name} ({f"+{player.result}" if player.result > 0 else player.result} WINS)**\n'
            if player.result != 0:
                await db.modifyWins(str(player.profile.id), player.result)
        await self.channel.send(embed=msg)
        
        # Restarting the table for a new match
        await asyncio.sleep(3)
        async for player in self.players:
            player.prepare_player()
        self.ingame = False
        self.deck = None
        await self.show_table()
            
                        
    async def show_table(self):
        msg = discord.Embed(title=f'**Blackjack Table N° {randint(100, 999)}**',  colour=discord.Colour.gold(),
                            description='* ``Blackjack! (Dealer)``\n')
        
        async for player in self.players:
            msg.description += f'* ``{player.profile.name} (Player)``\n'
        msg.set_footer(text='Made By: MestreDosPATUS')
        
        await self.channel.send(embed=msg)
        