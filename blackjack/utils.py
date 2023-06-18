import discord
import asyncstdlib as a
import blackjack as bj
from PIL import Image, ImageDraw


class Alist(list):
    async def __aiter__(self):
        for item in self:
            yield item
            

def pil2discord(pil_image: Image, format='png'):
    from io import BytesIO
    with BytesIO() as bi:
        pil_image.save(bi, format=format.upper())
        bi.seek(0)
        return discord.File(bi, filename=f'Image.{format.lower()}')
        


def isChannelActive(channel: discord.TextChannel):
    try:
        bj.active_tables.index(channel)
        return True
    except ValueError:
        return False


def isPlayerActive(player: discord.Member | discord.User):
    try:
        bj.active_tables.index(player)
        return True
    except ValueError:
        return False


async def findTable(channel: discord.TextChannel):
    if not isChannelActive(channel):
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


def generateCards(cards: list, gap=4, Cwidth=40, Cheight=58):
    # Background
    img = Image.new(mode='RGBA', size=(len(cards)*(Cwidth+gap)+gap, Cheight+gap*2), color='#216b19')
    pencil = ImageDraw.Draw(img)
    pencil.rectangle(xy=(0, 0, img.width-1, img.height-1), outline='#00260a', width=3)
    
    # Putting the cards
    for i, card in enumerate(cards):
        img.paste(Image.open(card.image), box=(gap+(Cwidth+gap)*i, gap, Cwidth*(i+1)+(gap*(i+1)), gap+Cheight))
    return img
    
    
if __name__ == '__main__':
    generateCards(bj.cards[0:3])
    