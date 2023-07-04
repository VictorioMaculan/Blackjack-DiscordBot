import discord
import utils as ut

from .hand import Hand


class Player():
    def __init__(self, profile: discord.Member | discord.User):
        self.profile = profile
        self.hands = ut.Alist()
        
        self.bet = 0
        self.result = 0 # The amount of points you won/lost in the last match
        self.prepare_player()
    
    def __eq__(self, other:object) -> bool:
        if isinstance(other, Player):
            return self.profile.id == other.profile.id
        elif isinstance(other, (discord.User, discord.Member)):
            return self.profile == other
        elif isinstance(other, int):
            return self.profile.id == other
        return self == other    
    
    
    def prepare_player(self):
        self.bet = 1 # Initial Betting Amount
        self.result = 0
        self.hands.clear()
        self.hands.append(Hand(player=self.profile))
    
    
    def split_hand(self, hand_to_split: Hand):
        hand1 = Hand(player=self.profile)
        hand2 = Hand(player=self.profile)
        
        hand1.hand.append(hand_to_split.hand[0])
        hand1.eval_hand()
        hand2.hand.append(hand_to_split.hand[1])
        hand2.eval_hand()
        
        self.hands.extend([hand1, hand2])
        self.hands.remove(hand_to_split)
