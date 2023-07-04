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
