import asyncio
import os
from pathlib import Path
from datetime import datetime
from random import choice, sample

import aiohttp
from twitchio.ext import commands, routines

from utils.smiles import *
from config import db, CHANNELS
from cooldown import Cooldown


class SvinBot(commands.Bot, Cooldown):
    def __init__(self):
        super().__init__(token=os.getenv('TOKEN'), prefix='!', initial_channels=CHANNELS)
        self.admins = ['relanit', 'nelanit']
        self.trusted_users = ['nelanit', 'aroldas1', 'minoxysd', 'cantfindary']
        self.chatters = {}
        self.streams = set()
        self.blacklist = {'streamelements', 'moobot', 'nightbot', 'oldboty', 'watchstatsbot', 'supibot', 'okey_bot', 'donkboty'}
        self.global_smiles = set()
        self.channel_smiles = {}

        for channel in CHANNELS:
            self.chatters[channel] = {}

        for command in [path.stem for path in Path('commands').glob('*py')]:
            self.load_module(f'commands.{command}')

        self.check_streams.start(stop_on_error=False)
        self.update_smiles.start(stop_on_error=False)
        Cooldown.__init__(self, CHANNELS)

    async def event_ready(self):
        print(f'Logged in as {self.nick}')

    async def event_message(self, message):
        if message.echo or message.author.name == 'arrilsq':
            return

        if message.author.name not in self.blacklist:
            self.chatters[message.channel.name][message.author.name] = message.author.display_name

        content = message.content
        if 'reply-parent-msg-id' in message.tags:
            content = message.content.split(' ', 1)[1]

        if content.startswith(self._prefix):
            content = content.lstrip(self._prefix)
            if not content:
                return

            command = content.split(maxsplit=1)[0]
            command_lower = command.lower()

            if command_name := self.get_command_name(command_lower):
                message.content = message.content.replace(command, command_lower)
                if message.author.name in self.admins:
                    if await self.handle_command(command_name, message, admin=True):
                        await self.handle_commands(message)
                elif await self.handle_command(command_name, message):
                    await self.handle_commands(message)

    async def event_command_error(self, ctx, error):
        if type(error).__name__ == 'CommandNotFound':
            return

    @routines.routine(minutes=1.0, iterations=0)
    async def check_streams(self):
        channels = self.channels_names or CHANNELS
        streams = await self.fetch_streams(user_logins=channels)
        streams_db = {}

        async for stream_db in db.streams.find():
            streams_db[stream_db['channel']] = stream_db

        for channel in channels:
            stream = None

            for s in streams:
                if s.user.name.lower() == channel:
                    stream = s
                    break

            if stream:
                if channel not in streams_db:
                    start = str(stream.started_at.replace(tzinfo=None))
                    await db.streams.update_one({'channel': channel}, {'$setOnInsert': {'channel': channel},
                                                                       '$set': {'started_at': start,
                                                                                'viewer_counts': [stream.viewer_count],
                                                                                'game_name': stream.game_name,
                                                                                'game_started_at': start}}, upsert=True)
                    await db.streamstats.update_one({'channel': channel}, {'$setOnInsert': {'channel': channel},
                                                                           '$unset': {'stream_end': ''},
                                                                           '$set': {'total_messages': 0,
                                                                                    'stream_start': start,
                                                                                    'viewer_counts': [stream.viewer_count],
                                                                                    'users_stats': {},
                                                                                    'smiles_stats': {},
                                                                                    'users_smiles_stats': {}}}, upsert=True)
                elif streams_db[channel]['game_name'] != stream.game_name:
                    now = str(datetime.utcnow())
                    await db.streams.update_one({'channel': channel}, {'$set': {'game_name': stream.game_name,
                                                                                'game_started_at': now}})

                if channel in streams_db and stream.viewer_count not in streams_db[channel]['viewer_counts']:
                    await db.streams.update_one({'channel': channel},
                                                {'$push': {'viewer_counts': stream.viewer_count}})
                    await db.streamstats.update_one({'channel': channel},
                                                    {'$push': {'viewer_counts': stream.viewer_count}})

                if channel not in self.streams:
                    self.streams.add(channel)

                    if (data := await db.inspects.find_one({'channel': channel})) and data['active']:
                        await self.cogs['Inspect'].set(channel)

                if datetime.now().minute % 2 == 0:
                    self.clear_chatters(channel)
            else:
                if channel in streams_db:
                    await db.streams.delete_one({'channel': channel})
                    self.reset_cooldown(channel)
                    self.chatters[channel].clear()

                    if channel in self.streams:
                        self.streams.remove(channel)
                        stream_end = str(datetime.utcnow())

                        await db.streamstats.update_one({'channel': channel}, {'$set': {'stream_end': stream_end}})
                        await db.offlinestats.update_one({'channel': channel}, {'$setOnInsert': {'channel': channel},
                                                                                '$set': {'total_messages': 0,
                                                                                         'chatters': [],
                                                                                         'smiles_stats': {},
                                                                                         'users_smiles_stats': {}}}, upsert=True)

                        if (data := await db.inspects.find_one({'channel': channel})) and data['active']:
                            self.cogs['Inspect'].unset(channel)

                if not await db.offlinestats.find_one({'channel': channel}):
                    await db.offlinestats.update_one({'channel': channel}, {'$setOnInsert': {'channel': channel},
                                                                            '$set': {'total_messages': 0,
                                                                                     'chatters': [],
                                                                                     'smiles_stats': {},
                                                                                     'users_smiles_stats': {}}}, upsert=True)

                now = datetime.now()

                if now.minute % 30 == 0:
                    self.clear_chatters(channel)

    @routines.routine(minutes=15, iterations=0)
    async def update_smiles(self):
        channels = self.channels_names or CHANNELS
        broadcasters = await self.fetch_users(names=channels)
        twitch_smiles = [smile.name for smile in await self.fetch_global_emotes() if '.' not in smile.name and '\\' not in smile.name and '/' not in smile.name]
        async with aiohttp.ClientSession() as client:
            global_smiles = await get_global_smiles(client)
            self.global_smiles = set(twitch_smiles + global_smiles)

            for broadcaster in broadcasters:
                login = broadcaster.name.lower()
                bttv = await get_bttv(client, broadcaster.id)
                ffz = await get_ffz(client, broadcaster.id)
                stv = await get_7tv(client, login)
                sub = [smile.name for smile in await self.fetch_channel_emotes(broadcaster.id)]
                self.channel_smiles[login] = set(bttv + ffz + stv + sub)
                await asyncio.sleep(15)

    def clear_chatters(self, channel):
        length = len(self.chatters[channel])

        for i in self.chatters[channel].copy():
            del self.chatters[channel][i]

            if len(self.chatters[channel]) <= length / 2:
                break

    def random_chatter(self, ctx, allow_self=False, count=1):
        chatters = self.chatters[ctx.channel.name].copy()

        if len(chatters) > 1:
            if not allow_self:
                del chatters[ctx.author.name]

            if count == 1:
                chatter = choice(list(chatters.items()))

                if chatter[1].lower() != chatter[0]:
                    chatter = chatter[0]
                else:
                    chatter = chatter[1]
            else:
                chatter = []

                for user in sample(list(chatters.items()), count):
                    name = user[1]

                    if user[1].lower() != user[0]:
                        name = user[0]

                    chatter.append(name)
        else:
            chatter = ctx.author.display_name

            if chatter.lower() != ctx.author.name:
                chatter = ctx.author.name

        return chatter

    def smile(self, ctx, strict=None, *examples):
        smiles = set()
        default = set()

        def check_double_smiles(arr):
            nonlocal smiles
            for smile in arr:
                if ' ' in smile:
                    for s in smile.split():
                        if not self.smile(ctx, [[s], []]):
                            return
                    smiles |= {smile}

        if strict:
            check_double_smiles(strict[0])
            smiles |= set(strict[0]) & self.channel_smiles.get(ctx.channel.name, set()) | set(strict[0]) & self.global_smiles
            if not smiles:
                if len(strict) > 1 and strict[1] and '' not in strict[1]:
                    default |= set(strict[1])

        for example in examples:
            check_double_smiles(smile_examples[example]['channel'])
            smiles |= smile_examples[example]['channel'] & self.channel_smiles.get(ctx.channel.name, set())
            if not smiles:
                default |= smile_examples[example]['default']

        if not smiles:
            if not default:
                default.add('')
            smiles = default

        if smiles != {''}:
            return ' ' + choice(list(smiles)) + ' '
        else:
            return ''


bot = SvinBot()
bot.run()
