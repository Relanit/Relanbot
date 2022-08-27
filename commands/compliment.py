from random import choice

from twitchio.ext import commands

from utils.misc import read_file


class Compliment(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='compliment',
        aliases=['c'],
        cooldown={'per': 5, 'gen': 0},
        description='Подарить комплимент рандомному/указанному чаттеру.'
    )
    async def compliment(self, ctx):
        user = ctx.content.strip('@')
        if not user:
            user = self.bot.random_chatter(ctx)

        compliments = read_file('data/compliments.txt')
        compliment = choice(compliments)

        smile = self.bot.smile(ctx, [['Flushed', 'AWWWW']], 'love')
        message = f'{ctx.author.display_name} говорит {user}: {compliment} {smile}'
        await ctx.reply(message)


def prepare(bot):
    bot.add_cog(Compliment(bot))
