import asyncio
import asyncstdlib as a
import blackjack as bj


class Alist(list):
    async def __aiter__(self):
        for item in self:
            yield item


async def isChannelActive(channel):
    try:
        bj.active_tables.index(channel)
        return True
    except ValueError:
        return False


async def isPlayerActive(player):
    try:
        bj.active_tables.index(player)
        return True
    except ValueError:
        return False

async def findTableIndex(table_channel):
    async for table in bj.active_tables:
            if table.channel == table_channel:
                return table
    return None


def generateCards():
    pass