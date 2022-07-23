from random import randint

from twitchio.ext import commands


class Cock(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='cock',
        cooldown={'per': 5, 'gen': 0},
        description='YEP'
    )
    async def cock(self, ctx):
        number = randint(0, 30)
        smile = self.bot.smile(ctx, [], 'yep')

        if user := ctx.content.strip('@'):
            message = f'Cock {user} равен {number} {smile}'
        else:
            message = f'Ваш Cock равен {number} см {smile}'

        await ctx.reply(message)


def prepare(bot):
    bot.add_cog(Cock(bot))
