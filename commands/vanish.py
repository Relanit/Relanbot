from twitchio.ext import commands


class Vanish(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='vanish',
        cooldown={'per': 5, 'gen': 0},
        description='Очистка чата от своих сообщений. Доверенным пользователям можно указывать время мута.'
    )
    async def vanish(self, ctx):
        if not ctx.channel.bot_is_mod:
            await ctx.reply('Боту необходима модерка для работы этой команды')
            return

        if ctx.author.name in self.bot.trusted_users and ctx.content:
            try:
                duration = min(max(60, int(ctx.content)), 1209600)
            except ValueError:
                return

        message = f'/timeout {ctx.author.name} {duration} {self.bot._prefix}vanish'
        await ctx.send(message)


def prepare(bot):
    bot.add_cog(Vanish(bot))
