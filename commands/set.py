import os
from collections import Counter

import aiohttp
from twitchio.ext import commands

from config import db


class Set(commands.Cog):
    """
    
    !set weather [город]
    !set horoscope [знак]
    !set slots [варианты через пробел]
    
    !reset
    !reset weather
    !reset horoscope
    !reset slots
    
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='set',
        aliases=['reset'],
        cooldown={'per': 5, 'gen': 0},
        description='Установка гороскопа, города или слотов по умолчанию. {prefix}reset для сброса данных. Примеры: https://i.imgur.com/LvDuz9a.png'
    )
    async def set(self, ctx):
        user_id = ctx.author.id

        if ctx.command_alias == f'set':
            content = ctx.content.split()
            if len(content) < 2:
                await ctx.reply('Неверный ввод, скорее всего, вы забыли одно из этих слов: horoscope, weather, slots')
                return

            if self.bot.get_command_name(content[0].lower()) == 'horoscope':
                if content[1].lower() not in ['овен', 'телец', 'близнецы', 'рак', 'лев', 'дева', 'весы', 'скорпион', 'стрелец', 'козерог', 'водолей', 'рыбы']:
                    await ctx.reply('Неверный знак зодиака')
                    return

                data = {'horoscope': content[1].lower()}
            elif content[0].lower() in ('город', 'city', 'weather', 'погода'):
                url = f'http://api.openweathermap.org/data/2.5/weather?q={" ".join(content[1:]).lower()}&appid={os.getenv("WEATHER_ID")}&lang=ru&units=metric'
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        data = await response.json()

                if data['cod'] == '404':
                    await ctx.reply('Город не найден')
                    return

                data = {'city': ' '.join(content[1:]).lower()}
            elif self.bot.get_command_name(content[0].lower()) == 'slots':
                if len(content) < 4:
                    await ctx.reply('Укажите как минимум 3 варианта')
                    return
                elif len(Counter(content[1:])) < len(content[1:]):
                    await ctx.reply('Варианты не должны повторяться')
                    return

                for slot in content[1:]:
                    if len(slot) > 25:
                        if slot not in self.bot.channel_smiles[ctx.channel.name]:
                            await ctx.reply('Максимальная длина варианта 25 символов')
                            return
                data = {'slots': content[1:]}
            else:
                await ctx.reply('Неверный ввод. Скорее всего, вы забыли одно из этих слов: horoscope, weather, slots')
                return

            await db.users.update_one({'user_id': user_id},
                                      {'$setOnInsert': {'user_id': user_id},
                                       '$set': data}, upsert=True)
        else:
            if ctx.command_alias == f'reset':
                content = ctx.content.split()

                if not content:
                    data = 'all'
                elif self.bot.get_command_name(content[0].lower()) == 'horoscope':
                    data = {'horoscope': ''}
                elif content[0].lower() in ('город', 'city', 'погода'):
                    data = {'city': ''}
                elif self.bot.get_command_name(content[0].lower()) == 'slots':
                    data = {'slots': ''}
                else:
                    await self.bot.send_message(ctx, 'Неверный ввод.', 'reply')
                    return

                if data == 'all':
                    await db.users.delete_one({'user_id': user_id})
                else:
                    await db.users.update_one({'user_id': user_id}, {'$unset': data})

        await ctx.reply('Готово.')


def prepare(bot):
    bot.add_cog(Set(bot))
