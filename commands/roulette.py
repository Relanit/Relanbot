import asyncio
from random import randint

from twitchio.ext import commands


class Roulette(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.roulettes = set()

    @commands.command(
        name='roulette',
        aliases=['рулетка'],
        cooldown={'per': 0, 'gen': 10},
        description='Испытать удачу в русской рулетке.'
    )
    async def roulette(self, ctx):
        if not ctx.channel.bot_is_mod:
            await ctx.reply('Боту необходима модерка для работы этой команды')
            return
        if ctx.channel.name not in self.roulettes:
            self.roulettes.add(ctx.channel.name)
            smile = self.bot.smile(ctx, '', 'meltdown')
            await ctx.send(f'{ctx.author.display_name} прислоняет револьвер к своей голове {smile}')
            await asyncio.sleep(randint(4, 8))

            if randint(0, 2) > 0:
                smile = self.bot.smile(ctx, [['Zaebalo']], 'sad', 'rip')
                await ctx.send(f'Выстрел! {ctx.author.display_name} не выживает {smile}')
                await ctx.send(f'/timeout {ctx.author.name} 60 Проигрыш в рулетке')
            else:
                smile = self.bot.smile(ctx, '', 'pog')
                await ctx.send(f'Щёлк! {ctx.author.display_name} выживает! {smile}')
            self.roulettes.remove(ctx.channel.name)


def prepare(bot):
    bot.add_cog(Roulette(bot))
