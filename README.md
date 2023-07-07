# 🃏 Blackjack-DiscordBot
 Play blackjack in Discord with your friends with this simple discord bot! You can invite the official bot [Clicking Here](https://discord.com/api/oauth2/authorize?client_id=1116728355484610581&permissions=52288&scope=bot) (Deactivated).

This is my first time using ``Asyncio`` and ``Discord.py``, so if you want to report an error or want to give a suggestion, just make a issue!

**To use the bot you'll need to:**
1. Create an application at the [Discord Developer Portal](discord.com/developers/applications) 
2. Get it's token on the "Bot" menu.
3. In the file named ``main.py``, replace "Your Token Here" with your token.
4. Run ``main.py``

## 🐱‍💻 Bot Commands
The bot uses the prefix ``bj`` for his commmands. You can also see a commands list using the command ``bj help`` in a discord text channel.

The list of commands is:
* ``bj help`` -> Shows the help menu.
* ``bj ranking`` -> Shows the global ranking (Based on the amount of "Win Points").
* ``bj create_table`` -> Creates a Blackjack table.
* ``bj delete_table`` -> Delete the current Blackjack table.
* ``bj start_table`` -> Starts the current Blackjack table.
* ``bj join_table`` -> Joins the channel's active table.
* ``bj leave_table`` -> Leaves the current table.
* ``bj kick [Nickname]`` -> Kicks [Nickname] out of your table

A "table" is like a real-life blackjack table, you can add up to seven people to it, each player will receive their cards and have their turn. **You can only have one table per channel, and it'll be deleted after 5 minutes of inactivity**.

## ⚠️ Disclaimer
Gambling is not cool, you can get [addicted to it](https://en.wikipedia.org/wiki/Problem_gambling) or get in big trouble. Also, in some countries gambling is ilegal, that includes [Brazil](https://pt.wikipedia.org/wiki/Jogos_de_apostas_no_Brasil) (The country that I live in).

Thinking about all that, instead of implementing a betting system, I implemented a "Wins" system, so, everytime you win a Blackjack game, you receive a "Win Point". **The Split or Double action modify the amount of "Win Points" you receive.**

## 📖 Blackjack rules
There is a little tuturial below, if you want some more informations, you can check the [Blackjack Wikipedia Article](https://en.wikipedia.org/wiki/Blackjack).

Blackjack is a card game where your goal is to beat the dealer (You play alone against him). A blackjack match starts with the dealer giving each player in the table 2 cards. He also gets two cards, but he only shows one of them, the other one is put upside down. Then he asks each of the players in the table if they want to **Stand**, **Hit**, **Double Down** or, sometimes, **Split**, some players may loose at this point. After all the players made their decision, the Dealer reveal his upside-down card, and if he wants, he can draw some cards, after he ends his turn, the match ends.

### 🎭 Winning and loosing
So, when you win and when you loose? There are three ways of winning in blackjack:
* Getting a higher amount of point than the Dealer.
* Getting a Blackjack (Excatly 21 points).
* The dealer gets a amount of points higher than 21.

And there are two ways of loosing:
* Getting less points than the Dealer.
* Getting more than 21 points.
* The dealer gets a Blackjack.

And you can even tie if both you and the dealer get the same amount of points!

(Considering that points are the sum of the cards' values in your hand)

### 💰 Cards' values
Every card in blackjack is worth what say they are (Example: Seven of Clubs is worth 7 points), except for the *Jack*, the *King*, the *Queen* and the *Ace*.

The *Jack*, the *King* and the *Queen* are all worth 10 points.

The *Ace* is worth 1 or 11 points. If considering the ace as 11 you get a amount of point higher than 21, then ace is equal to 1, otherwise ace is equal to 11. When you have other card and an ace (Wich is worth eleven) we say you have a *soft* amount of points (Example: Seven of Clubs + Ace = *Soft* Eighteen).

### ⚙️ Your Options
You have a several amount of option to choose when it's your turn:
* **Stand**: You're satisfied with your hand and don't want more cards. You basically skip your turn.
* **Hit**: You get another card.
* **Double**: At the first two cards you can get another card and double your bet, you're not able to get any cards for the rest of the match.
* **Split**: If your first two cards have the same value in points, you can create a new hand using one of the cards (You're basically playing two games at the same time). You have to bet the same value for the second hand that you betted in the first one.
* **Surrender (Rare)**: At some tables, if you don't like your cards, you can surrender, getting half of what you betted back.

