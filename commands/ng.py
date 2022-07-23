from datetime import datetime

from twitchio.ext import commands


class Ng(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='ng',
        aliases=['нг'],
        cooldown={'per': 5, 'gen': 0},
        description='Оставшееся время до Нового Года.'
    )
    async def new_year(self, ctx):
        now = datetime.today()
        nyd = datetime(now.year + 1, 1, 1)
        left = nyd - now
        minutes, seconds = divmod(left.seconds, 60)
        hours, minutes = divmod(minutes, 60)
        smile = self.bot.smile(ctx, [['PapichSng', 'sDR'], ['🎄', 'HolidaySanta']], 'ez', 'pog')

        if left.days >= 1:
            message = f'До Нового Года осталось {left.days}д {hours}ч {smile}'
        else:
            if hours >= 1:
                message = f'До Нового Года осталось {hours}ч {minutes}м {smile}'
            else:
                if minutes >= 1:
                    message = f'До Нового Года осталось {minutes}м {seconds}с {smile}'
                else:
                    message = f'До Нового Года осталось {seconds}с {smile}'

        await ctx.reply(message)


def prepare(bot):
    bot.add_cog(Ng(bot))
