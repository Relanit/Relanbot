from random import choice

from twitchio.ext import commands


class Bts(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='bts',
        aliases=['бтс'],
        cooldown={'per': 5, 'gen': 0},
        description='Узнай, кто ты из BTS 😱.'
    )
    async def bts(self, ctx):
        bts = ['🐥Чимина🐥', '🐯Тэхэна🐯', '🐹Джина🐹', '🐿️Джей Хоупа🐿️', '🐰Чонгука🐰', '🐱Шуга🐱']
        message = f'Ты очень похож(а) на {choice(bts)} из BTS 😱'
        await ctx.reply(message)


def prepare(bot):
    bot.add_cog(Bts(bot))
