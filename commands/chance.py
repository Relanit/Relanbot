from random import randint

from twitchio.ext import commands


class Chance(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='chance',
        aliases=['шанс'],
        cooldown={'per': 5, 'gen': 0},
        description='Узнать вероятность события.'
    )
    async def chance(self, ctx):
        content = ctx.content
        if not content:
            await ctx.reply('Введите текст')
            return

        if 'что' in content:
            content = content.lstrip('что')

        percent = randint(0, 100)
        smile = self.bot.smile(ctx, [], 'verypog')
        message = f'Шанс, что {content} равен {percent}% {smile}'
        await ctx.reply(message)


def prepare(bot):
    bot.add_cog(Chance(bot))
