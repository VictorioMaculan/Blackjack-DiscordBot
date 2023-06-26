from random import randint, choices, shuffle
import asyncstdlib as a
import asyncio
import discord
import os.path
import database.DBlib as db
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
    
    
    async def start_game(self, client: discord.Client): # TODO: Concertar e Melhorar e Olhar esse Client
        self.ingame = True
        self.last_game = time()
        self.deck = ut.Alist(cards)
        dealer = Hand(player='Dealer')
        
        
        def check(reaction, user):
                return reaction.emoji in ('🎯', '🛑', '💸', '✂️') and player.profile.id == user.id 
        
                
        # Match
        async for round in ut.Alist(range(1, 3)):
            # Checking if all players lost/blackjacked already
            if all([(hand.total > 21 or hand.total == 21) for player in self.players for hand in player.hands]):
                for player in self.players:
                    player.result = player.bet*-1
                break
                        
            # Dealer's Turn
            if round == 1:
                await dealer.draw_cards(self.deck)
                dealer.hand.append(Card(image='blackjack/cards/back.png', value=None)) # Hidden Card
                await dealer.show_hand(self.channel)
            else:
                dealer.hand.pop()
                await dealer.draw_cards(self.deck) # Revealing the hidden card
                await dealer.show_hand(self.channel)
                
                while True:
                    await asyncio.sleep(3)
                    
                    if dealer.total <= 16: # Dealer hits
                        await self.channel.send(f'The dealer chose **hit**!')
                        await dealer.draw_cards(self.deck)
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
                            player.result += player.bet if hand.total > dealer.total else player.bet*-1
                    break
                
            if round == 2: # Checking if the game is over
                break
                
            # Players' Turn
            async for player in self.players:
                player: Player
                
                # Player's Hands
                async for hand_num, hand in a.enumerate(reversed(player.hands)): # TODO: Concertar isso.
                    hand: Hand
                    
                    if hand_num == 0: # First Hand Gets Two Cards
                        await asyncio.sleep(3)
                        await hand.draw_cards(self.deck, amount=2)
                    
                    if hand.total == 21: # Player got a Blackjack
                        await self.channel.send(embed=discord.Embed(title=f'**{player.profile.name} got a Blackjack!**',  colour=discord.Colour.dark_purple(),
                                description=f'``Total = 21``'))
                        continue
                    
                    # Specific Hand Action
                    try:
                        while True:
                            await self.channel.send(f'Hand{hand_num}')
                            await hand.show_turn(self.channel)
                            output = await client.wait_for('reaction_add', timeout=30, check=check)
                            
                            if output[0].emoji == '🎯':
                                await self.channel.send(f'{player.profile.name} chose **hit**!')
                                await hand.draw_cards(self.deck)
                            
                            if output[0].emoji == '🛑':
                                await self.channel.send(f'{player.profile.name} chose **stand**!')
                                break
                            
                            if output[0].emoji == '💸' and hand.canDouble(): # TODO: Fix
                                await self.channel.send(f'{player.profile.name} chose **double**!')
                                await hand.draw_cards(self.deck)
                                player.bet *= 2
                                await hand.show_hand(self.channel)
                            
                            if output[0].emoji == '✂️': #and hand.canSplit():
                                await self.channel.send(f'{player.profile.name} chose **split**!')
                                await player.split_hand(hand_to_split=hand)
                                for h in player.hands:
                                    print(h)
                                    for c in h.hand:
                                        print(c)
                                break
                            
                            if hand.total == 21: # Player got a Blackjack
                                await self.channel.send(embed=discord.Embed(title=f'**{player.profile.name} got a Blackjack!**',  colour=discord.Colour.dark_purple(),
                                                    description=f'``Total = 21``'))
                                break
                            
                            if hand.total > 21: # Player lost the match
                                await self.channel.send(embed=discord.Embed(title=f'**{player.profile.name} lost!**',  colour=discord.Colour.dark_red(),
                                    description=f'``Total = {hand.total}``'))
                                break
                    except asyncio.TimeoutError:
                        await ut.error_msg(self.channel, f'{player.profile.name} took too long! Skipping his/her turn...')
            
        # Match Summary and "Win Points"
        msg = discord.Embed(title='Match Summary', colour=discord.Colour.gold(), description='')
        async for player in self.players:
            msg.description += f'* **{player.profile.name} ({f"+{player.result}" if player.result > 0 else player.result})**'
            if player.result != 0:
                await db.modifyWins(str(player.profile.id), player.result)
        await self.channel.send(embed=msg)
        
        # Restarting the table for a new match
        await asyncio.sleep(3)
        async for player in self.players: # TODO: Simplify
            player.restartHands()
            player.bet = 1 # Initial Betting 
            player.result = 0
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
        

class Hand():
    def __init__(self, player: discord.Member | discord.User | str):
        self.player = player
        self.hand = ut.Alist()
        self.total = 0
    
    
    async def eval_hand(self): # TODO: Tirar de async e melhorar
        aces = 0
        self.total = 0
        
        async for card in self.hand:
            if card.value is None:
                continue
            if card.value == 11:
                aces += 1
            self.total += card.value
            
        async for ace in ut.Alist(range(aces)):
            if self.total <= 21:
                break
            self.total -= 10 


    def canDouble(self):
        return len(self.hand) == 2
    
    
    def canSplit(self):
        return len(self.hand) == 2 and self.hand[0].value == self.hand[1].value
        
        
    async def draw_cards(self, deck: list, amount=1): # TODO: Take a better look here
        cards = choices(deck, k=amount)
        self.hand.extend(cards)
        for card in cards:
            deck.remove(card)
        await self.eval_hand()
        print(cards) # Remove this later
        
        
    async def show_hand(self, channel: discord.TextChannel):
        name = self.player if isinstance(self.player, str) else self.player.name
        cards_img = ut.generateCards(self.hand)
        
        msg = discord.Embed(title=f'**{name}\'s Hand:**',  colour=discord.Colour.dark_green(),
                            description=f'``Total = {self.total}``')
        msg.set_footer(text='Made By: MestreDosPATUS')
        
        await channel.send(embed=msg)
        await channel.send(file=ut.pil2discord(cards_img))


    async def show_turn(self, channel:discord.TextChannel):
        name = self.player if isinstance(self.player, str) else self.player.name
        cards_img = ut.generateCards(self.hand)
        msg = discord.Embed(title=f'**{name}\'s Hand:**',  colour=discord.Colour.dark_green(),
                            description=f'''``Total = {self.total}``
                            
                                            **Your options:**
                                            🎯 -> Hit
                                            🛑 -> Stand''')
            
        if self.canDouble():
            msg.description += '\n 💸 -> Double Down'
        if self.canSplit():
            msg.description += '\n ✂️ -> Split'
        msg.set_footer(text='You have 30 seconds to choose what to do!')

        menu = await channel.send(embed=msg)
        await channel.send(file=ut.pil2discord(cards_img))
        
        await menu.add_reaction('🎯')
        await menu.add_reaction('🛑')
        if self.canDouble():
            await menu.add_reaction('💸')
        if self.canSplit():
            await menu.add_reaction('✂️')
        

class Card():
    def __init__(self, image: str, value: str | int):
        self.image = image
        self.value = value
        
    def __str__(self) -> str:
        return str(self.value)
        
class Player():
    def __init__(self, profile: discord.Member | discord.User):
        self.profile = profile
        self.hands = ut.Alist([Hand(player=profile)])
        
        self.bet = 1 # Initial Betting
        self.result = 0 # The amount of points you won/lost in the match
    
    def __eq__(self, other:object) -> bool:
        if isinstance(other, Player):
            return self.profile.id == other.profile.id
        elif isinstance(other, (discord.User, discord.Member)):
            return self.profile == other
        elif isinstance(other, int):
            return self.profile.id == other
        return self == other    
    
    
    async def split_hand(self, hand_to_split: Hand):
        hand1 = Hand(player=self.profile)
        hand2 = Hand(player=self.profile)
        
        hand1.hand.append(hand_to_split.hand[0])
        hand2.hand.append(hand_to_split.hand[1])
        await hand1.eval_hand()
        await hand2.eval_hand()
        
        self.hands.extend([hand1, hand2])
        # TODO: Ver melhor maneira e acabar
    
    def newHand(self):
        self.hands.append(Hand(player=self.profile))
            
            
    def restartHands(self):
        self.hands.clear()
        self.newHand()
        
            
# Generating a list with the cards
for rep in os.listdir('blackjack/cards'):
    if not os.path.isdir(f'blackjack/cards/{rep}'):
        continue
    for card in os.listdir(f'blackjack/cards/{rep}'):
        if card.endswith('.png'):

            if card.split('_')[0].upper() in ('JACK', 'KING', 'QUEEN'):
                value = 10
            elif card.split('_')[0].upper() == 'ACE':
                value = 11
            else:
                value = int(card.split('_')[0])

            cards.append(Card(image=os.path.abspath(f'blackjack\\cards\\{rep}\\{card}'), value=value))
