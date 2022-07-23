from collections import Counter
from datetime import datetime

from twitchio.ext import commands
from dateutil.parser import parse

from config import db


class StreamStats(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.event()
    async def event_message(self, message):
        if message.echo:
            return

        channel = message.channel.name
        author = message.author.name

        if channel in self.bot.streams:
            values = {'$inc': {f'users_stats.{author}': 1, 'total_messages': 1}}
            text = message.content.split()

            if not set(text).isdisjoint(self.bot.channel_smiles.get(channel, {})) or not set(text).isdisjoint(self.bot.global_smiles):
                counter = Counter(text)

                for word, count in counter.items():
                    if word in self.bot.channel_smiles.get(channel, {}) or word in self.bot.global_smiles:
                        values['$inc'][f'smiles_stats.{word}'] = count
                        values['$inc'][f'users_smiles_stats.{author}.{word}'] = count

            await db.streamstats.update_one({'channel': channel}, values)

    """
    
    !ss - статистика стрима
    !ss top - топ пользователей
    !ss smiles - топ смайлов
    !ss smiles [смайл] - статистика смайла
    !ss smiles [смайл] top - топ пользователей смайла
    
    !ss [ник] - статистика пользователя
    !ss [ник] smiles - статистика смайлов пользователя
    !ss [ник] smiles [смайл] - статистика смайла пользователя
    
    !ss me - ваша статистика
    !ss me smiles - ваш топ смайлов
    !ss me smiles [смайл] - ваша статистика смайла
    
    """

    @commands.command(
        name='streamstats',
        aliases=['ss'],
        cooldown={'per': 5, 'gen': 0},
        description='Статистика стрима. Полное описание: https://i.imgur.com/l1GzEiD.png'
    )
    async def streamstats(self, ctx):
        channel = ctx.channel.name
        streamstats = await db.streamstats.find_one({'channel': channel}, {'channel': 1})
        if not streamstats:
            smile = self.bot.smile(ctx, [['KEKVVait', 'modcheck', 'Awkward', 'awkward'], [':/']])
            await ctx.reply(f'У меня нет информации о прошедшем стриме {smile}')
            return

        content = ctx.content.replace('@', '')
        content_lower = content.lower()
        content_split = content.split()
        content_lower_split = content_lower.split()

        if not content:
            streamstats = await db.streamstats.find_one({'channel': channel}, {'total_messages': 1,
                                                                               'stream_start': 1,
                                                                               'stream_end': 1,
                                                                               'viewer_counts': 1,
                                                                               'users_stats': 1})
            total_messages = streamstats['total_messages']
            total_chatters = len(streamstats['users_stats'])
            if 'stream_end' in streamstats:
                duration = parse(streamstats['stream_end']) - parse(streamstats['stream_start'])
            else:
                duration = datetime.utcnow() - parse(streamstats['stream_start'])

            hours = duration.seconds // 3600
            minutes = (duration.seconds // 60) % 60
            messages_speed = round(total_messages / duration.seconds, 1)

            average_viewers = sum(streamstats['viewer_counts']) // len(streamstats['viewer_counts'])
            max_viewers = max(streamstats['viewer_counts'])

            message = f'NOTED Длительность: {str(hours) + "ч " if hours else ""} {str(minutes)}м. ' \
                      f'Средний онлайн: {average_viewers}. ' \
                      f'Максимум зрителей: {max_viewers}. ' \
                      f'Всего чаттеров: {total_chatters}. ' \
                      f'Всего сообщений: {total_messages}. ' \
                      f'Скорость сообщений: {messages_speed} в секунду.'
        elif content_lower == 'top':
            streamstats = await db.streamstats.find_one({'channel': channel}, {'users_stats': 1})
            items = streamstats['users_stats'].items()
            sorted_users = sorted(items, key=lambda x: x[1], reverse=True)

            top = []
            for place, user in enumerate(sorted_users[:5], start=1):
                name = user[0][:1] + u'\U000E0000' + user[0][1:]
                top.append(f'{place}. {name} - {user[1]}{" сообщений" if place == 1 else ""}')

            smile = self.bot.smile(ctx, '', 'chatting')
            message = f'{smile} Топ пользователей без личной жизни: {", ".join(top)}'
        elif content_lower in ('smiles', 'smile'):
            streamstats = await db.streamstats.find_one({'channel': channel}, {'smiles_stats': 1})
            items = streamstats['smiles_stats'].items()
            sorted_smiles = sorted(items, key=lambda x: x[1], reverse=True)
            top = []
            for place, smile in enumerate(sorted_smiles[:5], start=1):
                top.append(f'{place}. {smile[0]} - {smile[1]}{" использований" if place == 1 else ""}')

            smile = self.bot.smile(ctx, '', 'chatting')
            message = f'{smile} Топ смайлов за стрим: {", ".join(top)}'
        elif len(content_split) == 1:
            streamstats = await db.streamstats.find_one({'channel': channel}, {'users_stats': 1})
            user = content_lower_split[0]
            if user == 'me':
                if ctx.author.name in streamstats['users_stats']:
                    items = streamstats['users_stats'].items()
                    sorted_users = sorted(items, key=lambda x: x[1], reverse=True)

                    for pos in range(len(sorted_users)):
                        if ctx.author.name in sorted_users[pos]:
                            place = pos + 1
                            messages = sorted_users[pos][1]
                            break

                    message = f'{place} место ({messages} сообщений)'
                else:
                    smile = self.bot.smile(ctx, [['KEKVVait', 'modcheck', 'Awkward'], [':/']])
                    message = f'У вас ни одного сообщения за стрим {smile}'
            else:
                if user in streamstats['users_stats']:
                    items = streamstats['users_stats'].items()
                    sorted_users = sorted(items, key=lambda x: x[1], reverse=True)

                    for pos in range(len(sorted_users)):
                        if user in sorted_users[pos]:
                            place = pos + 1
                            messages = sorted_users[pos][1]
                            break

                    message = f'{user} - {place} место ({messages} сообщений)'
                else:
                    smile = self.bot.smile(ctx, [['KEKVVait', 'modcheck', 'Awkward'], [':/']])
                    message = f'У {user} ни одного сообщения за стрим {smile}'
        elif len(content_split) == 2 and 'smile' in content_lower_split[0]:
            streamstats = await db.streamstats.find_one({'channel': channel}, {'users_smiles_stats': 1,
                                                                               'smiles_stats': 1})
            smile = content_split[1]
            if smile in streamstats['smiles_stats']:
                usage_count = streamstats['smiles_stats'][smile]

                if usage_count > 1:
                    items = streamstats['smiles_stats'].items()
                    sorted_smiles = sorted(items, key=lambda x: x[1], reverse=True)

                    for pos in range(len(sorted_smiles)):
                        if smile in sorted_smiles[pos]:
                            place = pos + 1
                            break

                    chatters_count = 0

                    for user in streamstats['users_smiles_stats'].items():
                        if smile in user[1]:
                            chatters_count += 1

                    message = f'{smile} - {place} место, использовали {usage_count} раз(a) {chatters_count} человек(а)'
                else:
                    message = f'Смайл {smile} использовали 1 раз'
            else:
                message = f'Смайл {smile} использовали 0 раз'
        elif len(content_split) == 2 and 'smile' in content_lower_split[1]:
            user = content_lower_split[0]
            if user == 'me':
                streamstats = await db.streamstats.find_one({'channel': channel}, {f'users_smiles_stats.{ctx.author.name}': 1})
                if ctx.author.name in streamstats['users_smiles_stats']:
                    items = streamstats['users_smiles_stats'][ctx.author.name].items()
                    sorted_smiles = sorted(items, key=lambda x: x[1], reverse=True)

                    top = []
                    for place, smile in enumerate(sorted_smiles[:5], start=1):
                        top.append(f'{place}. {smile[0]} - {smile[1]}{" использований" if place == 1 else ""}')

                    smile = self.bot.smile(ctx, '', 'chatting')
                    message = f'{smile} Ваш топ смайлов за стрим: {", ".join(top)}'
                else:
                    smile = self.bot.smile(ctx, [['KEKVVait', 'modcheck', 'Awkward'], [':/']])
                    message = f'Вы не отправили ни одного смайла за стрим {smile}'
            else:
                streamstats = await db.streamstats.find_one({'channel': channel}, {f'users_smiles_stats.{user}': 1})
                if user in streamstats['users_smiles_stats']:
                    items = streamstats['users_smiles_stats'][user].items()
                    sorted_smiles = sorted(items, key=lambda x: x[1], reverse=True)

                    top = []
                    for place, smile in enumerate(sorted_smiles[:5], start=1):
                        top.append(f'{place}. {smile[0]} - {smile[1]}{" использований" if place == 1 else ""}')

                    smile = self.bot.smile(ctx, [['Chatting', 'FeelsChattingMan', 'chatting'], ['ImTyping ']])
                    message = f'{smile} Топ смайлов {user}: {", ".join(top)}'
                else:
                    smile = self.bot.smile(ctx, [['KEKVVait', 'modcheck', 'Awkward'], [':/']])
                    message = f'{user} не отправил ни одного смайла за стрим {smile}'
        elif len(content_split) == 3 and 'smile' in content_lower_split[0] and content_lower_split[2] == 'top':
            streamstats = await db.streamstats.find_one({'channel': channel}, {'users_smiles_stats': 1,
                                                                               'smiles_stats': 1})
            smile = content_split[1]
            if smile in streamstats['smiles_stats']:
                stats = []

                for user in streamstats['users_smiles_stats'].items():
                    if smile in user[1]:
                        stats.append((user[0], user[1][smile]))
                sorted_stats = sorted(stats, key=lambda x: x[1], reverse=True)

                top = []
                for place, user in enumerate(sorted_stats[:5], start=1):
                    name = user[0][:1] + u'\U000E0000' + user[0][1:]
                    top.append(f'{place}. {name} - {user[1]}{" использований" if place == 1 else ""}')

                smile1 = self.bot.smile(ctx, '', 'chatting')
                message = f'{smile1} Топ пользователей смайла {smile} : {", ".join(top)}'
            else:
                message = f'Смайл {smile} ни разу не отправили за стрим'
        elif len(content_split) == 3 and 'smile' in content_lower_split[1]:
            user = content_lower_split[0]
            smile = content_split[2]

            if user == 'me':
                streamstats = await db.streamstats.find_one({'channel': channel}, {f'users_smiles_stats.{ctx.author.name}': 1})
                if ctx.author.name in streamstats['users_smiles_stats']:
                    usage_count = streamstats['users_smiles_stats'][ctx.author.name].get(smile)

                    if usage_count:
                        message = f'Вы использовали смайл {smile} {usage_count} раз(а)'
                    else:
                        message = f'Вы ни разу не использовали {smile}'
                else:
                    smile = self.bot.smile(ctx, [['KEKVVait', 'modcheck', 'Awkward'], [':/']])
                    message = f'Вы не отправили ни одного смайла за стрим {smile}'
            else:
                streamstats = await db.streamstats.find_one({'channel': channel}, {f'users_smiles_stats.{user}': 1})
                if user in streamstats['users_smiles_stats']:
                    usage_count = streamstats['users_smiles_stats'][user].get(smile)

                    if usage_count:
                        message = f'{user} использовал смайл {smile} {usage_count} раз(а)'
                    else:
                        message = f'{user} ни разу не использовал {smile}'
                else:
                    smile = self.bot.smile(ctx, [['KEKVVait', 'modcheck', 'Awkward'], [':/']])
                    message = f'{user} не отправил ни одного смайла {smile}'
        else:
            message = 'Ошибка - !help ss'

        await ctx.reply(message)


def prepare(bot):
    bot.add_cog(StreamStats(bot))
