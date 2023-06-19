from random import randint, choices, shuffle
import asyncstdlib as a
import asyncio
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
    
    
    async def start_game(self, client: discord.Client): # TODO: Concertar e Melhorar e Olhar esse Client
        self.ingame = True
        self.last_game = time()
        self.deck = shuffle(ut.Alist(cards))
        
        dealer = Hand(player='Dealer')
        blackjack, lost = list(), list()
        game_round = 1
        
        # Match
        while True:
            # Dealer's Turn
            while True:
                # TODO: Acabar o sistema do Dealer a checar os DRY
                if game_round == 1:                    
                    await dealer.draw_cards(self.deck)
                    dealer.hand.append(Card(image='blackjack/cards/back.png', value=None)) # Back of the Cards
                    await dealer.show_hand(self.channel)
                    break
                if game_round == 2:
                    dealer.hand.pop()
                    dealer.draw_cards(self.deck)
                    await dealer.show_hand(self.channel)
                
                if dealer.total <= 16:
                    await self.channel.send(f'The dealer chose **hit**!')
                    await dealer.show_hand(self.channel)
                    continue
                await self.channel.send(f'The dealer chose **stand**!')
                
            '''if len(losers) + len(winners) == len(self.players):
                # Adicionar um resumo da partida
                    break'''
            # Players' turn
            async for player in self.players:
                player: Player
                 
                if player in lost or player in blackjack:
                    continue
                if game_round == 1:
                    await player.hand.draw_cards(self.deck, amount=2)
                
                await asyncio.sleep(3)
                if player.hand.total == 21: # TODO: DRY
                    await self.channel.send(embed=discord.Embed(title=f'**{player.profile.name} got a Blackjack!**',  colour=discord.Colour.dark_purple(),
                            description=f'``Total = {player.hand.total}``'))
                    blackjack.append(player)
                    continue
                
                def check(reaction, user):
                    return reaction.emoji in ('🎯', '🛑', '💸', '✂️') and player.profile.id == user.id 
                
                try:
                    while True:
                        await player.hand.show_turn(self.channel, game_round)
                        output = await client.wait_for('reaction_add', timeout=30, check=check)
                        
                        if output[0].emoji == '🎯':
                            await self.channel.send(f'{player.profile.name} chose **hit**!')
                            await player.hand.draw_cards(self.deck)
                        
                        elif output[0].emoji == '🛑':
                            await self.channel.send(f'{player.profile.name} chose **stand**!')
                            break
                        
                        elif output[0].emoji == '💸' and player.hand.canDouble(game_round):
                            pass
                        
                        elif output[0].emoji == '✂️' and player.hand.canSplit():
                            pass
                        
                        if player.hand.total == 21: # TODO: DRY
                            await self.channel.send(embed=discord.Embed(title=f'**{player.profile.name} got a Blackjack!**',  colour=discord.Colour.dark_purple(),
                                                description=f'``Total = {player.hand.total}``'))
                            blackjack.append(player)
                            break
                        if player.hand.total > 21:
                            await self.channel.send(embed=discord.Embed(title=f'**{player.profile.name} lost!**',  colour=discord.Colour.red(),
                                description=f'``Total = {player.hand.total}``'))
                            lost.append(player)
                            break
                
                except asyncio.TimeoutError:
                    await ut.error_msg(self.channel, f'{player.profile.name} took too long! Skipping his/her turn...')
            game_round += 1
            await self.channel.send('Dealer')    
                
                        
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


    def canDouble(self, game_round):
        return len(self.hand) == 2 and game_round == 1
    
    
    def canSplit(self):
        return self.hand[0].value == self.hand[1].value 
        
        
    async def draw_cards(self, deck: list, amount=1): # TODO: Take a better look here
        cards = choices(deck, k=amount)
        self.hand.extend(cards)
        for card in cards:
            deck.remove(card)
        await self.eval_hand()
        
        
    async def show_hand(self, channel: discord.TextChannel):
        name = self.player if isinstance(self.player, str) else self.player.name
        cards_img = ut.generateCards(self.hand)
        
        msg = discord.Embed(title=f'**{name}\'s Hand:**',  colour=discord.Colour.dark_green(),
                            description=f'``Total = {self.total}``')
        msg.set_footer(text='Made By: MestreDosPATUS')
        
        await channel.send(embed=msg)
        await channel.send(file=ut.pil2discord(cards_img))


    async def show_turn(self, channel:discord.TextChannel, game_round: int):
        name = self.player if isinstance(self.player, str) else self.player.name
        cards_img = ut.generateCards(self.hand)
        msg = discord.Embed(title=f'**{name}\'s Hand:**',  colour=discord.Colour.dark_green(),
                            description=f'''``Total = {self.total}``
                            
                                            **Your options:**
                                            🎯 -> Hit
                                            🛑 -> Stand''')
            
        if self.canDouble(game_round):
            msg.description += '\n 💸 -> Double Down'
        if self.canSplit():
            msg.description += '\n ✂️ -> Split'
        msg.set_footer(text='You have 30 seconds to choose what to do!')

        menu = await channel.send(embed=msg)
        await channel.send(file=ut.pil2discord(cards_img))
        
        await menu.add_reaction('🎯')
        await menu.add_reaction('🛑')
        if self.canDouble(game_round):
            await menu.add_reaction('💸')
        if self.canSplit():
            await menu.add_reaction('✂️')
        

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
