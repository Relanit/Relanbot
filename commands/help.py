from twitchio.ext import commands

from config import db


class Help(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='help',
        aliases=['commands'],
        cooldown={'per': 5, 'gen': 0},
        description='Эта команда.'
    )
    async def help(self, ctx):
        content = ctx.content.lstrip(self.bot._prefix).lower()
        if not content:
            smile = self.bot.smile(ctx, [['PepoG', 'NOTED'], ['📚']])
            message = f'{smile} Доступные команды - https://pastebin.com/wTD5z2AQ | ' \
                      f'Напишите {self.bot._prefix}help [команда], чтобы узнать описание команды'
            await ctx.reply(message)
            return

        command = self.bot.get_command_name(content.split()[0])
        if not command:
            await ctx.reply('Несуществующая команда')
            return

        data = self.bot.get_command(command)
        if 'admin' in data.flags:
            await ctx.reply('Несуществующая команда')
            return

        aliases = ''
        if data.aliases:
            aliases = f'({self.bot._prefix}{str(", " + self.bot._prefix).join(data.aliases)})'

        cooldowns = await db.cooldowns.find_one({'channel': ctx.channel.name})
        if cooldowns and 'whitelist' not in data.flags:

            if command in cooldowns['commands']:
                if 'offline' in cooldowns['commands'][command]:
                    offline = {
                        'per': cooldowns['commands'][command]['offline']['per'],
                        'gen': cooldowns['commands'][command]['offline']['gen']
                    }
                else:
                    mul_offline = cooldowns['mul_offline']
                    offline = {
                        'per': max(cooldowns['min_offline']['per'], data.cooldown['per'] * mul_offline),
                        'gen': max(cooldowns['min_offline']['gen'], data.cooldown['gen'] * mul_offline)
                    }
                if 'online' in cooldowns['commands'][command]:
                    online = {
                        'per': cooldowns['commands'][command]['online']['per'],
                        'gen': cooldowns['commands'][command]['online']['gen']
                    }
                else:
                    mul_online = cooldowns['mul_online']
                    online = {
                        'per': max(cooldowns['min_online']['per'], data.cooldown['per'] * mul_online),
                        'gen': max(cooldowns['min_online']['gen'], data.cooldown['gen'] * mul_online)
                    }
            else:
                mul_offline = cooldowns['mul_offline']
                mul_online = cooldowns['mul_online']
                offline = {
                    'per': max(cooldowns['min_offline']['per'], data.cooldown['per'] * mul_offline),
                    'gen': max(cooldowns['min_offline']['gen'], data.cooldown['gen'] * mul_offline)
                }
                online = {
                    'per': max(cooldowns['min_online']['per'], data.cooldown['per'] * mul_online),
                    'gen': max(cooldowns['min_online']['gen'], data.cooldown['gen'] * mul_online)
                }
        else:
            offline = data.cooldown
            online = data.cooldown

        offline_per = offline['per']
        offline_gen = offline['gen']
        online_per = online['per']
        online_gen = online['gen']

        if offline_per and offline_gen and offline == online:
            cooldown = f'личный {offline_per}с, общий {offline_gen}с.'
        elif offline_per and offline == online:
            cooldown = f'личный {offline_per}с.'
        elif offline_gen and offline == online:
            cooldown = f'общий {offline_gen}с.'
        elif offline_per and offline_gen and online_per and online_gen:
            cooldown = f'личный {offline_per}с, общий {offline_gen}с (на стриме: {online_per}с, {online_gen}с соответственно).'
        elif offline_per and offline_gen and online_per:
            cooldown = f'личный {offline_per}с, общий {offline_gen}с (на стриме: личный {online_per}с).'
        elif offline_per and offline_gen and online_gen:
            cooldown = f'личный {offline_per}с, общий {offline_gen}с (на стриме: общий {online_gen}с).'
        elif offline_per and online_per and online_gen:
            cooldown = f'личный {offline_per}с (на стриме: личный {online_per}с, общий {online_gen}с).'
        elif offline_gen and online_per and online_gen:
            cooldown = f'общий {offline_gen}с (на стриме: личный {online_per}с, общий {online_gen}с).'
        elif offline_per and online_per and offline_per != online_per:
            cooldown = f'личный {offline_per}с (на стриме: личный {online_per}с).'
        elif offline_gen and online_gen and offline_gen != online_gen:
            cooldown = f'общий {offline_gen}с (на стриме: общий {online_gen}с).'
        elif offline_per:
            cooldown = f'личный {offline_per}с'
        else:
            cooldown = f'общий {offline_gen}с'

        for_who = ''
        if 'moderator' in data.flags and 'trusted' in data.flags:
            for_who = 'Для модераторов и доверенных пользователей.'
        elif 'moderator' in data.flags:
            for_who = 'Для модераторов.'

        message = f'{self.bot._prefix}{command}{":" if not aliases else " " + aliases + ":"} ' \
                  f'{data.description.format(prefix=self.bot._prefix)} {for_who} ' \
                  f'Кд: {cooldown}'

        await ctx.reply(message)


def prepare(bot):
    bot.add_cog(Help(bot))
