from collections import Counter

from twitchio.ext import commands

from config import db


class OfflineStats(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.event()
    async def event_message(self, message):
        if message.echo:
            return

        channel = message.channel.name
        author = message.author.name

        if channel not in self.bot.streams and message.author.name not in self.bot.blacklist:
            values = {'$inc': {'total_messages': 1}, '$addToSet': {'chatters': author}}
            text = message.content.split()

            if not set(text).isdisjoint(self.bot.channel_smiles.get(channel, {})) or not set(text).isdisjoint(self.bot.global_smiles):
                counter = Counter(text)

                for word, count in counter.items():
                    if word in self.bot.channel_smiles.get(channel, {}) or word in self.bot.global_smiles:
                        values['$inc'][f'smiles_stats.{word}'] = count
                        values['$inc'][f'users_smiles_stats.{author}.{word}'] = count

            await db.offlinestats.update_one({'channel': channel}, values)

    """

    !os - статистика оффлайнчата
    !os smiles - топ смайлов
    !os smiles [смайл] - статистика смайла
    !os smiles [смайл] top - топ пользователей смайла

    !os [ник] smiles - статистика смайлов пользователя
    !os [ник] smiles [смайл] - статистика смайла пользователя

    !os me smiles - ваш топ смайлов
    !os me smiles [смайл] - ваша статистика смайла

    """

    @commands.command(
        name='offlinestats',
        aliases=['os'],
        cooldown={'per': 5, 'gen': 0},
        description='Статистика оффлайнчата. Полное описание: https://i.imgur.com/JjchSaf.png'
    )
    async def offlinestats(self, ctx):
        channel = ctx.channel.name
        offlinestats = await db.offlinestats.find_one({'channel': channel}, {'channel': 1})

        if not offlinestats:
            smile = self.bot.smile(ctx, [['KEKVVait', 'modcheck'], [':/']])
            await ctx.reply(f'У меня нет информации об оффчатике {smile}')
            return

        content = ctx.content.replace('@', '')
        content_lower = content.lower()
        content_split = content.split()
        content_lower_split = content_lower.split()

        if not content:
            offlinestats = await db.offlinestats.find_one({'channel': channel}, {'total_messages': 1,
                                                                                 'chatters': 1})
            total_messages = offlinestats['total_messages']
            total_chatters = len(offlinestats['chatters'])

            message = f'Всего чаттеров: {total_chatters}. ' \
                      f'Всего сообщений: {total_messages}. '
        elif content_lower in ('smiles', 'smile'):
            offlinestats = await db.offlinestats.find_one({'channel': channel}, {'smiles_stats': 1})
            items = offlinestats['smiles_stats'].items()
            sorted_smiles = sorted(items, key=lambda x: x[1], reverse=True)

            top = []
            for place, smile in enumerate(sorted_smiles[:5], start=1):
                top.append(f'{place}. {smile[0]} - {smile[1]}{" использований" if place == 1 else ""}')

            smile = self.bot.smile(ctx, '', 'chatting')
            message = f'{smile} Топ смайлов в оффчате: {", ".join(top)}'
        elif len(content_split) == 2 and 'smile' in content_lower_split[0]:
            offlinestats = await db.offlinestats.find_one({'channel': channel}, {'users_smiles_stats': 1,
                                                                                 'smiles_stats': 1})
            smile = content_split[1]
            if smile in offlinestats['smiles_stats']:
                usage_count = offlinestats['smiles_stats'][smile]

                if usage_count > 1:
                    items = offlinestats['smiles_stats'].items()
                    sorted_smiles = sorted(items, key=lambda x: x[1], reverse=True)

                    for pos in range(len(sorted_smiles)):
                        if smile in sorted_smiles[pos]:
                            place = pos + 1
                            break

                    chatters_count = 0

                    for user in offlinestats['users_smiles_stats'].items():
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
                offlinestats = await db.offlinestats.find_one({'channel': channel},
                                                              {f'users_smiles_stats.{ctx.author.name}': 1})
                if ctx.author.name in offlinestats['users_smiles_stats']:
                    items = offlinestats['users_smiles_stats'][ctx.author.name].items()
                    sorted_smiles = sorted(items, key=lambda x: x[1], reverse=True)

                    top = []
                    for place, smile in enumerate(sorted_smiles[:5], start=1):
                        top.append(f'{place}. {smile[0]} - {smile[1]}{" использований" if place == 1 else ""}')

                    smile = self.bot.smile(ctx, '', 'chatting')
                    message = f'{smile} Ваш топ смайлов в оффчате: {", ".join(top)}'
                else:
                    smile = self.bot.smile(ctx, [['KEKVVait', 'modcheck'], [':/']])
                    message = f'Вы не отправили ни одного смайла в оффчате {smile}'
            else:
                offlinestats = await db.offlinestats.find_one({'channel': channel}, {f'users_smiles_stats.{user}': 1})
                if user in offlinestats['users_smiles_stats']:
                    items = offlinestats['users_smiles_stats'][user].items()
                    sorted_smiles = sorted(items, key=lambda x: x[1], reverse=True)

                    top = []
                    for place, smile in enumerate(sorted_smiles[:5], start=1):
                        top.append(f'{place}. {smile[0]} - {smile[1]}{" использований" if place == 1 else ""}')

                    smile = self.bot.smile(ctx, '', 'chatting')
                    message = f'{smile} Топ смайлов {user}: {", ".join(top)}'
                else:
                    smile = self.bot.smile(ctx, [['KEKVVait', 'modcheck', 'Awkward'], [':/']])
                    message = f'{user} не отправил ни одного смайла в оффчате {smile}'
        elif len(content_split) == 3 and 'smile' in content_lower_split[0] and content_lower_split[2] == 'top':
            offlinestats = await db.offlinestats.find_one({'channel': channel}, {'users_smiles_stats': 1,
                                                                                 'smiles_stats': 1})
            smile = content_split[1]
            if smile in offlinestats['smiles_stats']:
                stats = []

                for user in offlinestats['users_smiles_stats'].items():
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
                message = f'Смайл {smile} ни разу не отправили в оффчате'
        elif len(content_split) == 3 and 'smile' in content_lower_split[1]:
            user = content_lower_split[0]
            smile = content_split[2]

            if user == 'me':
                offlinestats = await db.offlinestats.find_one({'channel': channel},
                                                              {f'users_smiles_stats.{ctx.author.name}': 1})
                if ctx.author.name in offlinestats['users_smiles_stats']:
                    usage_count = offlinestats['users_smiles_stats'][ctx.author.name].get(smile)

                    if usage_count:
                        message = f'Вы использовали смайл {smile} {usage_count} раз(а)'
                    else:
                        message = f'Вы ни разу не использовали {smile}'
                else:
                    smile = self.bot.smile(ctx, [['KEKVVait', 'modcheck', 'Awkward'], [':/']])
                    message = f'Вы не отправили ни одного смайла {smile}'
            else:
                offlinestats = await db.offlinestats.find_one({'channel': channel}, {f'users_smiles_stats.{user}': 1})
                if user in offlinestats['users_smiles_stats']:
                    usage_count = offlinestats['users_smiles_stats'][user].get(smile)

                    if usage_count:
                        message = f'{user} использовал смайл {smile} {usage_count} раз(а)'
                    else:
                        message = f'{user} ни разу не использовал {smile}'
                else:
                    smile = self.bot.smile(ctx, [['KEKVVait', 'modcheck', 'Awkward'], [':/']])
                    message = f'{user} не отправил ни одного смайла {smile}'
        else:
            message = f'Ошибка - {self.bot._prefix}help os'

        await ctx.reply(message)


def prepare(bot):
    bot.add_cog(OfflineStats(bot))
