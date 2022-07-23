import time
from config import db


class Cooldown:

    def __init__(self, channels):
        self.cooldowns = {}
        self.pause_ends = {}
        for channel in channels:
            self.cooldowns[channel] = {}
            self.pause_ends[channel] = {}

    async def handle_command(self, command, message, admin=False):
        now = time.time()
        data = self.get_command(command)

        channel = message.channel.name

        if not admin:
            user = message.author.name
            if 'moderator' and 'trusted' in data.flags:
                if not (message.author.is_mod or user in self.trusted_users):
                    return
            elif 'moderator' in data.flags:
                if not message.author.is_mod:
                    return
            elif 'trusted' in data.flags:
                if user not in self.trusted_users:
                    return
            elif 'admin' in data.flags:
                return

            if self.pause_ends[channel].get(command, 0) < now:
                if command in self.cooldowns[channel]:
                    if self.cooldowns[channel][command]['gen'] < now > self.cooldowns[channel][command]['per'].get(user, 0):
                        per, gen = await self.get_cooldown_end(command, channel, data)
                        if per - self.cooldowns[channel][command]['per'].get(user, 0) < 0.5 or gen - self.cooldowns[channel][command]['gen'] < 0.5:
                            return

                        self.cooldowns[channel][command]['per'][user], self.cooldowns[channel][command]['gen'] = per, gen
                        return True

                    return

                per_end, gen_end = await self.get_cooldown_end(command, channel, data)
                self.cooldowns[channel][command] = {'per': {user: per_end}, 'gen': gen_end}
                return True

            return

        if 'admin' in data.flags:
            return True

        if command in self.cooldowns[channel]:
            _, self.cooldowns[channel][command]['gen'] = await self.get_cooldown_end(command, channel, data)
            return True

        _, gen_end = await self.get_cooldown_end(command, channel, data)
        self.cooldowns[channel][command] = {'per': {}, 'gen': gen_end}
        return True

    async def get_cooldown_end(self, command, channel, data):
        if channel in self.streams:
            status = 'online'
        else:
            status = 'offline'

        cooldowns = await db.cooldowns.find_one({'channel': channel})

        if cooldowns and 'whitelist' not in data.flags:
            min_per = cooldowns[f'min_{status}']['per']
            min_gen = cooldowns[f'min_{status}']['gen']

            if command in cooldowns['commands']:
                if status in cooldowns['commands'][command]:
                    cooldown = {
                        'per': cooldowns['commands'][command][status]['per'],
                        'gen': cooldowns['commands'][command][status]['gen']
                    }
                else:
                    mul = cooldowns[f'mul_{status}']
                    cooldown = {
                        'per': max(min_per, data.cooldown['per'] * mul),
                        'gen': max(min_gen, data.cooldown['gen'] * mul)
                    }
            else:
                mul = cooldowns[f'mul_{status}']
                cooldown = {
                    'per': max(min_per, data.cooldown['per'] * mul),
                    'gen': max(min_gen, data.cooldown['gen'] * mul)
                }
        else:
            cooldown = data.cooldown

        now = time.time()
        per_end = now + cooldown['per']
        gen_end = now + cooldown['gen']
        return per_end, gen_end

    def set_pause(self, channel, command, minutes):
        pause_end = time.time() + minutes * 60

        if command == 'all':
            for command in self.commands.keys():
                flags = self.get_command(command).flags

                if 'whitelist' not in flags and 'admin' not in flags:
                    self.pause_ends[channel][command] = pause_end
        else:
            self.pause_ends[channel][command] = pause_end

    def unset_pause(self, channel, command):
        if command == 'all':
            self.pause_ends[channel].clear()
        else:
            self.pause_ends[channel].pop(command, None)

    def reset_cooldown(self, channel):
        self.unset_pause(channel, 'all')
        self.cooldowns[channel] = {}
