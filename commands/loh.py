from twitchio.ext import commands


class Loh(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='loh',
        aliases=['лох'],
        cooldown={'per': 5, 'gen': 0},
        description='Рандомный лох из чата.'
    )
    async def loh(self, ctx):
        content = ctx.content
        if not content:
            content = self.bot.smile(ctx, [['Lohich'], ['Лох']])

        user = self.bot.random_chatter(ctx, allow_self=True)
        message = f'{user} 👈 {content}'
        await ctx.send(message)


def prepare(bot):
    bot.add_cog(Loh(bot))
