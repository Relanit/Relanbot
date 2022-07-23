from random import choice, sample
from twitchio.ext import commands

from config import db


class Slots(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='slots',
        aliases=['roll'],
        cooldown={'per': 15, 'gen': 0},
        description='Игра в слоты. Можно установить свои варианты через {prefix}set slots.'
    )
    async def slots(self, ctx):
        items = ['🍋', '🍒', '🍌']

        data = await db.users.find_one({'user_id': ctx.author.id})
        if data and 'slots' in data:
            items = data['slots']

        line = sample(items * 3, 3)

        result = 'Ты проиграл ' + self.bot.smile(ctx, '', 'sad')
        if line[0] == line[1] == line[2]:
            result = 'Ты выиграл ' + self.bot.smile(ctx, '', 'pog')

        line = '[ ' + ' | '.join(line) + ' ]'
        message = self.bot.smile(ctx, [['GAMBA']]) + ' ' + line + ' ' + result
        await ctx.reply(message)


def prepare(bot):
    bot.add_cog(Slots(bot))
