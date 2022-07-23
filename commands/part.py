from twitchio.ext import commands

from config import db


class PartChannel(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='part',
        flags=['admin']
    )
    async def part_channel(self, ctx):
        channel = ctx.content.lower()
        if not channel:
            channel = ctx.channel.name
        else:
            data = await db.channels.find_one({'_id': 1})
            channels = data['channels']
            if channel not in channels:
                await ctx.reply('❌ Канал не подключён')
                return

        self.bot.chatters.pop(channel, None)
        self.bot.cooldowns.pop(channel, None)
        self.bot.pause_ends.pop(channel, None)
        await db.channels.update_one({'_id': 1}, {'$pull': {'channels': channel}})
        await self.bot.part_channels([channel])
        await ctx.reply('✅ Удалён')


def prepare(bot):
    bot.add_cog(PartChannel(bot))
