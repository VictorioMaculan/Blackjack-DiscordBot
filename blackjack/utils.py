import asyncio
import blackjack as bj

# TODO: Do theese in a async way


class Alist(list):
    async def __aiter__(self):
        for item in self:
            yield item


async def isChannelActive(channel):
    async for table in bj.active_tables:
        if table.channel == channel:
            return True
    return False


async def isPlayerActive(player):
    async for table in bj.active_tables:
        if player in table.players:
            return True
    return False

