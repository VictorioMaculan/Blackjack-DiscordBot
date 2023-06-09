import discord
import sqlite3
import database.DBlib as db


def ranking_msg():
    msg = discord.Embed()
    msg.title = '**Top 10 Most Wins 🫡**'
    msg.description = ''
    for i, player in enumerate(db.getRanking(10)):
        msg.description += f'``{i+1}°) {player[1]} ({player[2]} Wins)``'
    msg.color = discord.Colour.green()
    msg.set_footer(text='Made By: MestreDosPATUS')
    return msg
    

hello_msg = discord.Embed()
hello_msg.title = 'Hello, guild!'
hello_msg.description = "Hello! I'm a blackjack bot, to get started use: ``bj help``!"
hello_msg.colour = discord.Colour.blurple()
hello_msg.set_footer(text='Made By: MestreDosPATUS')


help_msg = discord.Embed()
help_msg.title = 'Commands:'
help_msg.description = '''
``bj help`` -> Shows the help menu
``bj ranking`` -> Shows the global rank

``bj create_table`` -> Creates a Blackjack table
``bj delete_table`` -> Delete the current Blackjack table
``bj start_table`` -> Starts the current Blackjack table
``bj join_table [TableId]`` -> Joins the [TableId] table

``bj kick [Nickname]`` -> Kicks [Nickname] out of your table
'''
help_msg.colour = discord.Colour.blurple()
help_msg.set_footer(text='Made By: MestreDosPATUS')