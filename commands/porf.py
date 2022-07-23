from random import choice

from twitchio.ext import commands
import aiohttp

from utils.misc import censore_banwords


class Porf(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='porf',
        cooldown={'per': 0, 'gen': 10},
        description='Генерация текста с помощью нейросети Порфирьевич.'
    )
    async def porf(self, ctx):
        prompt = ctx.content
        if not prompt:
            await ctx.reply('Введите текст')
            return

        timeout = aiohttp.ClientTimeout(total=12)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            url = 'https://pelevin.gpt.dobro.ai/generate/'
            async with session.get(url) as response:
                if response.status != 405:
                    await ctx.reply('Порфирьевич временно недоступен')
                    return

            async with session.post(url, json={'prompt': prompt, 'length': 50}) as response:
                response = await response.json()

        result = prompt + choice(response['replies'])
        message = censore_banwords(result)

        await ctx.reply(message)


def prepare(bot):
    bot.add_cog(Porf(bot))
