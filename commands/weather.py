import gettext
import os
from datetime import datetime, timedelta
import re
import time as t

from twitchio.ext import commands
import pycountry
import aiohttp

from config import db

russian = gettext.translation('iso3166', pycountry.LOCALES_DIR, languages=['ru'])
russian.install()


def get_country(code):
    ru = pycountry.countries.get(alpha_2=code)
    return _(ru.name)


def get_wind_direction(deg):
    val = int((deg / 22.5) + .5)
    directions = ['С', 'ССВ', 'СВ', 'ВСВ', 'В', 'ВЮВ', 'ЮВ', 'ЮЮВ', 'Ю', 'ЮЮЗ', 'ЮЗ', 'ЗЮЗ', 'З', 'ЗСЗ', 'СЗ', 'ССЗ']
    direction = directions[val % 16]

    return direction


class Weather(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='weather',
        aliases=['погода'],
        cooldown={'per': 10, 'gen': 0},
        description='Погода в указанном городе. Можно установить город по умолчанию через {prefix}set weather [город].'
    )
    async def weather(self, ctx):
        city = ctx.content.lower()

        if not city:
            data = await db.users.find_one({'user_id': ctx.author.id})
            if data and 'city' in data:
                city = data['city']
            else:
                await ctx.reply(f'Укажите город или установите его через {self.bot._prefix}set weather [город]')
                return
        elif city.startswith('@'):
            user = await self.bot.fetch_users(names=[city.strip('@')])
            if not user:
                await ctx.reply('Несуществующий логин')
                return
            data = await db.users.find_one({'user_id': user[0].id})
            if data and 'city' in data:
                city = data['city']
            else:
                await ctx.reply('Пользователь не указывал свой город.')
                return

        async with aiohttp.ClientSession() as session:
            url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={os.getenv("WEATHER_ID")}&lang=ru&units=metric'
            async with session.get(url) as response:
                data = await response.json()

                if data['cod'] == '404':
                    await ctx.reply('Город не найден. Если вы хотели узнать погоду в городе пользователя, добавьте @ перед ником')
                    return

            lat = data['coord']['lat']
            lon = data['coord']['lon']

            url = f'http://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&units=metric&exclude=current,minutely,hourly&appid={os.getenv("WEATHER_ID")}&lang=ru'
            async with session.get(url) as response:
                onecall = await response.json()

        city = data['name']
        country = f', {get_country(data["sys"]["country"])}' if 'country' in data['sys'] and city != get_country(data['sys']['country']) else ''

        if len(data['weather']) == 1:
            description = data['weather'][0]['description']
        else:
            description = data['weather'][0]['description'] + ', ' + data['weather'][1]['description']

        icon = self.get_icon(ctx, data, onecall)

        temp = round(data['main']['temp'], 1) if round(data['main']['temp'], 1) % 1 != 0 else int(data['main']['temp'])
        feels_like = f', ощущается как {round(data["main"]["feels_like"], 1)}°C' if abs(temp - data['main']['feels_like']) >= 1 else ''
        wind = data['wind']

        gust = ''
        if 'gust' in wind and wind['gust']:
            gust = f', порывы до {round(wind["gust"], 1) if round(wind["gust"], 1) % 1 != 0 else int(wind["gust"])} м/с.' if \
                wind['gust'] - wind['speed'] >= 0.5 else ''

        wind = f'Ветер: {get_wind_direction(wind["deg"])} {round(wind["speed"], 1) if round(wind["speed"], 1) % 1 != 0 else int(wind["speed"])} м/с{gust or ". "}' if wind["speed"] else 'Безветренно.'
        clouds = f'Облачность: {data["clouds"]["all"]}%.' if data["clouds"]["all"] else ''
        humidity = data['main']['humidity']

        if data['sys']['sunset'] != 0:
            if data['sys']['sunrise'] < t.time() < data['sys']['sunset']:
                time = datetime.utcfromtimestamp(data['sys']['sunset']) + timedelta(days=1) - datetime.utcnow()
                hours = time.seconds // 3600
                minutes = (time.seconds // 60) % 60
                if hours:
                    sun = f' Закат через {hours}ч {minutes}м'
                else:
                    sun = f' Закат через {minutes}м'
            elif t.time() > data['sys']['sunset'] > data['sys']['sunrise']:
                time = datetime.utcfromtimestamp(onecall['daily'][1]['sunrise']) + timedelta(days=1) - datetime.utcnow()
                hours = time.seconds // 3600
                minutes = (time.seconds // 60) % 60
                if hours:
                    sun = f' Восход через {hours}ч {minutes}м'
                else:
                    sun = f' Восход через {minutes}м'
            else:
                time = datetime.utcfromtimestamp(data['sys']['sunrise']) + timedelta(days=1) - datetime.utcnow()
                hours = time.seconds // 3600
                minutes = (time.seconds // 60) % 60
                if hours:
                    sun = f' Восход через {hours}ч {minutes}м'
                else:
                    sun = f' Восход через {minutes}м'
        else:
            sun = ' Полярный день'

        pressure = data['main']['pressure']

        warnings = ''
        if 'alerts' in onecall:
            warnings = []
            for alert in onecall['alerts']:
                if bool(re.search('[а-яА-ЯЁё]', alert['event'])) and alert['event'] not in warnings:
                    if 'Прочие опасности' not in alert['event']:
                        warnings.append(alert['event'])
                if len(warnings) == 2:
                    break

            if not warnings:
                for alert in onecall['alerts']:
                    if 'Прочие опасности' in alert['event']:
                        warnings = ''
                        break
                    alert_lower = alert['event'].lower()
                    if 'wind' in alert_lower:
                        alert['event'] = 'Ветер'
                    elif 'fog' in alert_lower:
                        alert['event'] = 'Туман'
                    elif 'gust' in alert_lower:
                        alert['event'] = 'Порывы ветра'
                    elif 'thunder' in alert_lower:
                        alert['event'] = 'Гроза'
                    elif 'low' in alert_lower and 'temperature' in alert_lower:
                        alert['event'] = 'Низкая температура'
                    elif 'high' in alert_lower and 'temperature' in alert_lower:
                        alert['event'] = 'Высокая температура'
                    elif 'rain' in alert_lower:
                        alert['event'] = 'Дождь'
                    else:
                        print(alert['event'])

                    if alert['event'] not in warnings:
                        warnings.append(alert['event'])

                    if len(warnings) == 2:
                        break

        if warnings:
            warnings = f'⚠️ Внимание: {", ".join(warnings)}.'

        message = f' {city}{country}: {icon} {description}, {temp}°C{feels_like}. {wind} {clouds}' \
                  f' Влажность: {humidity}%. Давление: {pressure} гПа. {sun}. {warnings}'

        await ctx.reply(message)

    def get_icon(self, ctx, data, onecall):
        icon = data['weather'][0]['icon']
        if icon == '01d' or '01' in icon and not data['sys']['sunset']:
            icon = self.bot.smile(ctx, [['Dadadada'], ['☀']])
        elif icon == '01n':
            moon_phase = onecall['daily'][0]['moon_phase']
            val = int(moon_phase / .125 + .5)
            moon_phases = ['🌑', '🌒', '🌓', '🌔', '🌕', '🌖', '🌗', '🌘']
            icon = moon_phases[val % 8]
        elif '02' in icon:
            icon = '⛅'
        elif '03' in icon:
            icon = '☁️'
        elif '04' in icon:
            icon = '☁️'
        elif '09' in icon:
            icon = self.bot.smile(ctx, [['FeelsRainMan', 'Rain'], ['🌧️']])
        elif '10' in icon:
            icon = self.bot.smile(ctx, [['FeelsRainMan'], ['🌦️']])
        elif '11' in icon:
            icon = '⛈'
        elif '13' in icon:
            icon = '❄️'
        elif '50' in icon:
            icon = '🌫️'

        return icon


def prepare(bot):
    bot.add_cog(Weather(bot))
