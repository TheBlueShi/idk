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
CHANNEL_ID = int(os.environ('CHANNEL_ID'))

intents = discord.Intents.default()
intents.message_content = True
intents.presences = True
intents.guilds = True
intents.reactions = True

# Use the PREFIX from the config
bot = commands.Bot(command_prefix=">", intents=intents)

# Loop to send the fact every minute (for testing, change interval to 'days=1' for daily)
@tasks.loop(minutes=1)
async def fact_sender():
    channel = bot.get_channel(CHANNEL_ID)  # Use the channel ID from the Railway secret
    if channel:
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
            image_url = "https://cdn.discordapp.com/attachments/1296806815983734784/1297449756662038571/Fun_fact.gif?ex=6715f7bf&is=6714a63f&hm=8f5b221d5c274abf16ffade0f46d635e771f296a80a11e0d8cd2cb664af3cf89&"
            embed.set_image(url=image_url)  # Set the image in the embed

            # Send the message in the channel
            message = await channel.send(embed=embed)

            # Check if the channel is an announcement channel and publish the message
            if isinstance(channel, discord.TextChannel) and channel.is_news():
                await message.publish()
                await channel.send("The fact has been published to all follower servers!")
        else:
            await channel.send("Failed to fetch the fact. Please try again later.")


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
    if not fact_sender.is_running():
        fact_sender.start()
    print(f"Logged in as {bot.user}")

keep_alive()
bot.run(os.environ["DISCORD_TOKEN"])
