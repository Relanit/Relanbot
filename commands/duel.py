import asyncio
from random import shuffle, randint, choice

from twitchio.ext import commands


class Duel(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.duels = set()
        self.prepare = {}
        self.members = {}
        self.smile = {}

    @commands.Cog.event()
    async def event_message(self, message):
        if message.echo:
            return

        if message.channel.name in self.prepare:
            if message.content.startswith(self.bot._prefix):
                content = message.content.lstrip(self.bot._prefix)
                if not content:
                    return

                command = content.split()[0].lower()
                if command == 'acduel':
                    self.acduel(message)

        if message.channel.name in self.smile:
            author = message.author.display_name

            if author.lower() != message.author.name:
                author = message.author.name

            if author in self.members[message.channel.name]:
                if self.smile[message.channel.name] in message.content:
                    del self.smile[message.channel.name]
                    i = self.members[message.channel.name].index(message.author.display_name)
                    del self.members[message.channel.name][i]
                    looser = ''.join(self.members[message.channel.name])
                    smile = self.bot.smile(message, '', 'sad', 'rip')
                    await message.channel.send(f'{author} убивает {looser} {smile}')
                    await message.channel.send(f'/timeout {looser} 60 {self.bot._prefix}duel')

    @commands.command(
        name='duel',
        aliases=['дуэль', 'sduel'],
        cooldown={'per': 0, 'gen': 10},
        description='Мутит одного из участников дуэли. {prefix}duel - рандомный мут, {prefix}sduel - дуэль на скорость отправки смайла.'
    )
    async def duel(self, ctx):
        if ctx.channel.bot_is_mod:
            await ctx.reply('Боту необходима модерка для работы этой команды')
            return
        if ctx.channel.name in self.duels:
            return

        user = ctx.content.strip('@')

        author = ctx.author.display_name
        if author.lower() != ctx.author.name:
            author = ctx.author.name

        if not user or user.lower() == ctx.author.name:
            smile = self.bot.smile(ctx, [['Durka', 'RoflanDurka']], 'rip', 'eblan')
            await ctx.send(f'{author} вызывает на дуэль самого себя и проигрывает {smile}')
            await ctx.send(f'/timeout {author} 60 Проигрыш в дуэли')
            return

        self.duels.add(ctx.channel.name)
        self.prepare[ctx.channel.name] = True
        self.members[ctx.channel.name] = [author, user]

        smile = self.bot.smile(ctx, '', 'ez')
        await ctx.send(f'{author} вызывает на дуэль {user} {smile} Чтобы принять вызов, напишите {self.bot._prefix}acduel')

        for i in range(200):
            await asyncio.sleep(0.1)

            if not self.prepare[ctx.channel.name]:
                break

        if not self.prepare[ctx.channel.name]:
            if ctx.command_alias == 'sduel':
                await self.sduel(ctx)
            else:
                smile1 = self.bot.smile(ctx, '', 'meltdown')
                smile2 = self.bot.smile(ctx, [['Stare', 'Starege', 'WEIRD']])
                await ctx.send(f'{smile1} Дуэлянты смотрят друг другу в глаза... {smile2}')
                await asyncio.sleep(randint(4, 10))

                shuffle(self.members[ctx.channel.name])
                looser = self.members[ctx.channel.name].pop()
                smile = self.bot.smile(ctx, '', 'sad', 'rip')
                await ctx.send(f'{self.members[ctx.channel.name][0]} убивает {looser} {smile}')
                await ctx.send(f'/timeout {looser} 60 Проигрыш в дуэли')
        else:
            smile = self.bot.smile(ctx, [['Lois', 'ThumbUp', 'BloodTrail']], 'bruh')
            await ctx.reply(f'Оппонент не принял дуэль {smile}')

        del self.prepare[ctx.channel.name]
        del self.members[ctx.channel.name]
        self.duels.remove(ctx.channel.name)

    def acduel(self, message):
        author = message.author.display_name

        if author.lower() != message.author.name:
            author = message.author.name

        if author.lower() == self.members[message.channel.name][1].lower():
            self.members[message.channel.name][1] = author
            self.prepare[message.channel.name] = False

    async def sduel(self, ctx):
        message = f'{" и ".join(self.members[ctx.channel.name])}, приготовьтесь! ' \
                  f'Чтобы атаковать, отправьте смайл, который я напишу в чат через несколько секунд. '
        await ctx.send(message)

        smiles = self.bot.channel_smiles[ctx.channel.name].copy()
        smiles |= self.bot.global_smiles
        self.smile[ctx.channel.name] = choice(list(smiles))
        await asyncio.sleep(randint(5, 7))

        await ctx.send(f'@{" @".join(self.members[ctx.channel.name])} пишите {self.smile[ctx.channel.name]} !')
        self.smile[ctx.channel.name] = self.smile[ctx.channel.name].lstrip(':')

        for i in range(100):
            await asyncio.sleep(0.1)

            if ctx.channel.name not in self.smile:
                break

        if ctx.channel.name in self.smile:
            del self.smile[ctx.channel.name]
            shuffle(self.members[ctx.channel.name])
            looser = self.members[ctx.channel.name].pop()
            smile = self.bot.smile(ctx, [['Zaebalo']], 'rip')
            await ctx.send(f'{looser} застрелился от безысходности {smile}')
            await ctx.send(f'/timeout {looser} 60 Проигрыш в дуэли')


def prepare(bot):
    bot.add_cog(Duel(bot))
