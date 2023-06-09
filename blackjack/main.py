import discord
import messages as msg
import database.DBlib as db


intents = discord.Intents().default()
intents.message_content = True
intents.guilds = True
intents.members = True
client = discord.Client(intents=intents)

prefix = 'bj'


@client.event
async def on_ready():
    print('\n\033[32mBlackjack is rolling!\033[m\n')


@client.event
async def on_user_update(before, after):
    if before.name != after.name:
        if db.isRegistered(after.id, table='user'):
            import sqlite3
            from contextlib import closing
            
            with sqlite3.connect(db.DBpath) as con:
                with closing(con.cursor()) as cursor:
                    cursor.execute('update user set name = ? where id = ?', (after.name, before.id))
                    
                    
@client.event
async def on_guild_join(guild):
    for channel in guild.channels:
        try:
            if isinstance(channel, discord.TextChannel):
                await channel.send(embed=msg.hello_msg)
                break
        except discord.Forbidden:
            continue


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if not message.content.startswith(prefix):
        return
    
    if not db.isRegistered(message.author.id, table='user'):
        db.registerUser(message.author.id, message.author.name)

    
    if message.content == f'{prefix} help':
        await message.channel.send(embed=msg.help_msg)
    
    if message.content == f'{prefix} ranking':
        await message.channel.send(embed=msg.ranking_msg())
    

if __name__ == '__main__':
    client.run('MTExNjcyODM1NTQ4NDYxMDU4MQ.GmLos7.tLufIQCaY649W7tKR89eZjpSkfnL1ShjmeU7ow')