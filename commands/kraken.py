import asyncio
from random import randint

from twitchio.ext import commands

from config import db


class Kraken(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.krakens = set()
        self.number = {}
        self.members = {}
        self.smile = {}

    @commands.Cog.event()
    async def event_message(self, message):
        if message.echo:
            return

        if message.channel.name in self.krakens:
            author = message.author.display_name

            if author.lower() != message.author.name:
                author = message.author.name

            if self.members[message.channel.name].get(author) == 0:
                count = message.content.split().count(self.smile[message.channel.name])

                if 0 < count < 6:
                    self.members[message.channel.name][author] = count

    @commands.command(
        name='kraken',
        aliases=['кракен'],
        cooldown={'per': 0, 'gen': 120},
        description='Выпускает в чат кракена, который может утащить с собой до 5 человек.'
    )
    async def kraken(self, ctx):
        if not ctx.channel.bot_is_mod:
            await ctx.reply('Боту необходима модерка для работы этой команды')
            return
        if ctx.channel.name in self.krakens:
            return

        chatters = self.bot.chatters[ctx.channel.name]
        game = randint(1, 2)

        if game == 1 and len(chatters) >= (number := randint(3, 5)):
            self.krakens.add(ctx.channel.name)
            self.members[ctx.channel.name] = {}

            for chatter in self.bot.random_chatter(ctx, allow_self=True, count=number):
                self.members[ctx.channel.name][chatter] = 0

            smile1 = self.smile[ctx.channel.name] = self.bot.smile(ctx, [['PeepoRunCry', 'papichRun'], ['BibleThump']]).strip()
            smile2 = self.bot.smile(ctx, [['polarExtreme'], ['Squid2 Squid3']])
            message = f'Кракен начинает охоту за {", ".join(self.members[ctx.channel.name])}! ' \
                      f'Чтобы попробовать сбежать, отправьте от 1 до 5 смайлов {smile1} в чат, принимается только первый вариант. ' \
                      f'У вас ровно одна минута, время пошло! Бегите, глупцы! Squid1 {smile2} Squid4'

            await ctx.send(message)
            await asyncio.sleep(60)

            survivors = []
            self.number[ctx.channel.name] = randint(1, 5)
            for member in self.members[ctx.channel.name].copy():
                if self.members[ctx.channel.name][member] == self.number[ctx.channel.name] or ctx.channel.get_chatter(member).is_mod:
                    survivors.append(member)
                    del self.members[ctx.channel.name][member]

            if len(self.members[ctx.channel.name]) != 0:
                future = await db.lives.find_one_and_update({'_id': 1},
                                                            {'$inc': {'lives': len(self.members[ctx.channel.name])}},
                                                            new=True)
                lives = future['lives']

                smile1 = self.bot.smile(ctx, [['peepoRIP', 'Deadge'], ['⚰', '💀']])
                smile2 = self.bot.smile(ctx, [['Deadge', 'roflanPominy', 'BloodTrail']])
                if len(survivors) == 0:
                    message = f'Никому не удалось спастись! WeirdChamping Погибшие: {f"{smile1} " * number} ' \
                              f'{", ".join(self.members[ctx.channel.name])} | Кракен забрал уже {lives} жизней {smile2}'
                elif len(survivors) == 1:
                    message = f'{survivors[0]} выживает! WeirdChamping Погибшие: {f"{smile1} " * (number - 1)}' \
                              f'{", ".join(self.members[ctx.channel.name])} | Кракен забрал уже {lives} жизней {smile2}'
                elif len(survivors) == number - 1:
                    message = f'{", ".join(survivors)} выживают! WeirdChamping Погибший: {smile1} " ' \
                              f'{self.members[ctx.channel.name][0]} | Кракен забрал уже {lives} жизней {smile2}'
                else:
                    message = f'{", ".join(survivors)} выживают! WeirdChamping Погибшие: ' \
                              f'{f"{smile1} " * (number - len(survivors))} {", ".join(self.members[ctx.channel.name])} | ' \
                              f'Кракен забрал уже {lives} жизней {smile2}'

                await ctx.send(message)
                smile1 = self.bot.smile(ctx, [['polarExtreme'], ['Squid3']])
                smile2 = self.bot.smile(ctx, [['PeepoRunCry'], ['BibleThump']])
                await ctx.send(f'Кракен ждёт новых жертв... {smile1} {smile2}')

                for user in self.members[ctx.channel.name]:
                    await ctx.send(f'/timeout {user} 30 Выбор кракена пал на тебя!')
            else:
                smile = self.bot.smile(ctx, [['polarExtreme'], ['Squid2 Squid3']])
                await ctx.send(f'Squid1 {smile} Squid2 Великий Кракен всех пощадил.')

            self.krakens.remove(ctx.channel.name)
            del self.number[ctx.channel.name]
            del self.members[ctx.channel.name]
            return

        user = self.bot.random_chatter(ctx, allow_self=True)
        if ctx.channel.get_chatter(user).is_mod:
            await ctx.send(f'Могущество {user} слишком велико даже для Великого Кракена!')
            return

        future = await db.lives.find_one_and_update({'_id': 1}, {'$inc': {'lives': 1}}, new=True)
        lives = future['lives']
        smile1 = self.bot.smile(ctx, [['polarExtreme'], ['Squid2 Squid3']])
        smile2 = self.bot.smile(ctx, [['Deadge', 'roflanPominy', 'BloodTrail']])
        message = f'Squid1 {smile1} Squid4 Великий Кракен выбрал тебя, {user}, чтобы утащить в бездну! | Кракен забрал уже {lives} жизней {smile2}'
        await ctx.send(message)
        await ctx.send(f'/timeout {user} 30 Выбор кракена пал на тебя!')


def prepare(bot):
    bot.add_cog(Kraken(bot))
