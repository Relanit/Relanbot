from random import randint

from twitchio.ext import commands


class Iq(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='iq',
        cooldown={'per': 5, 'gen': 0},
        description='Узнай свой IQ или IQ пользователя, если указан ник.'
    )
    async def iq(self, ctx):
        number = randint(0, 189)

        if 0 <= number < 49:
            smile = self.bot.smile(ctx, [['gorillaSpin', 'MONKE'], ['🐒']])
        elif number == 49:
            smile = self.bot.smile(ctx, [['TROLL'], [':tf:']])
        elif 49 < number < 60:
            smile = self.bot.smile(ctx, [['WIdeEBLAN']], 'eblan')
        elif number == 60:
            smile = self.bot.smile(ctx, [['Svin'], ['🐷']])
        elif 60 < number < 89:
            smile = self.bot.smile(ctx, '', 'eblan')
        elif number == 89:
            smile = 'BOP'
        elif 89 < number < 110:
            smile = self.bot.smile(ctx, [['EZ', 'Krytoi']])
        elif number == 110:
            smile = self.bot.smile(ctx, [['KEKW'], ['😂']])
        elif number == 189:
            smile = self.bot.smile(ctx, [['blushW']], 'pog')
        else:
            smile = self.bot.smile(ctx, [['GIGACHAD', '5Head', 'WAYTOODANK']])

        if user := ctx.content.lstrip('@'):
            message = f'IQ {user} равен {number} {smile}'
        else:
            message = f'Ваш IQ равен {number} {smile}'

        await ctx.reply(message)


def prepare(bot):
    bot.add_cog(Iq(bot))
