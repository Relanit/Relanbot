import asyncio
import time
from twitchio.ext import commands, routines
from config import db


class Link(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.links = {}
        self.cooldowns = {}
        self.get_links.start()

    @commands.Cog.event()
    async def event_message(self, message):
        if message.echo:
            return

        content = message.content
        if 'reply-parent-msg-id' in message.tags:
            content = message.content.split(' ', 1)[1]

        if content.startswith(self.bot._prefix):
            content = content.lstrip(self.bot._prefix)
            if not content:
                return

            command = content.split(maxsplit=1)[0].lower()

            if command in self.links.get(message.channel.name, []):
                future = await db.links.find_one({'channel': message.channel.name})
                text = future['links'][command]

                if message.author.is_mod:
                    content = ' '.join(content.split()[1:3])
                    num = 1
                    announce = False

                    if 'a' in content or 'а' in content:
                        announce = True
                        content = content.replace('a', ' ').replace('а', ' ').strip(' ')

                    if announce:
                        text = f'/announce {text}'

                    if content:
                        try:
                            num = min(int(content.split(maxsplit=1)[0]), 15)
                        except ValueError:
                            num = 1

                    for i in range(num):
                        await message.channel.send(text)
                        await asyncio.sleep(0.1)
                elif time.time() > self.cooldowns[message.channel.name].get(command, 0):
                    ctx = await self.bot.get_context(message)
                    await ctx.reply(text)
                    self.cooldowns[message.channel.name][command] = time.time() + 2.5

    @commands.command(
        name='link',
        aliases=['links', 'dellink'],
        cooldown={'per': 0, 'gen': 5},
        description='Создание кастомных команд-ссылок. {prefix}links - список ссылок, {prefix}link [имя] [текст] - создание/изменение ссылки, {prefix}dellink [имя] - удаление ссылки, {prefix}имя a - ссылка с announce. ',
        flags=['moderator', 'whitelist']
    )
    async def link(self, ctx):
        if not ctx.channel.bot_is_vip and not ctx.channel.bot_is_mod:
            await ctx.reply('Боту необходима випка или модерка для работы этой команды')
            return
        if ctx.command_alias == f'links':
            if self.links.get(ctx.channel.name, None):
                message = f'Доступные ссылки: {self.bot._prefix}{str(" " + self.bot._prefix).join(self.links[ctx.channel.name])}'
                await ctx.reply(message)
            else:
                await ctx.reply('На вашем канале ещё нет ссылок')
            return

        content = ctx.content.split()

        if ctx.command_alias == f'dellink':
            if not content:
                await ctx.reply(f'Пустой ввод - {self.bot._prefix}help link')
                return

            link = content[0].lower()
            if ctx.channel.name in self.links and link in self.links[ctx.channel.name]:
                values = {'$unset': {f'links.{link}': ''}}
                self.links[ctx.channel.name].remove(link)
                self.cooldowns[ctx.channel.name].pop(link, None)
                message = f'Удалено {self.bot._prefix}{link}'
            else:
                await ctx.reply('Несуществующая ссылка')
                return
        else:
            if len(content) < 2:
                await ctx.reply(f'Пустой ввод - {self.bot._prefix}help link')
                return
            elif len(self.links[ctx.channel.name]) == 40:
                await ctx.reply('Максимальное количество ссылок - 40')
                return

            link_name = content[0].lower().lstrip(self.bot._prefix)
            link_text = ' '.join(content[1:]).lstrip('/. ')
            values = {'$setOnInsert': {'channel': ctx.channel.name},
                      '$set': {f'links.{link_name}': link_text}}

            if self.bot.get_command_name(link_name) or link_name in ['play', 'stop', 'acduel', 'accept']:
                await ctx.reply('Нельзя создать ссылку с таким названием')
                return
            elif '.' in link_name or '$' in link_name:
                await ctx.reply('Нельзя создать ссылку с точкой или $ в названии')
                return
            elif len(link_name) > 15:
                await ctx.reply('Нельзя создать ссылку с названием длиной более 15 символов')
                return

            if ctx.channel.name in self.links:
                if link_name in self.links[ctx.channel.name]:
                    message = f'Изменено {self.bot._prefix}{link_name}'
                else:
                    message = f'Добавлено {self.bot._prefix}{link_name}'
                    self.links[ctx.channel.name].add(link_name)
            else:
                message = f'Добавлено {self.bot._prefix}{link_name}'
                self.links[ctx.channel.name] = {link_name}

        await db.links.update_one({'channel': ctx.channel.name}, values, upsert=True)
        await ctx.reply(message)

    @routines.routine(iterations=1)
    async def get_links(self):
        async for document in db.links.find():
            self.links[document['channel']] = set(document['links'].keys())
            self.cooldowns[document['channel']] = {}


def prepare(bot):
    bot.add_cog(Link(bot))
