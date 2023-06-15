import discord
import asyncio
import asyncstdlib as a
import blackjack as bj


class Alist(list):
    async def __aiter__(self):
        for item in self:
            yield item


async def isChannelActive(channel: discord.TextChannel):
    try:
        bj.active_tables.index(channel)
        return True
    except ValueError:
        return False


async def isPlayerActive(player: discord.Member | discord.User):
    try:
        bj.active_tables.index(player)
        return True
    except ValueError:
        return False


async def findTable(channel: discord.TextChannel):
    if not await isChannelActive(channel):
        return 
    async for table in bj.active_tables:
            if table == channel:
                return table
    return


async def error_msg(channel: discord.TextChannel, description: str):
    await channel.send(embed=discord.Embed(title='❌ Error', colour=discord.Colour.red(),
                description=description))
    

async def sucess_msg(channel: discord.TextChannel, description: str):
    await channel.send(embed=discord.Embed(title='✅ Success', colour=discord.Colour.green(),
                    description=description))


def generateCards():
    pass