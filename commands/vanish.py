from twitchio.ext import commands


class Vanish(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='vanish',
        aliases=['vanishme'],
        cooldown={'per': 5, 'gen': 0},
        description='Очистка чата от своих сообщений. Доверенным пользователям можно указывать время мута.'
    )
    async def vanish(self, ctx):
        duration = 1
        content = ctx.content
        if content and ctx.author.name in self.bot.trusted_users:
            try:
                duration = min(int(content), 1209600)
            except ValueError:
                return

        await ctx.send(f'/timeout {ctx.author.name} {duration} {self.bot._prefix}vanish')


def prepare(bot):
    bot.add_cog(Vanish(bot))
