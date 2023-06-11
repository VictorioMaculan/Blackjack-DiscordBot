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
    print('\n\033[32mBlackjack is rolling!\033[m\n')


@client.event
async def on_user_update(before, after):
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
        if await ut.isChannelActive(message.channel) or await ut.isPlayerActive(message.author):
            await message.channel.send(embed=discord.Embed(title='❌ Error', colour=discord.Colour.red(),
                                description='A table is already active in this channel or you\'re already in a table!'))
            return
        new_table = bj.Table(channel=message.channel, master=message.author)
        bj.active_tables.append(new_table)
        await new_table.show_table()
      
    
    # Delete_Table Command
    if message.content == f'{prefix} delete_table': # TODO: Padronizar!
        async for table in bj.active_tables:
            if table.channel == message.channel and table.players[0] == message.author:
                bj.active_tables.remove(table)
                await message.channel.send(embed=discord.Embed(title='✅ Success', colour=discord.Colour.green(),
                        description='The table was deleted.'))
                return
        await message.channel.send(embed=discord.Embed(title='❌ Error', colour=discord.Colour.red(),
                        description='There is no active table in this channel or you\'re not the table master!'))
      
        
    # Start_Table Command
    if message.content == f'{prefix} start_table':
        pass
    
    
    # Join_Table Command
    if message.content == f'{prefix} join_table':
        if await ut.isPlayerActive(message.author) or not await ut.isChannelActive(message.channel):
            await message.channel.send(embed=discord.Embed(title='❌ Error', colour=discord.Colour.red(),
                        description='You\'re already in a table or there\'s no active table in this channel!'))
            return
        
        async for table in bj.active_tables:
            if table.channel == message.channel:
                await table.add_player(message.author)
                await table.show_table()
                return
    
    
    # Leave_Table Command
    if message.content == f'{prefix} leave_table':
        if not await ut.isPlayerActive(message.author) or not await ut.isChannelActive(message.channel):
            await message.channel.send(embed=discord.Embed(title='❌ Error', colour=discord.Colour.red(),
                        description='You\'re not in a table!'))
            return

        async for table in bj.active_tables:
            if table.channel == message.channel:
                if table.players[0] == message.author:
                    await message.channel.send(embed=discord.Embed(title='❌ Error', colour=discord.Colour.red(),
                        description='You\'re the table master, if you want to leave, delete the table!'))
                    return
                await table.remove_player(message.author)
                await table.show_table()
                return
            
            
    # Kick command
    if message.content.startswith(f'{prefix} kick'):
        if not ut.isChannelActive(message.channel):
            return
        try:
            kicked_id = int(message.content.split()[2][2:][:-1])
            
            async for table in bj.active_tables:
                if table.channel == message.channel:
                    if message.author != table.players[0] or table.players[0].id == kicked_id:
                        await message.channel.send(embed=discord.Embed(title='❌ Error', colour=discord.Colour.red(),
                            description='You don\'t have permision to do that!'))
                        return
                    async for player in table.players:
                        if player.id == kicked_id:
                            await table.remove_player(player)
                            await message.channel.send(embed=discord.Embed(title='✅ Success', colour=discord.Colour.green(),
                                description='The player got kicked from the table.'))
                            return
                    await message.channel.send(embed=discord.Embed(title='❌ Error', colour=discord.Colour.red(),
                            description='The player was not found in the table!'))
        except IndexError:
            await message.channel.send(embed=discord.Embed(title='❌ Error', colour=discord.Colour.red(),
                            description='Check if you typed everything write!'))

if __name__ == '__main__':
    client.run('MTExNjcyODM1NTQ4NDYxMDU4MQ.GmLos7.tLufIQCaY649W7tKR89eZjpSkfnL1ShjmeU7ow')