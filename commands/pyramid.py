import asyncio

from twitchio.ext import commands


class Pyramid(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='pyramid',
        aliases=['vpyramid'],
        cooldown={'per': 0, 'gen': 15},
        description='Строит пирамиду в чате.',
        flags=['moderator', 'trusted']
    )
    async def pyramid(self, ctx):
        if not (ctx.channel.bot_is_vip or ctx.channel.bot_is_mod):
            await ctx.reply('Боту необходима випка или модерка для работы этой команды')
            return
        content_split = ctx.content.split()
        if not content_split:
            await ctx.reply('Введите текст')
            return

        try:
            num = min(int(content_split[0]), 15)
            if len(content_split) < 2:
                await ctx.reply('Введите текст')
                return
            text = ' '.join(content_split[1:]).lstrip(' ./!') + ' '
        except ValueError:
            num = 3
            text = ' '.join(content_split).lstrip(' ./!') + ' '

        if ctx.command_alias == 'pyramid':
            counter = 1
            for i in range(num * 2 - 1):
                message = text * counter
                if counter < num and i < num:
                    counter += 1
                else:
                    counter -= 1

                if len(message) >= 500:
                    counter -= 1
                    i += 1
                    continue

                await ctx.send(message)
                await asyncio.sleep(0.1)
        else:
            for i in range(num):
                message = ' 󠀀 ' * (num - i) * 3 + text * (i + 1)

                if len(message) >= 500:
                    break

                await ctx.send(message)
                await asyncio.sleep(0.1)


def prepare(bot):
    bot.add_cog(Pyramid(bot))
