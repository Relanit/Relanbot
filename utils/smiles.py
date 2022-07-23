smile_examples = {
    'pog': {
        'channel': {'pog', 'pogpog', 'pfff', 'PogT', 'Pog', 'bruhbruh', 'BRUHBRUH'},
        'default': {'PogChamp', 'PogBones'}
    },
    'ez': {
        'channel': {'GIGACHAD', 'Krytoi', 'BASED', 'POU', 'EZ Clap'},
        'default': {'EZ Clap'}
    },
    'sad': {
        'channel': {'Sadge', 'SadCat', 'peepoDown', 'pepeCry', 'FeelsWeakMan', 'Sadeg', 'SadChamp', 'catCry', 'sadCat'},
        'default': {'peepoSad', 'PoroSad', 'BibleThump'}
    },
    'love': {
        'channel': {'PeepoLuv', 'FloppaL', 'peepoLove', 'PukHeart', 'Hug0', 'peepoPats', 'pepeL', 'peepoShy', 'Luv', 'peepoHug'},
        'default': {'<3', '😍'}
    },
    'rip': {
        'channel': {'Deadge', 'roflanPominy', 'peepoRIP'},
        'default': {'💀', '⚰'}
    },
    'verypog': {
        'channel': {'verypog', 'Popkorn', 'Chai', 'showard', 'modcheck', 'Melon', 'VeryPog'},
        'default': {'FeelsDankMan', 'WTRuck'}
    },
    'jam': {
        'channel': {'Dadada', 'Dadadada', 'pepeFASTJAM', 'lebronJAM', 'pepeJAM', 'pepeJAMJAM', 'EZDance', 'catJam', 'VIBE'},
        'default': {'forsenPls', 'AlienDance', 'SourPls'}
    },
    'yep': {
        'channel': {'BOOBA', 'BOOBEST', 'YEP', 'YEPPEPEPEEYEP', 'kok', 'Smirk', 'epchik'},
        'default': {'😏', '🤤'}
    },
    'eblan': {
        'channel': {'EBLAN', 'Dolbaeb', 'Durak', 'maaaaan', 'Pepega'},
        'default': {'🤪', 'FailFish'}
    },
    'meltdown': {
        'channel': {'pepeMeltdown', 'monkaInsane', 'monkaw', 'monkaW', 'monkaX', 'monkaS', 'monkaOMEGA'},
        'default': {'monkaS'}
    },
    'tasty': {
        'channel': {'Cat', 'Tasty', 'PogTasty'},
        'default': {'🍽'}
    },
    'bruh': {
        'channel': {'bruh', 'BRUH', 'Starege', 'WEIRD', 'peepoWeirdLeave', 'sho'},
        'default': {'FeelsWeirdMan', '😦'}
    },
    'despair': {
        'channel': {'TrollDespair', 'Despairge', 'BRUHDespair', 'forsenDespair', 'Despair'},
        'default': {'😧'}
    },
    'sleep': {
        'channel': {'catSleep', 'peepoSleep', 'catSleep', 'Peepobed', 'Bedge', 'gn'},
        'default': {'ResidentSleeper', '😴'}
    },
    'chatting': {
        'channel': {'Chatting', 'FeelsChattingMan', 'chatting', 'peepoChat'},
        'default': {'ImTyping'}
    }
}


async def get_bttv(client, broadcaster_id):
    url = f'https://api.betterttv.net/3/cached/users/twitch/{broadcaster_id}'
    async with client.get(url) as response:
        data = await response.json()

    smiles = []
    try:
        for smile in data['channelEmotes']:
            smiles.append(smile['code'])

        for smile in data['sharedEmotes']:
            smiles.append(smile['code'])
    except KeyError:
        pass

    return smiles


async def get_ffz(client, broadcaster_id):
    url = f'https://api.betterttv.net/3/cached/frankerfacez/users/twitch/{broadcaster_id}'
    async with client.get(url) as response:
        data = await response.json()

    smiles = []
    for smile in data:
        smiles.append(smile['code'])

    return smiles


async def get_7tv(client, login):
    url = f'https://api.7tv.app/v2/users/{login}/emotes'
    async with client.get(url) as response:
        data = await response.json()

    smiles = []
    try:
        for smile in data:
            smiles.append(smile['name'])
    except TypeError:
        pass

    return smiles


async def get_global_smiles(client):
    smiles = []

    url = 'https://api.betterttv.net/3/cached/emotes/global'
    async with client.get(url) as response:
        bttv_smiles = await response.json()

    for smile in bttv_smiles:
        smiles.append(smile['code'])

    url = 'https://api.frankerfacez.com/v1/set/global'
    async with client.get(url) as response:
        ffz_smiles = await response.json()

    ffz_smiles = ffz_smiles['sets']['3']['emoticons']
    for smile in ffz_smiles:
        smiles.append(smile['name'])

    url = 'https://api.7tv.app/v2/emotes/global'
    async with client.get(url) as response:
        stv_smiles = await response.json()

    for smile in stv_smiles:
        smiles.append(smile['name'])

    return smiles
