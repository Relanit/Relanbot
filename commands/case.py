import aiohttp
from random import choice

from twitchio.ext import commands, routines


class Case(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.skins = []
        self.get_skins.start(stop_on_error=False)

    @commands.command(
        name='case',
        aliases=['кейс'],
        cooldown={'per': 5, 'gen': 0},
        description='Покрутить кейс из CS:GO.'
    )
    async def case(self, ctx):
        skin = choice(self.skins)
        skin_name = skin['market_hash_name'].replace('.', ' ')
        skin_price = float(skin['price'])

        if skin_price <= 500:
            smile = self.bot.smile(ctx, '', 'sad')
        elif 500 < skin_price < 30000:
            smile = self.bot.smile(ctx, '', 'pog')
        else:
            smile = self.bot.smile(ctx, '', 'ez')

        message = f'Вам выпал {skin_name} стоимостью {skin_price} рублей {smile}'

        await ctx.reply(message)

    @routines.routine(iterations=1)
    async def get_skins(self):
        async with aiohttp.ClientSession() as session:
            url = 'https://market.csgo.com/api/v2/prices/RUB.json'
            async with session.get(url) as response:
                data = await response.json()
                self.skins = data['items']


def prepare(bot):
    bot.add_cog(Case(bot))
