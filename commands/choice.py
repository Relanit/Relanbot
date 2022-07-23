import aiohttp
from twitchio.ext import commands

from config import RANDOMORG_TOKEN


class Choice(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='choice',
        aliases=['pick'],
        cooldown={'per': 5, 'gen': 0},
        description='Выбор варианта из списка. Разделитель - пробел, либо "или", можно указать диапазон чисел через ":".'
    )
    async def choice(self, ctx):
        content = ctx.content
        if not content:
            await ctx.reply('Укажите варианты через пробел или "или".')
            return

        if 'или' in content:
            content_split = content.split('или')
        else:
            content_split = content.split()

        range_ = False
        if len(content_split) == 1:
            if ':' in content_split[0]:
                range_ = True
                try:
                    min_, max_ = map(int, content_split[0].split(':'))
                except ValueError:
                    await ctx.reply(f'Должно быть указано целое число')
                    return
                if min_ >= max_:
                    await ctx.reply('Минимальное число больше максимального')
                    return
                elif len(str(min_).strip('-')) > 9 or len(str(max_).strip('-')) > 9:
                    await ctx.reply('Число не должно содержать более 9 цифр')
                    return
            else:
                await ctx.reply('Укажите больше одного варианта.')
                return
        else:
            min_ = 0
            max_ = len(content_split) - 1

        js = {
            'jsonrpc': '2.0',
            'method': 'generateIntegers',
            'params': {
                'apiKey': RANDOMORG_TOKEN,
                'min': min_,
                'max': max_,
                'n': 1,
            },
            'id': 1,
        }

        async with aiohttp.ClientSession() as session:
            async with session.get('http://api.random.org/json-rpc/1/invoke', json=js) as response:
                response = await response.json()
                index = response['result']['random']['data'][0]

        message = content_split[index] if not range_ else str(index)
        await ctx.reply(message)


def prepare(bot):
    bot.add_cog(Choice(bot))
