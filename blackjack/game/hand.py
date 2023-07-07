import discord
import utils as ut
from random import choices

initial_betting = 1


class Hand():
    def __init__(self, player: discord.Member | discord.User | str):
        self.player = player
        self.hand = ut.Alist()
        self.bet = initial_betting # The amount that the player betted in this hand
        self.total = 0
    
    def eval_hand(self):
        self.total = 0
        
        for card in self.hand[:]:
            if card.value is None:
                continue
            if card.value == 11:
                if self.total + 11 > 21:
                    self.total += 1
                    continue
            self.total += card.value


    def canDouble(self):
        return len(self.hand) <= 2
    
    
    def canSplit(self):
        return len(self.hand) == 2 and self.hand[0].value == self.hand[1].value
        
        
    def draw_cards(self, deck: list, amount=1):
        cards = choices(deck, k=amount)
        self.hand.extend(cards)
        for card in cards:
            deck.remove(card) 
        self.eval_hand()
        
        
    async def show_hand(self, channel: discord.TextChannel, show_options=False):
        name = self.player if isinstance(self.player, str) else self.player.name
        cards_img = ut.generateCards(self.hand)
        
        msg = discord.Embed(title=f'**{name}\'s Hand:**',  colour=discord.Colour.dark_green(),
                            description=f'``Total = {self.total}``')
        msg.set_footer(text='Made By: Victório Maculan')
        
        await channel.send(embed=msg)
        await channel.send(file=ut.pil2discord(cards_img))


    async def show_turn(self, channel:discord.TextChannel, hand_num=1):
        name = self.player if isinstance(self.player, str) else self.player.name
        cards_img = ut.generateCards(self.hand)
        msg = discord.Embed(title=f'**{name}\'s Hand N°{hand_num}:**',  colour=discord.Colour.dark_green(),
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
