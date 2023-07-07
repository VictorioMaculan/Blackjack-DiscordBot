import aiosqlite
import os

DBpath = os.path.join('blackjack', 'database', 'BlackjackDB.db')


async def createDB():
    async with aiosqlite.connect(DBpath) as con:
        async with con.cursor() as cursor:
            await cursor.execute('''create table user(id text,
                                name text,
                                wins integer)''')


async def getRegister(id, table: str, column='id'):
    async with aiosqlite.connect(DBpath) as con:
        con.row_factory = aiosqlite.Row
        async with con.execute(f'select * from {table} where {column} = ?', (id,)) as cursor:
            return await cursor.fetchone()


async def isRegistered(id, table: str, column='id'):
    async with aiosqlite.connect(DBpath) as con:
        async with con.execute(f'select * from {table} where {column} = ?', (id,)) as cursor:
            return len(await cursor.fetchall()) != 0


async def registerUser(id: str, name: str):
    async with aiosqlite.connect(DBpath) as con:
        async with con.cursor() as cursor:
            await cursor.execute('''insert into user(id, name, wins) values(?, ?, ?)''', (id, name, 0))
            await con.commit()


async def getRanking(places=10):
    async with aiosqlite.connect(DBpath) as con:
        async with con.execute('select * from user order by wins desc limit ?', (places,)) as cursor:
            return await cursor.fetchall()


async def modifyWins(id: str, num: int):
    async with aiosqlite.connect(DBpath) as con:
        async with con.cursor() as cursor:
            await cursor.execute(f'update user set wins = wins + {num} where id = ?', (id,))
            await con.commit()

import asyncio
from time import strftime
if not os.path.isfile(DBpath):
    asyncio.run(createDB())
    print(f'\n\033[32m[{strftime("%x")} - {strftime("%X")}] The database was created!\033[m\n')
