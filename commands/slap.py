import traceback
from random import choice, randint

from twitchio.ext import commands

from utils.misc import read_file


class Slap(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='slap',
        aliases=['do'],
        cooldown={'per': 5, 'gen': 0},
        description='Пнуть рандомного/указанного чела.'
    )
    async def slap(self, ctx):
        user = user2 = ctx.content.strip('@')
        slap = choice(read_file('data/slap/slap.txt'))

        try:
            if not user:
                if len(self.bot.chatters[ctx.channel.name]) > 2:
                    user, user2 = self.bot.random_chatter(ctx, count=2)
                else:
                    user = user2 = self.bot.random_chatter(ctx)

            if user == user2 and len(self.bot.chatters[ctx.channel.name]) > 2:
                while user == user2:
                    user2 = self.bot.random_chatter(ctx)

            if 'choice' in slap:
                for word in slap.split('`'):
                    if 'choice' in word:
                        slap = slap.replace(word, eval(word, {'choice': choice, 'smile': self.bot.smile, 'ctx': ctx,'str': str, 'randint': randint}))
                slap = slap.replace('`', '')

            kwargs = {}
            for word in slap.split():
                if 'author' in word:
                    kwargs['author'] = ctx.author.display_name if ctx.author.display_name.lower() == ctx.author.name else ctx.author.name
                elif 'user2' in word:
                    kwargs['user2'] = user2
                elif 'user' in word:
                    kwargs['user'] = user
                elif 'vozol' in word:
                    kwargs['vozol'] = choice(read_file('data/vozol.txt'))
                elif 'food' in word:
                    kwargs['food'] = choice(read_file('data/slap/food.txt')).strip('\n').format(user2=user2)
                elif 'compliment' in word:
                    kwargs['compliment'] = choice(read_file('data/compliments.txt'))
                elif 'drink' in word:
                    kwargs['drink'] = choice(read_file('data/slap/drinks.txt')).strip('\n')
                elif 'game' in word:
                    kwargs['game'] = choice(read_file('data/slap/games.txt')).strip('\n')

            message = slap.format(**kwargs)
            if 'smile' in message:
                for word in message.split('~'):
                    if 'smile' in word:
                        message = message.replace(word, eval(word, {'smile': self.bot.smile, 'ctx': ctx}))
                message = message.replace('~', '')

            if 'randint' in message:
                for word in message.split():
                    if 'randint' in word:
                        message = message.replace(word, str(eval(word, {'randint': randint})))
        except:
            traceback.print_exc()
            print(slap[0:70] + '...')
            return

        await ctx.reply(message)


def prepare(bot):
    bot.add_cog(Slap(bot))
