import os
import json
import random
import datetime
import pytz

import discord
from discord import app_commands, ui
from discord.ext import tasks

from ui import SelectView, Configure

class MyClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.all()
        intents.message_content = True
        intents.members = True
        intents.presences = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
    async def setup_hook(self):
        await self.tree.sync()
client = MyClient()

def get_workout(data, user):
    if data['users'][user]['exercises'].items():
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
    return None

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

            if start_time < current_time < end_time and data['users'][user]['options']['rest_day'] == False:
                guild = client.get_guild(841828321359822858)
                member = guild.get_member(int(user))
                if str(member.status) in data['users'][user]['options']['statuses']:
                    generated_workout = get_workout(data, user)
                    #print(get_workout(data, user))
                    if generated_workout:
                        await member.send(generated_workout)

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if isinstance(message.channel, discord.DMChannel):
        if message.content.startswith("new"):
            user = str(message.author.id)
            with open('./workout.json', 'r') as datafile:
                data = json.load(datafile)
            #print(get_workout(data, user))
            generated_workout = get_workout(data, user)
            if generated_workout:
                await message.channel.send(generated_workout)
            else: await message.channel.send('You have no exercises configured! Use `/configure` to add one!')

@client.tree.command(name = "register", description = "Get registered into our program")
async def register(interaction: discord.Interaction):
    with open('./workout.json', 'r') as datafile:
        data = json.load(datafile)
    if not str(interaction.user.id) in data['users']:
        new_tree = {
            "options": {
                "time": {
                    "timezone": "UTC",
                    "start_time": 0,
                    "end_time": 0
                },
                "statuses": ['disabled'],
                "rest_day": False
            },
            "exercises": {}
        }
        data['users'][str(interaction.user.id)] = new_tree
        with open('./workout.json', 'w') as datafile:
            json.dump(data, datafile, indent=4)

        embed = discord.Embed(title=f"Successfully Registered!", description="Please configure your settings below for the best experience", color=0x9470DC)
        view = Configure()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    else: await interaction.response.send_message(embed=discord.Embed(title=f"Already Registered!", description="To edit your settings you must use `/configure`\nTo register again you must use `/unregister`!\nThis will delete all your settings!", color=0xFF0000))

@client.tree.command(name = "configure", description = "Make changes to your current configuration")
async def configure(interaction: discord.Interaction):
    with open('./workout.json', 'r') as datafile:
        data = json.load(datafile)
    if str(interaction.user.id) in data['users']:
        embed = discord.Embed(title=f"Configuration Menu", description="Please configure your settings below for the best experience", color=0x9470DC)
        view = Configure()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    else: await interaction.response.send_message(embed=discord.Embed(title=f"You Aren't Registered!", description="In order to change your configuration you must be registered!\nUse `/register` to register!", color=0xFF0000))

client.run(os.environ.get('WORKOUT_BOT_TOKEN'))
