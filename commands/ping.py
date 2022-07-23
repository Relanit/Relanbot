from twitchio.ext import commands


class Ping(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='ping',
        cooldown={'per': 0, 'gen': 5},
        description='Pong.',
        flags=['whitelist']
    )
    async def ping(self, ctx):
        message = self.bot.smile(ctx, [['TheSvinBot'], ['Pong.']])
        await ctx.reply(message)


def prepare(bot):
    bot.add_cog(Ping(bot))
