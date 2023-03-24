import os
import json
import datetime
import random

import discord

class AddExercise(discord.ui.Modal, title='Add Exercise'):
    exercise = discord.ui.TextInput(label='Exercise', placeholder='Exercise...', style=discord.TextStyle.short)
    minimum = discord.ui.TextInput(label='Minimum Reps', placeholder='0', style=discord.TextStyle.short)
    maximum = discord.ui.TextInput(label='Maximum Reps', placeholder='0', style=discord.TextStyle.short)
    weight = discord.ui.TextInput(label='Weight (Chance)', placeholder='0', style=discord.TextStyle.short, max_length=2, default=1)

    async def on_submit(self, interaction: discord.Interaction):
        user = interaction.user.id
        try:
            minimum, maximum, weight, exercise = int(str(self.minimum)), int(str(self.maximum)), int(str(self.weight)), str(self.exercise)
        except ValueError:
            await interaction.response.send_message(embed=discord.Embed(title=f"Invalid Input!", description="The values `Minimum Reps`, `Maximum Reps`, and `Weight (Chance)` must be integers!", color=0xFF0000), ephemeral=True)
            return
        if minimum < 1 or maximum < 1 or weight < 0:
            await interaction.response.send_message(embed=discord.Embed(title=f"Invalid Input!", description="The values `Minimum Reps`, `Maximum Reps` should be greater than `0` and `Weight (Chance)` must be greater than or equal to `0`!", color=0xFF0000), ephemeral=True)
            return
        with open(f'./database/userdata/{user}.json', 'r') as datafile:
            data = json.load(datafile)
        if not exercise in data['exercises']:
            if maximum > minimum:
                data['exercises'][exercise.lower()] = {
                    'weight': weight,
                    'minimum': minimum,
                    'maximum': maximum,
                    'stats': {
                        'total': {
                            'completions': 0,
                            'fails': 0,
                            'reps': 0
                        },
                        'daily': {
                            'completions': 0,
                            'fails': 0,
                            'reps': 0 
                        }
                    
                    }
                }
                with open(f'./database/userdata/{user}.json', 'w') as datafile:
                    json.dump(data, datafile, indent=4)
                await interaction.response.send_message(f'Successfully added `{exercise.lower()}` to your exercises!', ephemeral=True)
                return
            await interaction.response.send_message('`Maximum Reps` must be greater than `Minimum Reps`!', ephemeral=True)
            return
        await interaction.response.send_message('You already have that exercise added! Please remove it before adding it again.', ephemeral=True)

class ViewJSON(discord.ui.View):
    def __init__(self, data) -> None:
        super().__init__(timeout=None)
        self.data = data
    
    @discord.ui.button(label = "View JSON", style = discord.ButtonStyle.gray, custom_id="view_json", row=1)
    async def view_json(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(content=f"```json\n{json.dumps(self.data, indent=4)}```", ephemeral=True)

class RenameExercise(discord.ui.Modal, title='Rename Exercise'):
    def __init__(self, old_name, callback, **kwargs):
        self.old_name = old_name
        self.callback = callback
        super().__init__(**kwargs)

    new_name = discord.ui.TextInput(label='Rename to', placeholder='New name...', style=discord.TextStyle.short)
    async def on_submit(self, interaction: discord.Interaction):
        new_name = str(self.new_name).lower()
        self.callback(new_name)
        user = interaction.user.id
        with open(f'./database/userdata/{user}.json', 'r') as datafile:
            data = json.load(datafile)
        if new_name in data['exercises']:
            await interaction.response.send_message(embed=discord.Embed(title=f"Exercise already exists", description=f"You already have an exercise named `{new_name}`! Please rename or delete this in order to proceed!", color=0xFF0000), ephemeral=True)
            return
        data['exercises'][new_name] = data['exercises'].pop(self.old_name)
        with open(f'./database/userdata/{user}.json', 'w') as datafile:
            data = json.dump(data, datafile, indent=4)
        await interaction.response.send_message(f'Successfully updated name! `{self.old_name} -> {new_name}`', ephemeral=True)

class SetMinimumExercise(discord.ui.Modal, title='Set Minimum'):
    def __init__(self, exercise, **kwargs):
        self.exercise = exercise
        super().__init__(**kwargs)

    new_minimum = discord.ui.TextInput(label='New Minimum', placeholder='0', style=discord.TextStyle.short)
    async def on_submit(self, interaction: discord.Interaction):
        user = interaction.user.id
        try: new_minimum = int(str(self.new_minimum))
        except ValueError:
            await interaction.response.send_message(embed=discord.Embed(title=f"Invalid Input!", description="The value `Minimum Reps` must be an integer!", color=0xFF0000), ephemeral=True)
            return
        if new_minimum < 1:
            await interaction.response.send_message(embed=discord.Embed(title=f"Invalid Input!", description="The value `Minimum Reps` must be greater than 0!", color=0xFF0000), ephemeral=True)
            return
        with open(f'./database/userdata/{user}.json', 'r') as datafile:
            data = json.load(datafile)
        data['exercises'][self.exercise]['minimum'] = new_minimum
        if data['exercises'][self.exercise]['maximum'] < new_minimum:
            data['exercises'][self.exercise]['maximum'] = new_minimum
        with open(f'./database/userdata/{user}.json', 'w') as datafile:
            json.dump(data, datafile, indent=4)
        await interaction.response.send_message(f'Successfully updated minimum reps for `{self.exercise}` to `{new_minimum}`.', ephemeral=True)

class SetMaximumExercise(discord.ui.Modal, title='Set Maximum'):
    def __init__(self, exercise, **kwargs):
        self.exercise = exercise
        super().__init__(**kwargs)

    new_maximum = discord.ui.TextInput(label='New Maximum', placeholder='0', style=discord.TextStyle.short)
    async def on_submit(self, interaction: discord.Interaction):
        user = interaction.user.id
        try: new_maximum = int(str(self.new_maximum))
        except ValueError:
            await interaction.response.send_message(embed=discord.Embed(title=f"Invalid Input!", description="The value `Maximum Reps` must be an integer!", color=0xFF0000), ephemeral=True)
            return
        if new_maximum < 1:
            await interaction.response.send_message(embed=discord.Embed(title=f"Invalid Input!", description="The value `Maximum Reps` must be greater than 0!", color=0xFF0000), ephemeral=True)
            return
        with open(f'./database/userdata/{user}.json', 'r') as datafile:
            data = json.load(datafile)
        data['exercises'][self.exercise]['maximum'] = new_maximum
        if data['exercises'][self.exercise]['minimum'] > new_maximum:
            data['exercises'][self.exercise]['minimum'] = new_maximum
        with open(f'./database/userdata/{user}.json', 'w') as datafile:
            json.dump(data, datafile, indent=4)
        await interaction.response.send_message(f'Successfully updated maximum reps for `{self.exercise}` to `{new_maximum}`.', ephemeral=True)

class SetExerciseWeight(discord.ui.Modal, title='Set Weight (Chance)'):
    def __init__(self, exercise, **kwargs):
        self.exercise = exercise
        super().__init__(**kwargs)

    new_weight = discord.ui.TextInput(label='New Weight', placeholder='1', style=discord.TextStyle.short, max_length=2)
    async def on_submit(self, interaction: discord.Interaction):
        user = interaction.user.id
        try: new_weight = int(str(self.new_weight))
        except ValueError:
            await interaction.response.send_message(embed=discord.Embed(title=f"Invalid Input!", description="The value `Weight` must be an integer!", color=0xFF0000), ephemeral=True)
            return
        if new_weight < 0:
            await interaction.response.send_message(embed=discord.Embed(title=f"Invalid Input!", description="The value `Weight` must be a positive integer!", color=0xFF0000), ephemeral=True)
            return
        with open(f'./database/userdata/{user}.json', 'r') as datafile:
            data = json.load(datafile)
        data['exercises'][self.exercise]['weight'] = new_weight
        with open(f'./database/userdata/{user}.json', 'w') as datafile:
            json.dump(data, datafile, indent=4)
        await interaction.response.send_message(f'Successfully updated weight (chance) for `{self.exercise}` to `{new_weight}`.', ephemeral=True)


class Configure(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(label = "Timezone", style = discord.ButtonStyle.blurple, custom_id = "set_timezone", row=1)
    async def set_timezone(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="Select your timezone!", description="Select your timezone from the dropdown box below.\nThis will determine when you recieve reminders!", color=0x9470DC)
        await interaction.response.send_message(embed=embed, view=SetTimezone(), ephemeral=True)

    @discord.ui.button(label = "Start Hour", style = discord.ButtonStyle.blurple, custom_id = "set_start_hour", row=1)
    async def start_hour(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="Select a Start Hour", description="By configuring start and finish hours, you will not be bothered outside these hours.", color=0x9470DC)
        await interaction.response.send_message(embed=embed, view=SelectView(placeholder="Start Hour", options=[discord.SelectOption(label=integer) for integer in range(24)], interaction=interaction, min=1, max=1), ephemeral=True)

    @discord.ui.button(label = "Finish Hour", style = discord.ButtonStyle.blurple, custom_id = "set_end_hour", row=1)
    async def end_hour(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="Select a Finish Hour", description="By configuring start and finish hours, you will not be bothered outside these hours.", color=0x9470DC)
        await interaction.response.send_message(embed=embed, view=SelectView(placeholder="Finish Hour", options=[discord.SelectOption(label=integer) for integer in range(24)], interaction=interaction, min=1, max=1), ephemeral=True)

    @discord.ui.button(label = "Statuses", style = discord.ButtonStyle.blurple, custom_id = "manage_statuses", row=1)
    async def manage_statuses(self, interaction: discord.Interaction, button: discord.ui.Button):
        statuses = ('Online', 'Idle', 'Do Not Disturb', 'Offline')
        embed = discord.Embed(title="Configure Your Statuses", description="The bot will only message you when you have a selected statuses.", color=0x9470DC)
        await interaction.response.send_message(embed=embed, view=SelectView(placeholder="Select Statuses", options=[discord.SelectOption(label=status) for status in statuses], interaction=interaction, min=0, max=4), ephemeral=True)  

    @discord.ui.button(label = "Add Exercise", style = discord.ButtonStyle.success, custom_id = "add_exercise", row=2)
    async def add_exercise(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AddExercise())

    @discord.ui.button(label = "Remove Exercise", style = discord.ButtonStyle.danger, custom_id = "remove_exercises", row=2)
    async def remove_exercises(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user.id
        with open(f'./database/userdata/{user}.json', 'r') as datafile: exercise_data = json.load(datafile)['exercises']
        if exercise_data:
            options = [discord.SelectOption(label=exercise) for exercise in exercise_data]
            embed = discord.Embed(title="Select Exercises To Remove", description="All settings for removed exercises will be lost! This cannot be undone.", color=0x9470DC)
            await interaction.response.send_message(embed=embed, view=SelectView(placeholder="Select Exercises To Remove", options=options, interaction=interaction, min=0, max=len(options)), ephemeral=True)
            return
        await interaction.response.send_message(embed=discord.Embed(title="Nothing To Remove", description="In order to remove exercises, you must have exercises configured!", color=0xFF0000), ephemeral=True)

    @discord.ui.button(label = "Manage Exercises", style = discord.ButtonStyle.gray, custom_id = "manage_exercises", row=2)
    async def manage_exercises(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user.id
        with open(f'./database/userdata/{user}.json', 'r') as datafile: exercise_data = json.load(datafile)['exercises']
        if exercise_data:
            options = [discord.SelectOption(label=exercise) for exercise in exercise_data]
            embed = discord.Embed(title="Select Exercise To Configure", description="Change minimum, maximum, weight, or rename.", color=0x9470DC)
            await interaction.response.send_message(embed=embed, view=SelectView(placeholder="Select Exercise To Configure", options=options, interaction=interaction, min=1, max=1), ephemeral=True)
            return
        await interaction.response.send_message(embed=discord.Embed(title="Nothing To Manage!", description="In order to manage exercises, you must have exercises configured!", color=0xFF0000), ephemeral=True)

    @discord.ui.button(label = "List Exercises", style = discord.ButtonStyle.gray, custom_id = "list_exercises", row=3)
    async def list_exercises(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user.id
        with open(f'./database/userdata/{user}.json', 'r') as datafile: exercise_data = json.load(datafile)['exercises']
        embed = discord.Embed(title="List of configured exercises:", description=None, color=0x9470DC)
        for exercise in exercise_data:
            embed.add_field(name=exercise.title(), value=f"Minimum: {exercise_data[exercise]['minimum']}\nMaximum: {exercise_data[exercise]['maximum']}\nWeight (chance): {exercise_data[exercise]['weight']}")
        if not embed.fields:
            embed.description = "You have no exercises configured."
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label = "List Settings", style = discord.ButtonStyle.gray, custom_id = "list_settings", row=3)
    async def list_settings(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user.id
        with open(f'./database/userdata/{user}.json', 'r') as datafile: data = json.load(datafile)
        timezone, start_time, finish_time = data['options']['time'].values()
        statuses = data['options']['statuses']
        online, idle, dnd, offline = str("online" in statuses).lower(), str("idle" in statuses).lower(), str("dnd" in statuses).lower(), str("offline" in statuses).lower()
        rest_day = str(data['options']['rest_day']).lower()

        embed = discord.Embed(title='Your Configuration', color=0x9470DC)
        embed.add_field(name='Time Settings', value=f'Timezone: {timezone}\nStart Time: {datetime.time(hour=start_time)}\nFinish Time: {datetime.time(hour=finish_time)}', inline=False)
        embed.add_field(name="Statuses:", value=f'Online: {online}\nIdle: {idle}\nDo Not Disturb: {dnd}\nOffline: {offline}', inline=False)
        embed.add_field(name='Other:', value=f'Rest Day: {rest_day}', inline=False)
        
        options = {}
        options['options'] = json.load(datafile)['options']
        await interaction.response.send_message(embed=embed, view=ViewJSON(data=options), ephemeral=True)

class ConfigureExercises(discord.ui.View):
    def __init__(self, original_exercise) -> None:
        super().__init__(timeout=None)
        self.original_exercise = original_exercise

    def update_original_exercise(self, new_exercise):
        self.original_exercise = new_exercise

    @discord.ui.button(label = "Rename", style = discord.ButtonStyle.blurple, custom_id = "rename_exercise", row=1)
    async def rename_exercise(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(RenameExercise(self.original_exercise, self.update_original_exercise))

    @discord.ui.button(label = "Edit Minimum", style = discord.ButtonStyle.blurple, custom_id = "change_minimum_exercises", row=1)
    async def change_minimum_exercises(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SetMinimumExercise(self.original_exercise))

    @discord.ui.button(label = "Edit Maximum", style = discord.ButtonStyle.blurple, custom_id = "change_maximum_exercises", row=1)
    async def change_maximum_exercises(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SetMaximumExercise(self.original_exercise))

    @discord.ui.button(label = "Edit Weight", style = discord.ButtonStyle.blurple, custom_id = "change_exercise_weight", row=1)
    async def change_exercises_weight(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SetExerciseWeight(self.original_exercise))

class SetTimezone(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(label = "North America", style = discord.ButtonStyle.blurple, custom_id = "timezones_north_america", emoji='🦅', row=1)
    async def set_timezone_north_america(self, interaction: discord.Interaction, button: discord.ui.Button):
        with open('./assets/timezones.json', 'r') as datafile:
            timezones = json.load(datafile)['north_america']
        embed = discord.Embed(title="Timezones for North America", description="Select your timezone from the dropdown box below.\nThis will determine when you recieve reminders!", color=0x9470DC)
        await interaction.response.send_message(embed=embed, view=SelectView(placeholder="Select Timezone", options=[discord.SelectOption(label=timezone) for timezone in timezones], interaction=interaction, min=1, max=1), ephemeral=True)

    @discord.ui.button(label = "South America", style = discord.ButtonStyle.blurple, custom_id = "timezones_south_america", emoji='🌄', row=1)
    async def set_timezone_south_america(self, interaction: discord.Interaction, button: discord.ui.Button):
        with open('./assets/timezones.json', 'r') as datafile:
            timezones = json.load(datafile)['south_america']
        embed = discord.Embed(title="Timezones for South America", description="Select your timezone from the dropdown box below.\nThis will determine when you recieve reminders!", color=0x9470DC)
        await interaction.response.send_message(embed=embed, view=SelectView(placeholder="Select Timezone", options=[discord.SelectOption(label=timezone) for timezone in timezones], interaction=interaction, min=1, max=1), ephemeral=True)

    @discord.ui.button(label = "Asia", style = discord.ButtonStyle.blurple, custom_id = "timezones_asia", emoji='🐼', row=1)
    async def set_timezone_asia(self, interaction: discord.Interaction, button: discord.ui.Button):
        with open('./assets/timezones.json', 'r') as datafile:
            timezones = json.load(datafile)['asia']
        embed = discord.Embed(title="Timezones for Asia", description="Select your timezone from the dropdown box below.\nThis will determine when you recieve reminders!", color=0x9470DC)
        await interaction.response.send_message(embed=embed, view=SelectView(placeholder="Select Timezone", options=[discord.SelectOption(label=timezone) for timezone in timezones], interaction=interaction, min=1, max=1), ephemeral=True)

    @discord.ui.button(label = "Europe", style = discord.ButtonStyle.blurple, custom_id = "timezones_europe", emoji='🏰', row=2)
    async def set_timezone_europe(self, interaction: discord.Interaction, button: discord.ui.Button):
        with open('./assets/timezones.json', 'r') as datafile:
            timezones = json.load(datafile)['europe']
        embed = discord.Embed(title="Timezones for Europe", description="Select your timezone from the dropdown box below.\nThis will determine when you recieve reminders!", color=0x9470DC)
        await interaction.response.send_message(embed=embed, view=SelectView(placeholder="Select Timezone", options=[discord.SelectOption(label=timezone) for timezone in timezones], interaction=interaction, min=1, max=1), ephemeral=True)

    @discord.ui.button(label = "Africa", style = discord.ButtonStyle.blurple, custom_id = "timezones_africa", emoji='🦒', row=2)
    async def set_timezone_africa(self, interaction: discord.Interaction, button: discord.ui.Button):
        with open('./assets/timezones.json', 'r') as datafile:
            timezones = json.load(datafile)['africa']
        embed = discord.Embed(title="Timezones for Africa", description="Select your timezone from the dropdown box below.\nThis will determine when you recieve reminders!", color=0x9470DC)
        await interaction.response.send_message(embed=embed, view=SelectView(placeholder="Select Timezone", options=[discord.SelectOption(label=timezone) for timezone in timezones], interaction=interaction, min=1, max=1), ephemeral=True)

    @discord.ui.button(label = "Oceania / Pacific", style = discord.ButtonStyle.blurple, custom_id = "timezones_pacific", emoji='🐨', row=2)
    async def set_timezone_pacific(self, interaction: discord.Interaction, button: discord.ui.Button):
        with open('./assets/timezones.json', 'r') as datafile:
            timezones = json.load(datafile)['pacific']
        embed = discord.Embed(title="Timezones for Oceania / Pacific", description="Select your timezone from the dropdown box below.\nThis will determine when you recieve reminders!", color=0x9470DC)
        await interaction.response.send_message(embed=embed, view=SelectView(placeholder="Select Timezone", options=[discord.SelectOption(label=timezone) for timezone in timezones], interaction=interaction, min=1, max=1), ephemeral=True)

# Select menus
class Select(discord.ui.Select):
    def __init__(self, placeholder, options, min, max):
        super().__init__(placeholder=placeholder, max_values=max, min_values=min, options=options)
        self.placeholder = placeholder

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user.id
        if self.placeholder == "Select Exercise To Configure":
            embed = discord.Embed(title="Configuration Options", description=f"Use the buttons below to make changes to `{self.values[0]}`", color=0x9470DC)
            await interaction.response.send_message(embed=embed, view=ConfigureExercises(self.values[0]), ephemeral=True)
            return

        with open(f'./database/userdata/{user}.json', 'r') as datafile:
            data = json.load(datafile)
        if self.placeholder == "Select Timezone":
            selected_timezone = self.values[0]
            data['options']['time']['timezone'] = selected_timezone
            response = f'Successfully updated your timezone to `{selected_timezone}`!'
        
        elif self.placeholder == "Start Hour":
            start_hour = int(self.values[0])
            data['options']['time']['start_time'] = start_hour
            formatted_start_hour = datetime.time(hour=start_hour)
            response = f'Successfully updated your start time to `{formatted_start_hour}`!'

        elif self.placeholder == "Finish Hour":
            end_hour = int(self.values[0])
            data['options']['time']['end_time'] = end_hour
            formatted_end_hour = datetime.time(hour=end_hour)
            response = f'Successfully updated your finish time to `{formatted_end_hour}`!'

        elif self.placeholder == "Select Statuses":
            status_list = [status.lower() if status != "Do Not Disturb" else 'dnd' for status in self.values]
            data['options']['statuses'] = status_list
            formatted_status_list = ', '.join(self.values) if self.values else "None"
            response = f'Successfully updated your statuses to include: `{formatted_status_list}`!'

        elif self.placeholder == "Select Exercises To Remove":
            if self.values:
                removed_list = []
                for exercise in self.values:
                    if str(exercise) in data['exercises']: removed_list.append(str(exercise))
                formatted_removed_list = ', '.join(removed_list) if removed_list else "None"
                embed = discord.Embed(title='Confirm Deletion', description=f'You are about to delete the following exercises: `{formatted_removed_list}`!\nThis cannot be undone, press the button below to continue.', color=0xFF0000)
                await interaction.response.send_message(embed=embed, view=ConfirmButton(method='delete_exercise', values=self.values), ephemeral=True)
                return
            await interaction.response.send_message(content='No exercises were selected.', ephemeral=True)
            return

        with open(f'./database/userdata/{user}.json', 'w') as datafile:
            json.dump(data, datafile, indent=4)
        await interaction.response.send_message(response, ephemeral=True)


class SelectView(discord.ui.View):
    def __init__(self, placeholder, options, interaction, min, max, *, timeout=300):
        super().__init__(timeout=timeout)
        self.add_item(Select(placeholder, options, min, max))
        self.interaction = interaction

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True
        await self.interaction.edit_original_response(view=self)

class CompletionButtons(discord.ui.View):
    def __init__(self, exercise, reps) -> None:
        super().__init__(timeout=None)
        self.exercise, self.reps = exercise, reps

    @discord.ui.button(label = "Mark Completed", style = discord.ButtonStyle.success, custom_id = "mark_completed", row=1)
    async def mark_completed(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user.id
        button.disabled = True
        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(view=self)

        with open('./assets/messages.json', 'r') as datafile:
            messages = json.load(datafile)
        message = random.choice(messages['completed_messages'])

        with open(f'./database/userdata/{user}.json', 'r') as datafile:
            data = json.load(datafile)
        data['exercises'][self.exercise]['stats']['total']['completions'] += 1
        data['exercises'][self.exercise]['stats']['total']['reps'] += self.reps
        data['exercises'][self.exercise]['stats']['daily']['completions'] += 1
        data['exercises'][self.exercise]['stats']['daily']['reps'] += self.reps
        with open(f'./database/userdata/{user}.json', 'w') as datafile:
            json.dump(data, datafile, indent=4)

        await interaction.followup.send(f'{message}', ephemeral=True)

    @discord.ui.button(label = "Mark Failed", style = discord.ButtonStyle.danger, custom_id = "mark_failed", row=1)
    async def mark_failed(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user.id
        button.disabled = True
        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(view=self)
        
        with open('./assets/messages.json', 'r') as datafile:
            messages = json.load(datafile)
        message = random.choice(messages['failed_messages'])

        with open(f'./database/userdata/{user}.json', 'r') as datafile:
            data = json.load(datafile)
        data['exercises'][self.exercise]['stats']['total']['fails'] += 1
        data['exercises'][self.exercise]['stats']['daily']['fails'] += 1
        with open(f'./database/userdata/{user}.json', 'w') as datafile:
            json.dump(data, datafile, indent=4)

        await interaction.followup.send(f'{message}', ephemeral=True)

class ConfirmButton(discord.ui.View):
    def __init__(self, method, values=None) -> None:
        super().__init__(timeout=None)
        self.values = values
        self.method = method

    @discord.ui.button(label = "Confirm", style = discord.ButtonStyle.danger, custom_id = "confirm_button", emoji='<:danger:1088218692183134361>', row=1)
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user.id
        button.disabled = True
        await interaction.response.edit_message(view=self)
        if self.method == "unregister":
            os.remove(f'./database/userdata/{user}.json')
            await interaction.followup.send('Successfully unregistered! *We are sorry to see you go.*', ephemeral=True)
        elif self.method == "delete_exercise":
            with open(f'./database/userdata/{user}.json', 'r') as datafile:
                data = json.load(datafile)
            removed_list = []
            for exercise in self.values:
                if str(exercise) in data['exercises']:
                    del data['exercises'][str(exercise)]
                    removed_list.append(str(exercise))
            with open(f'./database/userdata/{user}.json', 'w') as datafile:
                json.dump(data, datafile, indent=4)
            formatted_removed_list = ', '.join(removed_list) if removed_list else "None"
            await interaction.followup.send(f'Successfully deleted the following exercises: `{formatted_removed_list}`.', ephemeral=True)
