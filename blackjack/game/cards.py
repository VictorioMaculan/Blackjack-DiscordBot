import os.path
import utils as ut

cards = ut.Alist()


class Card():
    def __init__(self, image: str, value: str | int):
        self.image = image
        self.value = value
        
    def __str__(self) -> str:
        return str(self.value)
    

# Generating a list with the cards
cards_dir = os.path.join('blackjack', 'cards')
for rep in os.listdir(cards_dir):
    rep_dir = os.path.join(cards_dir, rep)
    if not os.path.isdir(rep_dir):
        continue
    for card in os.listdir(rep_dir):
        if card.endswith('.png'):
            card_name = card.split('_')[0].upper()
            if card_name in ('JACK', 'KING', 'QUEEN'):
                value = 10
            elif card_name == 'ACE':
                value = 11
            else:
                value = int(card_name)
            cards.append(Card(image=os.path.abspath(os.path.join(rep_dir, card)), value=value))
