from random import choice

from twitchio.ext import commands

from utils.misc import read_file


class Vozol(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='vozol',
        aliases=['воззл', 'возол', 'возл', 'возлик', 'воззлик'],
        cooldown={'per': 5, 'gen': 0},
        description='Вот это парилка нахуй.'
    )
    async def vozol(self, ctx):
        vozol = choice(read_file('data/vozol.txt'))
        message = f'Ты возлик со вкусом {vozol}'
        await ctx.reply(message)


def prepare(bot):
    bot.add_cog(Vozol(bot))
