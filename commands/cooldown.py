from twitchio.ext import commands

from config import db


class Cooldown(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    """
    online - на стриме
    offline - в оффлайне

    число:число
    Первое число - личный кд (кд на использование команды одним человеком)
    Второе число - общий кд (кд на использование команды всем чатом)

    !cd set [команда] [число:число] - установка кд для отдельной команды
    !cd set [команда] [число:число] online - установка кд команды на стриме
    !cd set [команда] [число:число] offline - установка кд команды в оффлайне

    !cd reset - сброс настроек кд
    !cd reset online - сброс кд на стриме
    !cd reset offline - сброс кд в оффлайне
    !cd reset min - сброс минимального кд
    !cd reset min online - сброс минимального кд на стриме
    !cd reset min offline - сброс минимального кд в оффлайне
    !cd reset [команда] - сброс кд команды
    !cd reset [команда] online - сброс кд команды на стриме
    !cd reset [команда] offline - сброс кд команды в оффлайне

    !cd mul [число] - умножить кд на число
    !cd mul [число] online - умножить кд на стриме
    !cd mul [число] offline - умножить кд в оффлайне
    !cd mul [число] [команда] - умножить кд команды на число
    !cd mul [число] [команда] online - умножить кд команды на стриме
    !cd mul [число] [команда] offline - умножить кд команды в оффлайне
    умножение идёт от кд по умолчанию

    !cd min [число:число] - установка минимального кд
    !cd min [число:число] online - установка минимального кд на стриме
    !cd min [число:число] offline - установка минимального кд в оффлайне

    """

    @commands.command(
        name='cooldown',
        aliases=['cd'],
        cooldown={'per': 0, 'gen': 5},
        description='Позволяет редактировать кд. Полное описание: https://i.imgur.com/6z4fomf.png',
        flags=['moderator', 'whitelist']
    )
    async def edit_cooldown(self, ctx):
        content = ctx.content.lower().split()
        if len(content) < 1:
            ctx.reply(f'Неверная запись команды, {self.bot._prefix}help cd')
            return

        await db.cooldowns.update_one({'channel': ctx.channel.name}, {
            '$setOnInsert': {
                'channel': ctx.channel.name,
                'mul_offline': 1,
                'mul_online': 1,
                'min_offline': {
                    'per': 0,
                    'gen': 0
                },
                'min_online': {
                    'per': 0,
                    'gen': 0
                },
                'commands': {}
            }
        }, upsert=True)

        if content[0] == 'set':
            if not 3 <= len(content) <= 4:
                await ctx.reply(f'Неверная запись команды, {self.bot._prefix}help cd')
                return

            if not (command := self.bot.get_command_name(content[1])):
                await ctx.reply('Несуществующая команда')
                return

            data = self.bot.get_command(command)
            if 'whitelist' in data.flags:
                await ctx.reply('Для этой команды запрещено редактирование кд')
                return
            elif 'admin' in data.flags:
                await ctx.reply('Несуществующая команда')
                return

            try:
                per, gen = map(int, content[2].split(':'))
            except ValueError:
                await ctx.reply(f'Неверная запись команды, {self.bot._prefix}help cd')
                return

            default = data.cooldown
            if per < default['per'] and gen < default['per'] or gen < default['gen']:
                await ctx.reply(
                    f'Кд не может быть меньше стандартного: Личный {default["per"]}с, общий {default["gen"]}с.')
                return
            elif per > 3600 or gen > 3600:
                await ctx.reply(f'Кд не может быть больше 1 часа')
                return

            if len(content) == 3:
                values = {
                    f'commands.{command}': {
                        'offline': {
                            'per': per,
                            'gen': gen
                        },
                        'online': {
                            'per': per,
                            'gen': gen
                        }
                    }
                }
            else:
                status = content[3]

                if status not in ('offline', 'online'):
                    await ctx.reply(f'Неверный статус (offline или online), {self.bot._prefix}help cd')
                    return

                values = {
                    f'commands.{command}.{status}': {
                        'per': per,
                        'gen': gen
                    }
                }
        elif content[0] == 'reset':
            if not 1 <= len(content) <= 3:
                await ctx.reply(f'Неверная запись команды, {self.bot._prefix}help cd')
                return

            if len(content) == 1:
                values = {
                    'commands': {},
                    'mul_offline': 1,
                    'mul_online': 1,
                    'min_offline': {
                        'per': 0,
                        'gen': 0
                    },
                    'min_online': {
                        'per': 0,
                        'gen': 0
                    }
                }
            elif len(content) == 2:
                if content[1] in ('offline', 'online'):
                    data = await db.cooldowns.find_one({'channel': ctx.channel.name})

                    for command in data['commands'].copy():
                        data['commands'][command].pop(content[1], None)
                        if not data['commands'][command]:
                            del data['commands'][command]

                    values = {
                        'commands': data['commands'],
                        f'mul_{content[1]}': 1,
                        f'min_{content[1]}': {
                            'per': 0,
                            'gen': 0
                        }
                    }
                elif content[1] == 'min':
                    values = {
                        'min_offline': {
                            'per': 0,
                            'gen': 0
                        },
                        'min_online': {
                            'per': 0,
                            'gen': 0
                        }
                    }
                elif command := self.bot.get_command_name(content[1]):
                    default = self.bot.get_command(command).cooldown
                    values = {
                        f'commands.{command}': {
                            'offline': default,
                            'online': default
                        }
                    }
                else:
                    await ctx.reply(f'Неверный статус (offline или online) или указана несуществующая команда, {self.bot._prefix}help cd')
                    return
            elif command := self.bot.get_command_name(content[1]):
                status = content[2]
                if status not in ('offline', 'online'):
                    await ctx.reply(f'Неверный статус (offline или online), {self.bot._prefix}help cd')
                    return

                default = self.bot.get_command(command).cooldown
                values = {
                    f'commands.{command}.{status}': default
                }
            elif content[1] == 'min':
                status = content[2]
                if status not in ('offline', 'online'):
                    await ctx.reply(f'Неверный статус (offline или online), {self.bot._prefix}help cd')
                    return

                values = {
                    f'min_{status}': {
                        'per': 0,
                        'gen': 0
                    }
                }
            else:
                await ctx.reply(
                    f'Неверная запись команды или указана несуществующая команда, {self.bot._prefix}help cd')
                return
        elif content[0] == 'mul':
            if not 2 <= len(content) <= 4:
                await ctx.reply(f'Неверная запись команды, {self.bot._prefix}help cd')
                return

            try:
                mul = int(content[1])
            except ValueError:
                await ctx.reply('Множитель должен быть целым числом')
                return

            if not 1 <= mul <= 10:
                await ctx.reply('Множитель не должен быть меньше 1 и больше 10')
                return

            if len(content) == 2:
                values = {
                    'mul_offline': mul,
                    'mul_online': mul,
                    'commands': {}
                }
            elif content[2] in ('offline', 'online'):
                data = await db.cooldowns.find_one({'channel': ctx.channel.name})

                for command in data['commands'].copy():
                    data['commands'][command].pop(content[2], None)
                    if not data['commands'][command]:
                        del data['commands'][command]

                values = {
                    'commands': data['commands'],
                    f'mul_{content[2]}': mul
                }
            elif command := self.bot.get_command_name(content[2]):
                data = self.bot.get_command(command)
                if 'whitelist' in data.flags:
                    await ctx.reply('Для этой команды запрещено редактирование кд')
                    return
                elif 'admin' in data.flags:
                    await ctx.reply('Несуществующая команда')
                    return

                default = data.cooldown
                per = default['per'] * mul
                gen = default['gen'] * mul

                if len(content) == 3:
                    values = {
                        f'commands.{command}': {
                            'offline': {
                                'per': per,
                                'gen': gen
                            },
                            'online': {
                                'per': per,
                                'gen': gen
                            }
                        }
                    }
                elif content[3] in ('offline', 'online'):
                    values = {
                        f'commands.{command}.{content[3]}': {
                            'per': per,
                            'gen': gen
                        }
                    }
                else:
                    await ctx.reply(f'Неверная запись команды, {self.bot._prefix}help cd')
                    return
            else:
                await ctx.reply('Несуществующая команда')
                return
        elif content[0] == 'min':
            if not 2 <= len(content) <= 3:
                await ctx.reply(f'Неверная запись команды, {self.bot._prefix}help cd')
                return

            try:
                per, gen = map(int, content[1].split(':'))
            except ValueError:
                await ctx.reply(f'Неверная запись кд, {self.bot._prefix}help cd')
                return

            if per < 0 or gen < 0:
                await ctx.reply(f'Неверная запись кд, {self.bot._prefix}help cd')
                return

            if len(content) == 2:
                data = await db.cooldowns.find_one({'channel': ctx.channel.name})

                for command in data['commands'].copy():
                    if 'offline' in data['commands'][command]:
                        if data['commands'][command]['offline']['per'] < per or data['commands'][command]['offline']['gen'] < gen:
                            data['commands'][command].pop('offline')
                    if 'online' in data['commands'][command]:
                        if data['commands'][command]['online']['per'] < per or data['commands'][command]['online']['gen'] < gen:
                            data['commands'][command].pop('online')
                    if not data['commands'][command]:
                        data['commands'].pop(command)

                values = {
                    'min_offline': {
                        'per': per,
                        'gen': gen
                    },
                    'min_online': {
                        'per': per,
                        'gen': gen
                    },
                    'commands': data['commands']
                }
            elif content[2] in ('offline', 'online'):
                data = await db.cooldowns.find_one({'channel': ctx.channel.name})

                for command in data['commands']:
                    if content[2] in data['commands'][command]:
                        if data['commands'][command][content[2]]['per'] < per:
                            data['commands'][command][content[2]]['per'] = per
                        if data['commands'][command][content[2]]['gen'] < gen:
                            data['commands'][command][content[2]]['gen'] = gen

                values = {
                    f'min_{content[2]}': {
                        'per': per,
                        'gen': gen
                    },
                    'commands': data['commands']
                }
            else:
                await ctx.reply(f'Неверная запись статуса (offline или online), {self.bot._prefix}help cd')
                return
        else:
            await ctx.reply(f'Неверная запись команды, {self.bot._prefix}help cd')
            return

        await db.cooldowns.update_one({'channel': ctx.channel.name}, {'$set': values})
        await ctx.reply('✅ Готово')


def prepare(bot):
    bot.add_cog(Cooldown(bot))
