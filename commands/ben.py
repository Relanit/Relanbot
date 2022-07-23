from random import choice

from twitchio.ext import commands


class Ben(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='ben',
        aliases=['бен'],
        cooldown={'per': 5, 'gen': 0},
        description='Бен.'
    )
    async def ben(self, ctx):
        smile = self.bot.smile(ctx, [['Ben'], ['☎']])
        message = smile + ' ' + choice(['Ho-ho-ho', 'Yes', 'No.', 'Ugh'])
        await ctx.reply(message)


def prepare(bot):
    bot.add_cog(Ben(bot))
