import os
import json
import random
import datetime
import pytz

import discord
from discord.ext import tasks, commands

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        intents.message_content = True
        intents.members = True
        intents.presences = True
        super().__init__(command_prefix=commands.when_mentioned_or('$'), intents=intents)
client = Bot()

def get_workout(data, user):
    weights = {}
    for workout in data['users'][user]['exercises'].items():
        weights[workout[0]] = workout[1]['weight']

    weighted_workouts = []
    for value, weight in weights.items():
        weighted_workouts.extend([value] * weight)
    random_workout = random.choices(weighted_workouts)[0]
    workout_amount = random.randint(data['users'][user]['exercises'][random_workout]['minimum'], data['users'][user]['exercises'][random_workout]['maximum'])

    with open('./messages.json', 'r') as datafile:
        messages = json.load(datafile)
    message = random.choice(messages['messages'])
    return f'{message} Do {workout_amount} {random_workout}!'

@client.event
async def on_ready():
    print(f'Logged in as {client.user}\n--------')
    workout_reminder.start()
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="your fitness"))

@tasks.loop(minutes=30)
async def workout_reminder():
    if random.choice([True, True, False]):
        with open('./workout.json', 'r') as datafile:
            data = json.load(datafile)
        for user in data['users']:
            timezone = pytz.timezone(data['users'][user]['options']['time']['timezone'])
            current_time = datetime.datetime.now(timezone).time()
            start_time = datetime.time(hour=data['users'][user]['options']['time']['start_time'])
            end_time = datetime.time(hour=data['users'][user]['options']['time']['end_time'])

            if start_time < current_time < end_time:
                print(get_workout(data, user))
                #guild = client.get_guild(841828321359822858)
                #user = guild.get_member(int(user))
                #await user.send(get_workout(data, user))

@client.event
async def on_message(message):
  if message.author == client.user:
    return
  if message.content.startswith("new"):
    if isinstance(message.channel, discord.DMChannel):
        user = str(message.author.id)
        with open('./workout.json', 'r') as datafile:
            data = json.load(datafile)
        print(get_workout(data, user))
        #await message.channel.send(get_workout(data, user))

client.run(os.environ.get('WORKOUT_BOT_TOKEN'))
