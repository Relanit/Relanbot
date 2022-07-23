import asyncio
from random import choice, shuffle, randint, randrange

from twitchio.ext import commands


class Marbles(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.games = set()
        self.prepare = set()
        self.active = set()
        self.members = {}
        self.prepare_duration = 25
        self.game_duration = 30

    @commands.Cog.event()
    async def event_message(self, message):
        if message.echo:
            return

        if message.channel.name in self.games:
            if message.content.startswith(self.bot._prefix):
                content = message.content.lstrip(self.bot._prefix)
                if not content:
                    return

                command = content.split()[0].lower()
                if command == 'play':
                    self.play(message)
                elif command == 'stop':
                    await self.stop(message)

    @commands.command(
        name='marbles',
        aliases=['шары'],
        cooldown={'per': 0, 'gen': 60},
        description='Аналог Marbles on Stream, {prefix}stop для отмены игры.',
        flags=['moderator', 'trusted']
    )
    async def marbles(self, ctx):
        if ctx.channel.name not in self.games:
            self.games.add(ctx.channel.name)
            await self.start_prepare(ctx)
            self.games.remove(ctx.channel.name)
            del self.members[ctx.channel.name]

    async def start_prepare(self, ctx):
        self.prepare.add(ctx.channel.name)
        self.members[ctx.channel.name] = []
        smile1 = self.bot.smile(ctx, [['OFFLINECHAT']])
        smile2 = self.bot.smile(ctx, '', 'verypog')
        await ctx.send(f'{smile1} Добро пожаловать в Marbles on Offlinechat! Чтобы принять участие, напишите команду {self.bot._prefix}play {smile2}')

        for i in range(self.prepare_duration):
            if ctx.channel.name in self.prepare:
                await asyncio.sleep(1)
            else:
                return

        self.prepare.remove(ctx.channel.name)
        if len(self.members[ctx.channel.name]) == 0:
            smile = self.bot.smile(ctx, [['Lois', 'ThumbUp', 'BloodTrail']], 'bruh')
            await ctx.send(f'Никто не принял участия {smile}')
        elif len(self.members[ctx.channel.name]) == 1:
            smile = self.bot.smile(ctx, [['Lois', 'ThumbUp', 'BloodTrail']])
            await ctx.send(f'Никто не принял участия, кроме {self.members[ctx.channel.name][0]} {smile}')
        else:
            await self.start(ctx)

    async def start(self, ctx):
        self.active.add(ctx.channel.name)
        shuffle(self.members[ctx.channel.name])
        smile = self.bot.smile(ctx, '', 'pog', 'ez')
        await ctx.send(f'Игра началась! Лидирует {self.members[ctx.channel.name][-1]} {smile}')

        map1 = [1, 1, 1, 1, 1, 1, 1, 1, 1, 2]
        map2 = [1, 1, 1, 1, 1, 1, 1, 1, 2, 2]
        map3 = [1, 1, 1, 1, 1, 1, 1, 2, 2, 2]
        final_map = choice([map1, map2, map3])
        game_duration = 0
        await asyncio.sleep(randint(3, 6))

        while ctx.channel.name in self.active:
            event_id = choice(final_map)
            if event_id == 1:
                await self.overtake(ctx)
            else:
                await self.kick(ctx)

            if len(self.members[ctx.channel.name]) == 0:
                await asyncio.sleep(1)
                smile = self.bot.smile(ctx, [['Lois', 'ThumbUp', 'BloodTrail']])
                await ctx.send(f'Все игроки вылетели {smile}')
                self.active.remove(ctx.channel.name)
            elif game_duration >= self.game_duration:
                winner = self.members[ctx.channel.name][-1]
                await asyncio.sleep(1)
                smile1 = self.bot.smile(ctx, '', 'ez')
                smile2 = self.bot.smile(ctx, [['sDR', 'EZ Clap', 'peepoClap', 'PeepoClap']])
                await ctx.send(f'{smile1} Победитель - {winner}! Поздравляем {smile2}')
                self.active.remove(ctx.channel.name)

            event_interval = randint(3, 6)
            game_duration += event_interval
            await asyncio.sleep(event_interval)

    async def overtake(self, ctx):
        if len(self.members[ctx.channel.name]) == 1:
            pass
        else:
            if len(self.members[ctx.channel.name]) < 7 or choice([1, 2]) > 1:
                player1 = randrange(len(self.members[ctx.channel.name]))
                player2 = randrange(len(self.members[ctx.channel.name]))
                while player1 == player2:
                    player2 = randrange(len(self.members[ctx.channel.name]))
            else:
                player1 = randrange(len(self.members[ctx.channel.name]) - 3, len(self.members[ctx.channel.name]))
                player2 = randrange(len(self.members[ctx.channel.name]) - 3, len(self.members[ctx.channel.name]))
                while player1 == player2:
                    player2 = randrange(len(self.members[ctx.channel.name]) - 3, len(self.members[ctx.channel.name]))

            self.members[ctx.channel.name][player1], self.members[ctx.channel.name][player2] = \
                self.members[ctx.channel.name][player2], self.members[ctx.channel.name][player1]

            if player1 > player2:
                first = self.members[ctx.channel.name][player1]
                second = self.members[ctx.channel.name][player2]
            else:
                first = self.members[ctx.channel.name][player2]
                second = self.members[ctx.channel.name][player1]

            leader = self.members[ctx.channel.name][-1]
            smile1 = self.bot.smile(ctx, '', 'ez', 'pog')
            smile2 = self.bot.smile(ctx, '', 'ez', 'pog')
            await ctx.send(f'{smile1} {first} обогнал(а) {second}, Лидирует {leader}! {smile2}')

    async def kick(self, ctx):
        if len(self.members[ctx.channel.name]) != 1:
            player = randrange(len(self.members[ctx.channel.name]) - 1)
            name = self.members[ctx.channel.name][player]
            del self.members[ctx.channel.name][player]
            leader = self.members[ctx.channel.name][-1]
            smile1 = self.bot.smile(ctx, [['Lois', 'ThumbUp', 'BloodTrail']], 'sad', 'rip')
            smile2 = self.bot.smile(ctx, '', 'ez', 'pog')
            await ctx.send(f'{smile1} {name} вылетел(а) за пределы карты. Лидирует {leader} {smile2}')
        else:
            user = self.members[ctx.channel.name][0]
            del self.members[ctx.channel.name][0]
            smile = self.bot.smile(ctx, [['Lois', 'ThumbUp', 'BloodTrail']], 'sad', 'rip')
            await ctx.send(f'{smile} {user} вылетел(а) за пределы карты')

    def play(self, message):
        if message.channel.name in self.prepare and message.author.name not in [member.lower() for member in self.members[message.channel.name]]:
            name = message.author.display_name

            if name.lower() != message.author.name:
                name = message.author.name

            self.members[message.channel.name].append(name)

    async def stop(self, message):
        if message.author.is_mod or message.author.name in self.bot.trusted_users and message.channel.name in self.games:
            self.prepare.discard(message.channel.name)
            self.active.discard(message.channel.name)
            smile = self.bot.smile(message, [['Awkward', 'awkward']], 'verypog')
            await message.channel.send(f'Игра отменена {smile}')


def prepare(bot):
    bot.add_cog(Marbles(bot))
