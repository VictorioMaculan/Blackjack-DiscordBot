import discord
import asyncstdlib as a
import database.DBlib as db
import blackjack as bj


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
async def on_message(message):
    if message.author == client.user:
        return
    if not message.content.startswith(prefix):
        return
    
    if not await db.isRegistered(message.author.id, table='user'):
        await db.registerUser(message.author.id, message.author.name)

    
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
    
    
    if message.content == f'{prefix} ranking':
        msg = discord.Embed(title='**Top 10 Most Wins 🫡**', description='', 
                            color=discord.Colour.green())
        
        async for i, player in a.enumerate(await db.getRanking(10)):
            msg.description += f'``{i}°) {player[1]} ({player[2]} WINS)\n``' 
        msg.set_footer(text='Made By: MestreDosPATUS')
        
        await message.channel.send(embed=msg)
        
    
    if message.content == f'{prefix} create_table':
        new_table = bj.Table(channel=message.channel, master=message.author)
        if not new_table in bj.active_tables:
            bj.active_tables.append(new_table)
            await new_table.show_table()
            return
        await message.channel.send(embed=discord.Embed(title='❌ Error', colour=discord.Colour.red(),
                            description='A Blackjack table is already active in this channel!'))

if __name__ == '__main__':
    client.run('MTExNjcyODM1NTQ4NDYxMDU4MQ.GmLos7.tLufIQCaY649W7tKR89eZjpSkfnL1ShjmeU7ow')