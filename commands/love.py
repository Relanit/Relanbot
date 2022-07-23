from random import randint

from twitchio.ext import commands


class Love(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='love',
        cooldown={'per': 5, 'gen': 0},
        description='Узнай свою совместимость с кем-либо/чем-либо.'
    )
    async def love(self, ctx):
        content = ctx.content.strip('@')

        if not content:
            content = 'Chel'

        percent = randint(0, 100)
        if percent <= 40:
            smile = self.bot.smile(ctx, '', 'sad')
        elif percent == 100:
            smile = self.bot.smile(ctx, '', 'pog') + ' ' + self.bot.smile(ctx, '', 'love')
        else:
            smile = self.bot.smile(ctx, '', 'love')

        message = f'{ctx.author.display_name} и {content} совместимы на {percent}% {smile}'
        await ctx.reply(message)


def prepare(bot):
    bot.add_cog(Love(bot))
