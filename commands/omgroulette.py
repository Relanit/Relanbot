import asyncio
import itertools
from random import choice, randint

from twitchio.ext import commands


class Omgroulette(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.omgroulettes = set()
        self.members = {}

    @commands.Cog.event()
    async def event_message(self, message):
        if message.echo:
            return

        if message.channel.name in self.omgroulettes:
            if self.bot._prefix in message.content:
                content = message.content.lower()
                en_to_ru = {
                    'a': 'а', 'c': 'с',
                    'e': 'е', 'p': 'р',
                    't': 'т'
                }

                for en, ru in en_to_ru.items():
                    content = ''.join(c[0] for c in itertools.groupby(content.replace(ru, en)))
                if 'acept' in content:
                    self.accept(message)

    @commands.command(
        name='omgroulette',
        cooldown={'per': 0, 'gen': 35},
        description='Рулетка с неограниченным количеством участников.'
    )
    async def omgroulette(self, ctx):
        if not ctx.channel.bot_is_mod:
            await ctx.reply('Боту необходима модерка для работы этой команды')
            return
        if ctx.channel.name in self.omgroulettes:
            return

        self.members[ctx.channel.name] = []
        self.omgroulettes.add(ctx.channel.name)

        smile = self.bot.smile(ctx, '', 'pog')
        await ctx.send(f'Смертельная рулетка началась {smile} Чтобы участвовать, напишите {self.bot._prefix}accept')
        await asyncio.sleep(30)

        if not self.members[ctx.channel.name]:
            smile = self.bot.smile(ctx, [['Lois', 'ThumbUp', 'BloodTrail']], 'bruh')
            await ctx.send(f'Никто не принял участия в рулетке {smile}')
            self.omgroulettes.remove(ctx.channel.name)
            del self.members[ctx.channel.name]
            return

        smile = self.bot.smile(ctx, '', 'meltdown')
        await ctx.send(f'Рулетка крутится... {smile}')
        await asyncio.sleep(randint(4, 6))

        looser = choice(self.members[ctx.channel.name])
        smile = self.bot.smile(ctx, '', 'rip', 'sad')
        await ctx.send(f'{looser} проигрывает в рулетке {smile}')
        await ctx.send(f'/timeout {looser} 600 Проигрыш в рулетке')
        self.omgroulettes.remove(ctx.channel.name)
        del self.members[ctx.channel.name]

    def accept(self, message):
        if message.channel.name in self.omgroulettes and message.author.name not in [member.lower() for member in self.members[message.channel.name]]:
            name = message.author.display_name

            if name.lower() != message.author.name:
                name = message.author.name

            self.members[message.channel.name].append(name)


def prepare(bot):
    bot.add_cog(Omgroulette(bot))
