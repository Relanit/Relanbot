from random import choice

from twitchio.ext import commands

from utils.misc import read_file


class Brawler(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='brawler',
        aliases=['бравлер'],
        cooldown={'per': 5, 'gen': 0},
        description='Узнай, кто ты из Brawl Stars 😱.'
    )
    async def brawler(self, ctx):
        brawlers = read_file('data/brawlers.txt')
        message = f'Ты очень похож(а) на {choice(brawlers)} из Brawl Stars 😱'
        await ctx.reply(message)


def prepare(bot):
    bot.add_cog(Brawler(bot))
