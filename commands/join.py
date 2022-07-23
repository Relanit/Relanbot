from twitchio.ext import commands

from config import db


class JoinChannel(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='join',
        flags=['admin']
    )
    async def join_channel(self, ctx):
        channel = ctx.content.lower()
        user = await self.bot.fetch_users(names=[channel])
        if not user:
            await ctx.reply('❌ Несуществующий логин')
            return

        self.bot.chatters[channel] = {}
        self.bot.cooldowns[channel] = {}
        self.bot.pause_ends[channel] = {}
        await db.channels.update_one({'_id': 1}, {'$addToSet': {'channels': channel}})
        await self.bot.join_channels([channel])
        await ctx.reply('✅ Добавлен')


def prepare(bot):
    bot.add_cog(JoinChannel(bot))
