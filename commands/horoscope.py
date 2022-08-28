import difflib
import os

from bs4 import BeautifulSoup
import aiohttp
from twitchio.ext import commands, routines

from config import db
from utils.misc import censore_banwords


def similarity(s1, s2):
    matcher = difflib.SequenceMatcher(None, s1, s2)
    return matcher.ratio()


class Horoscope(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.horoscopes = {}
        self.update_horoscopes.start(stop_on_error=False)

    @commands.command(
        name='horoscope',
        aliases=['гороскоп'],
        cooldown={'per': 5, 'gen': 0},
        description='Гороскоп по знаку зодиака. Можно установить знак зодиака по умолчанию через {prefix}set horoscope [знак].'
    )
    async def horoscope(self, ctx):
        sign = ctx.content.lower()

        if not sign:
            data = await db.users.find_one({'user_id': ctx.author.id})
            if data and 'horoscope' in data:
                sign = data['horoscope']
            else:
                await ctx.reply(f'Укажите знак зодиака или установите его через {self.bot._prefix}set horoscope [знак]')
                return
        elif sign.startswith('@'):
            user = await self.bot.fetch_users(names=[sign.strip('@')])
            if not user:
                await ctx.reply('Несуществующий логин')
                return

            data = await db.users.find_one({'user_id': str(user[0].id)})
            if data and 'horoscope' in data:
                sign = data['horoscope']
            else:
                await ctx.reply('Пользователь не указывал свой знак зодиака')
                return

        key = sign
        if sign not in self.horoscopes:
            new_sign = ''
            sim = 0
            for s in self.horoscopes:
                if s not in ['рыбы', 'водолей', 'козерог', 'стрелец', 'скорпион', 'весы', 'дева', 'лев', 'рак',
                             'близнецы', 'телец', 'овен'] and (new_sim := similarity(sign, s)) > sim:
                    new_sign = s
                    sim = new_sim

            if sim < 0.5:
                await ctx.reply('Гороскоп не найден')
                return

            key = new_sign

        match sign:
            case 'рыбы':
                emoji = '♓'
            case 'водолей':
                emoji = '♒ '
            case 'козерог':
                emoji = '♑'
            case 'стрелец':
                emoji = '♐'
            case 'скорпион':
                emoji = '♏'
            case 'весы':
                emoji = '♎'
            case 'дева':
                emoji = '♍'
            case 'лев':
                emoji = '♌'
            case 'рак':
                emoji = '♋'
            case 'близнецы':
                emoji = '♊'
            case 'телец':
                emoji = '♉'
            case 'овен':
                emoji = '♈'

        message = emoji + ' ' + self.horoscopes[key]
        await ctx.reply(message)

    @routines.routine(minutes=10, iterations=0)
    async def update_horoscopes(self):
        async with aiohttp.ClientSession() as session:
            url = 'https://api.vk.com/method/wall.get'
            params = {
                'access_token': os.getenv('VK_TOKEN'),
                'v': 5.131,
                'domain': 'godnoscop',
                'count': 30,
            }

            async with session.get(url, params=params) as response:
                data = await response.json()

        raw_posts = data['response']['items']
        posts = []

        for i, post in enumerate(raw_posts):
            posts.append(post['text'])

            if not post['text'] and i < 3:
                posts.clear()

                url = 'https://nitter.net/godnoscop'
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        html = await response.text()

                soup = BeautifulSoup(html, 'html.parser')
                blocks = soup.find_all('div', class_='tweet-content')

                for block in blocks:
                    posts.append(block.getText(strip=True))

                break

        self.horoscopes.clear()

        for post in posts:
            split_text = post.replace('\n', ' ').split('. ')
            sign = split_text[0].lower()

            if len(sign.split()) == 1 and sign not in self.horoscopes:
                self.horoscopes[sign] = censore_banwords(f'{sign.capitalize()} - {". ".join(split_text[1:])}')

            if len(self.horoscopes) == 12:
                return


def prepare(bot):
    bot.add_cog(Horoscope(bot))
