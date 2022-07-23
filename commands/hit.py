from random import choice

from twitchio.ext import commands


class Hit(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='hit',
        aliases=['уебать'],
        cooldown={'per': 5, 'gen': 0},
        description='Уебать.'
    )
    async def hit(self, ctx):
        user = ctx.content.strip('@')
        if not user:
            user = self.bot.random_chatter(ctx)

        how = ['слабовато', 'со всей силы', 'так, что тот потерял сознание']
        smile = self.bot.smile(ctx, [['Boxich'], ['👊']])
        message = f'{ctx.author.display_name} уебал {user} {choice(how)} {smile}'
        await ctx.reply(message)


def prepare(bot):
    bot.add_cog(Hit(bot))
