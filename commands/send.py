import asyncio

from twitchio.ext import commands


class Send(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='send',
        aliases=['spam'],
        cooldown={'per': 0, 'gen': 5},
        description='Отправляет текст указанное количество раз (до 15).',
        flags=['moderator', 'whitelist']
    )
    async def send(self, ctx):
        if not (ctx.channel.bot_is_vip or ctx.channel.bot_is_mod):
            await ctx.reply('Боту необходима випка или модерка для работы этой команды')
            return
        content_split = ctx.content.lstrip(' /.').split()
        if not content_split:
            await ctx.reply('Введите текст')
            return

        try:
            num = min(int(content_split[0]), 15)
            if len(content_split) < 2:
                await ctx.reply('Введите текст')
                return
            message = ' '.join(content_split[1:])
        except ValueError:
            num = 1
            message = ' '.join(content_split)

        for i in range(num):
            await ctx.send(message)
            await asyncio.sleep(0.1)


def prepare(bot):
    bot.add_cog(Send(bot))
