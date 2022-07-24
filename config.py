import asyncio
import os
import motor.motor_asyncio

TOKEN = os.getenv('TOKEN')
CLIENT_ID = os.getenv('CLIENT_ID')
MONGO = os.getenv('MONGO')
VK_TOKEN = os.getenv('VK_TOKEN')
WEATHER_ID = os.getenv('WEATHER_ID')
RANDOMORG_TOKEN = os.getenv('RANDOMORG_TOKEN')
db = motor.motor_asyncio.AsyncIOMotorClient(MONGO).svinbot

CHANNELS = []


async def get_channels():
    data = await db.channels.find_one({'_id': 1})
    global CHANNELS
    CHANNELS = data['channels']


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(get_channels())
