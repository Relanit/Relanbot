from datetime import datetime

from dateutil.parser import parse
from twitchio.ext import commands

from config import db


class Uptime(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='uptime',
        aliases=['up', 'time', 'время'],
        cooldown={'per': 0, 'gen': 5},
        description='Показывает длительность стрима и длительность текущей игры, либо время с конца прошлого стрима.',
        flags=['whitelist']
    )
    async def uptime(self, ctx):
        if ctx.channel.name in self.bot.streams:
            stream = await db.streams.find_one({'channel': ctx.channel.name})
            started_at = parse(stream['started_at'])
            game_name = stream['game_name']

            now = datetime.utcnow()
            from_stream_start = now - started_at
            minutes, seconds = divmod(from_stream_start.seconds, 60)
            hours, minutes = divmod(minutes, 60)

            if hours:
                from_stream_start = f'{hours}ч {minutes}м'
            else:
                from_stream_start = f'{minutes}м {seconds}с'

            if game_name == 'Just Chatting':
                message = f'Cтрим идёт {from_stream_start}'
            else:
                game_started_at = parse(stream['game_started_at'])
                from_game_start = now - game_started_at
                minutes, seconds = divmod(from_game_start.seconds, 60)
                hours, minutes = divmod(minutes, 60)

                if hours == 0:
                    from_game_start = f'{minutes}м {seconds}с'
                else:
                    from_game_start = f'{hours}ч {minutes}м'
                message = f'Стрим идёт {from_stream_start} | Играем в {game_name} уже {from_game_start}'

            await ctx.reply(message)
        else:
            streamstats = await db.streamstats.find_one({'channel': ctx.channel.name}, {'stream_end': 1})

            if not streamstats:
                smile = self.bot.smile(ctx, [['KEKVVait', 'modcheck', 'Awkward'], [':/']])
                await ctx.reply(f'У меня нет информации о прошедшем стриме {smile}')
                return

            stream_end = parse(streamstats['stream_end'])

            now = datetime.utcnow()
            from_stream_end = now - stream_end
            minutes, seconds = divmod(from_stream_end.seconds, 60)
            hours, minutes = divmod(minutes, 60)
            days = from_stream_end.days

            if days and hours:
                from_stream_end = f'{days}д {hours}ч {minutes}м'
            elif days:
                from_stream_end = f'{days}д {minutes}м'
            elif hours:
                from_stream_end = f'{hours}ч {minutes}м'
            else:
                from_stream_end = f'{minutes}м {seconds}с'

            message = f'Стрим закончился {from_stream_end} назад'

            await ctx.reply(message)


def prepare(bot):
    bot.add_cog(Uptime(bot))
