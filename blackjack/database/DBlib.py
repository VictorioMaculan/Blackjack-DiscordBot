import sqlite3
from contextlib import closing

DBpath = 'blackjack/database/BlackjackDB.db'


def getRegister(id, table, column='id'):
    with sqlite3.connect(DBpath) as con:
        con.row_factory = sqlite3.Row
        with closing(con.cursor()) as cursor:
            cursor.execute(f'select * from {table} where {column} = ?', (id,))
            return cursor.fetchone()


def isRegistered(id, table, column='id'):
    with sqlite3.connect(DBpath) as con:
        with closing(con.cursor()) as cursor:
            cursor.execute(f'select * from {table} where {column} = ?', (id,))
            return len(cursor.fetchall()) != 0


def registerUser(id, name):
    with sqlite3.connect(DBpath) as con:
        with closing(con.cursor()) as cursor:
            cursor.execute('''insert into user(id, name, wins) values(?, ?, ?)''', (id, name, 0))


def getRanking(places=10):
    with sqlite3.connect(DBpath) as con:
        with closing(con.cursor()) as cursor:
            cursor.execute('select * from user order by wins limit 10')
            return cursor.fetchall()


if __name__ == '__main__':
    """with sqlite3.connect(DBpath) as con:
        with closing(con.cursor()) as cursor:
             cursor.execute('''create table user(id text,
                            name text,
                            wins integer)''')"""