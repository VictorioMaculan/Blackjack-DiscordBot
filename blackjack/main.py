import discord
import asyncstdlib as a
import database.DBlib as db
import blackjack as bj
import utils as ut


intents = discord.Intents().default()
intents.message_content = True
intents.guilds = True
intents.members = True
client = discord.Client(intents=intents)

prefix = 'bj'


@client.event
async def on_ready():
    from time import strftime
    print(f'\n\033[32m[{strftime("%x")} - {strftime("%X")}] Blackjack is rolling!\033[m\n')


@client.event
async def on_user_update(before: discord.User, after: discord.User):
    if before.name != after.name:
        if await db.isRegistered(after.id, table='user'):
            import aiosqlite
            
            async with aiosqlite.connect(db.DBpath) as con:
                async with con.cursor() as cursor:
                    await cursor.execute('update user set name = ? where id = ?', (after.name, before.id))
                    await con.commit()
                    
@client.event
async def on_guild_join(guild):
    for channel in guild.channels:
        try:
            if isinstance(channel, discord.TextChannel):
                msg = discord.Embed(title='**Hello, guild!**', colour=discord.Colour.blurple())
                msg.description = "Hello! I'm a blackjack bot, to get started use: ``bj help``!"
                msg.set_footer(text='Made By: MestreDosPATUS')
                await channel.send(embed=msg)
        except discord.Forbidden:
            continue


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return
    if not message.content.startswith(prefix):
        return
    
    if not await db.isRegistered(message.author.id, table='user'):
        await db.registerUser(message.author.id, message.author.name)

    
    # Help Command
    if message.content == f'{prefix} help':
        msg = discord.Embed(title='**Commands:**', colour=discord.Colour.blurple())
        msg.description = '''
        ``bj help`` -> Shows the help menu
        ``bj ranking`` -> Shows the global rank

        ``bj create_table`` -> Creates a Blackjack table
        ``bj delete_table`` -> Delete the current Blackjack table
        ``bj start_table`` -> Starts the current Blackjack table
        ``bj join_table`` -> Joins the channel's active table
        ``bj leave_table`` -> Leaves the current table

        ``bj kick [Nickname]`` -> Kicks [Nickname] out of your table
        '''
        msg.set_footer(text='Made By: MestreDosPATUS')
        await message.channel.send(embed=msg)
    
    
    # Ranking Command
    if message.content == f'{prefix} ranking':
        msg = discord.Embed(title='**Top 10 Most Wins 🫡**', description='', 
                            color=discord.Colour.green())
        
        async for i, player in a.enumerate(await db.getRanking(10)):
            msg.description += f'``{i+1}°) {player[1]} ({player[2]} WINS)``\n' 
        msg.set_footer(text='Made By: MestreDosPATUS')
        
        await message.channel.send(embed=msg)
        
    
    # Create_Table Command
    if message.content == f'{prefix} create_table':
        if ut.isChannelActive(message.channel) or ut.isPlayerActive(message.author):
            await ut.error_msg(message.channel, 'There is not an active table in this channel or you\'re already in a table')
            return
        new_table = bj.Table(channel=message.channel, master=message.author)
        bj.active_tables.append(new_table)
        await new_table.show_table()
        del new_table
      
    
    # Delete_Table Command
    if message.content == f'{prefix} delete_table':
        table = await ut.findTable(message.channel)
        if table.ingame:
            return
        
        if table is None:
            await ut.error_msg(message.channel, 'There\'s not an active table in this channel!')
            return      
    
        if table.players[0] == message.author:
            bj.active_tables.remove(table)
            del table # TODO: Take a better look here
            await ut.sucess_msg(message.channel, 'The table was deleted!')
            return
        await ut.error_msg(message.channel, 'You don\'t have permission to do that!')
      
        
    # Start_Table Command
    if message.content == f'{prefix} start_table':
        table = await ut.findTable(message.channel)
        
        if table is None or not ut.isPlayerActive(message.author):
            await ut.error_msg(message.channel, 'There\'s not an active table in this channel or you\'re already in a table!')
            return
        
        if table.ingame:
            return
        if table.players[0] == message.author:
            await table.start_game(client)
            return
        await ut.error_msg(message.channel, 'You don\'t have permission to do that!')
    
    
    # Join_Table Command
    if message.content == f'{prefix} join_table':
        table = await ut.findTable(message.channel)
        if table.ingame:
            return
        
        if table is None or ut.isPlayerActive(message.author):
            await ut.error_msg(message.channel, 'There\'s not an active table in this channel or you\'re already in a table!')
            return
        
        await table.add_player(message.author)
        await table.show_table()

    
    # Leave_Table Command
    if message.content == f'{prefix} leave_table':
        table = await ut.findTable(message.channel)
        if table.ingame:
            return
        
        if table is None or not ut.isPlayerActive(message.author):
            await ut.error_msg(message.channel, 'You\'re not in a table!')
            return

        if table.players[0] == message.author:
            await ut.error_msg(message.channel, 'The table master has to delete the table if he wants to leave!')
            return
        await table.remove_player(message.author)
        await table.show_table()
            
            
    # Kick command
    if message.content.startswith(f'{prefix} kick'):
        table = await ut.findTable(message.channel)
        if table.ingame:
            return
        
        if table is None or not ut.isPlayerActive(message.author):
            await ut.error_msg(message.channel, 'You\'re not in a table!')
            return
        
        try:
            kicked_id = int(message.content.split()[2][2:][:-1]) # TODO: Clean Content
            if table.players[0] != message.author or table.players[0] == kicked_id:
                await ut.error_msg(message.channel, 'You don\'t have permision to do that!')
                return
            
            if kicked_id in table.players: # TODO: Take a better look here.
                    await table.remove_player(kicked_id)
                    await ut.sucess_msg(message.channel, 'The player got kicked from the table!')
                    return
            await ut.error_msg(message.channel, 'The player was not found!')
        except (IndexError, ValueError):
            await ut.error_msg(message.channel, 'Check if you typed everything right!')
            

if __name__ == '__main__':
    client.run('MTExNjcyODM1NTQ4NDYxMDU4MQ.GmLos7.tLufIQCaY649W7tKR89eZjpSkfnL1ShjmeU7ow')