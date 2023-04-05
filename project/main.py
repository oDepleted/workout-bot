import os
import json
import random
import datetime
import asyncio

import pendulum
import discord
from discord import app_commands
from discord.ext import tasks

from ui import Configure, CompletionButtons, ConfirmButton, ViewJSON, RestDayButtons, TrackerButtons

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

def get_workout(data):
    if data['exercises'].items():
        weights = {}
        for workout in data['exercises'].items():
            weights[workout[0]] = workout[1]['weight']

        weighted_workouts = []
        for value, weight in weights.items():
            weighted_workouts.extend([value] * weight)
        random_workout = random.choices(weighted_workouts)[0]
        workout_amount = random.randint(data['exercises'][random_workout]['minimum'], data['exercises'][random_workout]['maximum'])

        with open('./assets/messages.json', 'r') as datafile:
            messages = json.load(datafile)
        message = random.choice(messages['messages'])
        return f'{message} Do {workout_amount} {random_workout}!', random_workout, workout_amount
    return None

@client.event
async def on_ready():
    print(f'Logged in as {client.user}\n--------')
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="your fitness"))
    now = datetime.datetime.now()
    sleep_seconds = (30 - now.minute % 30) * 60 - now.second if now.minute < 30 else (60 - now.minute) * 60 - now.second
    await asyncio.sleep(sleep_seconds)
    workout_reminder.start()
    print(f'Task started! Time: {datetime.datetime.now()}')

@tasks.loop(minutes=30)
async def workout_reminder():
    for file in os.listdir('./database/userdata/'):
        user = int(file.split('.')[0])
        with open(f"./database/userdata/{file}", 'r') as datafile:
            data = json.load(datafile)

        if not data['exercises']:
            continue

        timezone = pendulum.timezone(data['options']['time']['timezone'])
        current_time = datetime.datetime.now(timezone).time()
        start_time = datetime.time(hour=data['options']['time']['start_time'])
        end_time = datetime.time(hour=data['options']['time']['end_time'])

        will_continue = False

        if current_time.hour == 0 and current_time.minute < 30:
            print(f'reset daily : {user}')
            for exercise in data['exercises']:
                data['exercises'][exercise]['stats']['daily'] = {'completions': 0, 'fails': 0, 'reps': 0}
            if data['options']['rest_day']['enabled'] == True:
                data['options']['rest_day']['enabled'] = False

            with open(f"./database/userdata/{file}", 'w') as datafile:
                json.dump(data, datafile, indent=4)
            will_continue = True

        if data['options']['rest_day']['enabled']:
            continue

        if current_time.hour == end_time.hour and current_time.minute < 30:
            embed = discord.Embed(title="Daily Exercise Summary", description=None, color=0x9470DC)
            for exercise in data['exercises']:
                completions, fails, reps = data['exercises'][exercise]['stats']['daily'].values()
                embed.add_field(name=exercise.title(), value=f'Reps: {reps}\nCompletions: {completions}\nFails: {fails}')
            guild = client.get_guild(841828321359822858)
            member = guild.get_member(user)
            if not member:
                print('Member not in discord server. Continuing...')
                continue
            await member.send(embed=embed)
            will_continue = True

        if will_continue:
            continue

        if start_time <= current_time <= end_time:
            if random.choice([True, True, False]):
                guild = client.get_guild(841828321359822858)
                member = guild.get_member(user)
                if not member:
                    print('Member not in discord server. Continuing...')
                    continue
                if str(member.status) in data['options']['statuses']:
                    generated_workout, exercise, reps = get_workout(data)
                    if generated_workout:
                        view = CompletionButtons(exercise, reps)
                        await member.send(generated_workout, view=view)

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if isinstance(message.channel, discord.DMChannel):
        if message.content.startswith("new"):
            user = message.author.id
            if os.path.exists(f'./database/userdata/{user}.json'):
                with open(f'./database/userdata/{user}.json', 'r') as datafile:
                    data = json.load(datafile)
                for exercise in data['exercises']:
                    if exercise in message.content[4:]:
                        data = {'exercises': {exercise: data['exercises'][exercise]}}
                        break

                generated_workout, exercise, reps = get_workout(data)
                if generated_workout:
                    view = CompletionButtons(exercise, reps)
                    await message.channel.send(generated_workout, view=view)
                else: await message.channel.send('You have no exercises configured! Use `/configure` to add one!')
            else: await message.channel.send('You have not registered! Use `/register` to register!')

@client.tree.command(name = "register", description = "Get registered into our program")
async def register(interaction: discord.Interaction):
    user = interaction.user.id
    if not os.path.exists(f'./database/userdata/{user}.json'):
        data = {
            "options": {
                "time": {
                    "timezone": "UTC",
                    "start_time": 0,
                    "end_time": 0
                },
                "statuses": ['online'],
                "rest_day": {
                    "enabled": False,
                    "history": []
                }
            },
            "exercises": {},
            "trackers": {}
        }
        with open(f'./database/userdata/{user}.json', 'w') as datafile:
            json.dump(data, datafile, indent=4)

        embed = discord.Embed(title=f"Successfully Registered!", description="Please configure your settings below for the best experience", color=0x9470DC)
        view = Configure()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    else: await interaction.response.send_message(embed=discord.Embed(title=f"Already Registered!", description="To edit your settings you must use `/configure`\nTo register again you must use `/unregister`!\nThis will delete all your settings!", color=0xFF0000))

@client.tree.command(name = "unregister", description = "Get registered into our program")
async def unregister(interaction: discord.Interaction):
    user = interaction.user.id
    if os.path.exists(f'./database/userdata/{user}.json'):
        embed = discord.Embed(title="Confirm Unregistration", description="This will delete all stats and settings!", color=0x9470DC)
        await interaction.response.send_message(embed=embed, view=ConfirmButton(method="unregister"), ephemeral=True)
    else: await interaction.response.send_message(embed=discord.Embed(title="You Aren't Registered!", description='In order to unregister, you need to have registered first!', color=0xFF0000), ephemeral=True)

@client.tree.command(name = "configure", description = "Make changes to your current configuration")
async def configure(interaction: discord.Interaction):
    user = interaction.user.id
    if os.path.exists(f'./database/userdata/{user}.json'):
        embed = discord.Embed(title=f"Configuration Menu", description="Please configure your settings below for the best experience", color=0x9470DC)
        view = Configure()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    else: await interaction.response.send_message(embed=discord.Embed(title=f"You Aren't Registered!", description="In order to change your configuration you must be registered!\nUse `/register` to register!", color=0xFF0000), ephemeral=True)

@client.tree.command(name = "daily", description = "View your daily exercise summary")
async def daily(interaction: discord.Interaction):
    user = interaction.user.id
    if os.path.exists(f'./database/userdata/{user}.json'):
        with open(f"./database/userdata/{user}.json", 'r') as datafile:
            data = json.load(datafile)
        embed = discord.Embed(title="Daily Exercise Summary", description=None, color=0x9470DC)
        json_data = {}
        for exercise in data['exercises']:
            completions, fails, reps = data['exercises'][exercise]['stats']['daily'].values()
            json_data[exercise] = {}
            json_data[exercise]['daily'] = {'completions': completions, 'fails': fails, 'reps': reps}
            embed.add_field(name=exercise.title(), value=f'Reps: {reps}\nCompletions: {completions}\nFails: {fails}')

        if not embed.fields:
            embed.description = "You have no exercises configured."

        await interaction.response.send_message(embed=embed, view=ViewJSON(data=json_data), ephemeral=True)
    else: await interaction.response.send_message(embed=discord.Embed(title="You Aren't Registered!", description='In order to view your daily summary, you need to have registered first!', color=0xFF0000), ephemeral=True)

@client.tree.command(name = "stats", description = "View your all time exercise summary")
async def stats(interaction: discord.Interaction):
    user = interaction.user.id
    if os.path.exists(f'./database/userdata/{user}.json'):
        with open(f"./database/userdata/{user}.json", 'r') as datafile:
            data = json.load(datafile)
        embed = discord.Embed(title="All Time Exercise Summary", description=None, color=0x9470DC)
        json_data = {}
        for exercise in data['exercises']:
            completions, fails, reps = data['exercises'][exercise]['stats']['total'].values()
            json_data[exercise] = {}
            json_data[exercise]['total'] = {'completions': completions, 'fails': fails, 'reps': reps}
            embed.add_field(name=exercise.title(), value=f'Reps: {reps}\nCompletions: {completions}\nFails: {fails}')

        if not embed.fields:
            embed.description = "You have no exercises configured."

        await interaction.response.send_message(embed=embed, view=ViewJSON(data=json_data), ephemeral=True)
    else: await interaction.response.send_message(embed=discord.Embed(title="You Aren't Registered!", description='In order to view your all time summary, you need to have registered first!', color=0xFF0000), ephemeral=True)

@client.tree.command(name = "restday", description = "Manage your rest days")
async def rest_day(interaction: discord.Interaction):
    user = interaction.user.id
    if os.path.exists(f'./database/userdata/{user}.json'):
        with open(f"./database/userdata/{user}.json", 'r') as datafile:
            data = json.load(datafile)
        
        current_status = {True: 'enabled', False: 'disabled'}.get(data['options']['rest_day']['enabled'])
        embed = discord.Embed(title="Manage Or View Rest Days", description=f"Current status: `{current_status}`\nYou can set or unset today as a rest day or view your rest day history.", color=0x9470DC)
        await interaction.response.send_message(embed=embed, view=RestDayButtons(), ephemeral=True)
    else: await interaction.response.send_message(embed=discord.Embed(title="You Aren't Registered!", description='In order to manage your rest days, you need to have registered first!', color=0xFF0000), ephemeral=True)

@client.tree.command(name = "tracker", description = "Track your progress")
async def tracker(interaction: discord.Interaction):
    user = interaction.user.id
    if os.path.exists(f'./database/userdata/{user}.json'):
        embed = discord.Embed(title="Manage Or View Entries", description="Add entries to track your progress over a period of time. Track different stats such as weight, max reps, etc.", color=0x9470DC)
        await interaction.response.send_message(embed=embed, view=TrackerButtons(), ephemeral=True)
    else: await interaction.response.send_message(embed=discord.Embed(title="You Aren't Registered!", description='In order to manage your tracker, you need to have registered first!', color=0xFF0000), ephemeral=True)


if __name__ == "__main__":
    client.run(os.environ.get('WORKOUT_BOT_TOKEN'))
