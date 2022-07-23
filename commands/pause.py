from twitchio.ext import commands


class Pause(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='pause',
        aliases=['unpause'],
        cooldown={'per': 0, 'gen': 5},
        description='Позволяет ставить паузу на все или указанную команды, с возможностью указания времени в минутах.',
        flags=['moderator', 'whitelist']
    )
    async def pause(self, ctx):
        content = ctx.content.lower().replace(self.bot._prefix, '')
        if ctx.command_alias == f'pause':
            if len(content.split()) == 1:
                try:
                    minutes = int(content)
                    if minutes > 600:
                        message = '❌ Максимальное время паузы 600 минут'
                    else:
                        self.bot.set_pause(ctx.channel.name, 'all', minutes)
                        message = f'⏸️ Пауза на {minutes} минут'
                except ValueError:
                    if not (command := self.bot.get_command_name(content)):
                        message = '❌ Несуществующая команда'
                    elif 'whitelist' not in (flags := self.bot.get_command(command).flags) and 'admin' not in flags:
                        minutes = 600
                        self.bot.set_pause(ctx.channel.name, command, minutes)
                        message = f'⏸️ Пауза для команды {command}'
                    elif 'admin' in flags:
                        message = '❌ Несуществующая команда'
                    else:
                        message = '❌ Эту команду нельзя поставить на паузу'
            elif len(content.split()) == 2:
                content = content.split()
                if not (command := self.bot.get_command_name(content[0])):
                    message = '❌ Несуществующая команда'
                elif 'whitelist' not in (flags := self.bot.get_command(command).flags) and 'admin' not in flags:
                    try:
                        minutes = int(content[1])
                        if minutes > 600:
                            message = '❌ Максимальное время паузы 600 минут'
                        else:
                            self.bot.set_pause(ctx.channel.name, command, minutes)
                            message = f'⏸️ Пауза для команды {command} на {minutes} минут'
                    except ValueError:
                        message = '❌ Ошибка'
                elif 'admin' in flags:
                    message = '❌ Несуществующая команда'
                else:
                    message = '❌ Эту команду нельзя поставить на паузу'
            else:
                minutes = 600
                self.bot.set_pause(ctx.channel.name, 'all', minutes)
                message = '⏸️ Пауза'
        else:
            if not content:
                self.bot.unset_pause(ctx.channel.name, 'all')
                message = '▶️ Пауза снята'
            else:
                if not (command := self.bot.get_command_name(content)):
                    message = '❌ Несуществующая команда'
                else:
                    self.bot.unset_pause(ctx.channel.name, command)
                    message = f'▶️ Снята пауза для команды {command}'

        await ctx.reply(message)


def prepare(bot):
    bot.add_cog(Pause(bot))
