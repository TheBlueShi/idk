import discord
from discord.ext import commands, tasks
import os
import json
from webserver import keep_alive
import requests
import random
from datetime import datetime, timedelta

DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
print(f"Using token: {DISCORD_TOKEN}")
print(os.environ)
if DISCORD_TOKEN is None:
    print("Error: DISCORD_TOKEN not set in environment variables.")
    exit(1)
    
API_KEY = os.getenv('API_KEY')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))

intents = discord.Intents.default()
intents.message_content = True
intents.presences = True
intents.guilds = True
intents.reactions = True

# Use the PREFIX from the config
bot = commands.Bot(command_prefix=">", intents=intents)

# Fetch fact from API function
def fetch_fact():
    api_key = os.getenv("API_KEY")  # Ensure your API_KEY is in Railway's environment variables
    url = f"https://api.example.com/fact?apikey={api_key}"  # Update with the correct URL

    try:
        response = requests.get(url)
        response.raise_for_status()
        fact_data = response.json()
        return fact_data.get('fact', 'No fact found.')
    except requests.exceptions.RequestException as e:
        print(f"Error fetching fact: {e}")
        return "Failed to fetch the fact. Please try again later."


@tasks.loop(minutes=1)  # Change to hours=24 for daily after testing
async def send_daily_fact():
    channel_id = int(os.getenv("CHANNEL_ID"))  # Set the channel ID in Railway variables
    channel = bot.get_channel(channel_id)
    if channel:
        fact = fetch_fact()
        await channel.send(fact)
    else:
        print("Channel not found. Ensure the CHANNEL_ID is correct.")


@bot.command()
async def fact(ctx):
    # Fetch fact from API Ninjas
    api_url = 'https://api.api-ninjas.com/v1/facts'
    response = requests.get(api_url, headers={'X-Api-Key': API_KEY})

    if response.status_code == 200:
        fact_data = response.json()[0]
        fact_text = fact_data['fact']

        # Create an embed
        embed = discord.Embed(
            title="Daily Fact",
            description=fact_text,
            color=random.randint(0, 0xFFFFFF)
        )
        # Optionally set an image (replace with a valid image URL)
        image_url = "https://cdn.discordapp.com/attachments/1296806815983734784/1297449756662038571/Fun_fact.gif?ex=6715f7bf&is=6714a63f&hm=8f5b221d5c274abf16ffade0f46d635e771f296a80a11e0d8cd2cb664af3cf89&"  # Replace with actual image URL
        embed.set_image(url=image_url)  # Set the image in the embed

        # Send the message in the channel
        message = await ctx.send(embed=embed)

        # Check if the channel is an announcement channel and publish the message
        if isinstance(ctx.channel, discord.TextChannel) and ctx.channel.is_news():
            await message.publish()
            await ctx.send("The fact has been published to all follower servers!")
        else:
            await ctx.send("This is not an announcement channel, so the fact was not published.")
    else:
        # Print the error details for debugging
        await ctx.send(f"Failed to fetch the fact. Error {response.status_code}: {response.text}")

# Adding the ping command directly in main.py
@bot.command(name='ping')
async def ping(ctx):
    print("Ping command executed!")  # Debugging line
    await ctx.send("Pong!")


@bot.event
async def on_ready():
    if not send_daily_fact.is_running():
        send_daily_fact.start()
    print(f"Logged in as {bot.user}")

keep_alive()
bot.run(os.environ["DISCORD_TOKEN"])
