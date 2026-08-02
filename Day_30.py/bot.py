#-------------------------------------------------------
# you need to install "discord.py" python-dotenv first
# python -m pip install"discord.py" python-dotenv
#-------------------------------------------------------

import os
import random
import re
import asyncio
from datetime import datetime, timezone

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import requests

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")


intents                  = discord.Intents.default()
intents.message_content  = True
intents.members          = True

bot = commands.Bot(command_prefix="!", intents=intents)


start_time     = datetime.now(timezone.utc)
command_count  = 0

FACTS = [
    "Python was named after Monty Python, not the snake.",
    "The first computer bug was an actual bug — a moth found in a relay in 1947.",
    "There are over 700 programming languages in existence.",
    "The average programmer writes 10–12 lines of production code per day.",
    "'Hello, World!' was first used in a 1972 C programming tutorial.",
    "Git was created by Linus Torvalds in just 10 days in 2005.",
    "JavaScript was written in 10 days by Brendan Eich in 1995.",
    "The first 1GB hard drive (1980) weighed 550 lbs and cost $40,000.",
]

WEATHER_CODES = {
    0: ("Clear sky"), 1: ("Mainly clear"),
    2: ("Partly cloudy"), 3: ("Overcast",),
    61: ("Slight rain"), 63: ("Moderate rain"),
    71: ("Snow"), 95: ("Thunderstorm"),
}



def make_embed(title: str, description: str = "",
               colour: int = 0x2563EB) -> discord.Embed:
    embed = discord.Embed(title=title, description=description, colour=colour)
    embed.set_footer(text=f"Requested at {datetime.now().strftime('%H:%M')}")
    return embed

def get_weather(city: str) -> discord.Embed | None:
    try:
        geo = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": city, "format": "json", "limit": 1},
            headers={"User-Agent": "DiscordWeatherBot/1.0"},
            timeout=8,
        ).json()
        if not geo:
            return None
        lat, lon = geo[0]["lat"], geo[0]["lon"]

        wx = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat, "longitude": lon,
                "current": "temperature_2m,weather_code,wind_speed_10m,"
                           "relative_humidity_2m",
                "timezone": "auto",
            },
            timeout=8,
        ).json()["current"]

        code        = wx["weather_code"]
        desc, emoji = WEATHER_CODES.get(code, ("Unknown"))
        embed       = make_embed(f"{emoji} Weather in {city.title()}",
                                 colour=0x0EA5E9)
        embed.add_field(name="Condition",    value=desc,                   inline=True)
        embed.add_field(name="Temperature",  value=f"{wx['temperature_2m']}°C", inline=True)
        embed.add_field(name="Wind",         value=f"{wx['wind_speed_10m']} km/h", inline=True)
        embed.add_field(name="Humidity",     value=f"{wx['relative_humidity_2m']}%", inline=True)
        return embed
    except Exception:
        return None



@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="for !help"
        )
    )
    daily_fact.start()
    print(f"  Logged in as {bot.user} (id: {bot.user.id})")
    print(f"  Serving {len(bot.guilds)} server(s)")

@bot.event
async def on_command(ctx):
    global command_count
    command_count += 1

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f" Missing argument. Try `!help {ctx.command}`")
    elif isinstance(error, commands.CommandNotFound):
        pass   
    else:
        await ctx.send(f" Error: {error}")



@bot.command(name="ping", help="Check bot latency")
async def ping(ctx):
    ms = round(bot.latency * 1000)
    await ctx.send(embed=make_embed(" Pong!", f"Latency: **{ms}ms**",
                                    colour=0x22C55E if ms < 100 else 0xF59E0B))

@bot.command(name="fact", help="Get a random programming fact")
async def fact(ctx):
    await ctx.send(embed=make_embed(" Did you know?", random.choice(FACTS)))

@bot.command(name="roll", help="Roll dice — e.g. !roll 2d6")
async def roll(ctx, dice: str = "1d6"):
    m = re.fullmatch(r"(\d+)d(\d+)", dice.lower())
    if not m:
        await ctx.send(" Format: `!roll NdN` e.g. `!roll 2d6`")
        return
    n, sides = int(m.group(1)), int(m.group(2))
    if n > 20 or sides > 1000:
        await ctx.send(" Max 20 dice, 1000 sides.")
        return
    rolls  = [random.randint(1, sides) for _ in range(n)]
    total  = sum(rolls)
    detail = " + ".join(str(r) for r in rolls) + f" = **{total}**"
    embed  = make_embed(f" Rolling {dice.upper()}", detail, colour=0x8B5CF6)
    await ctx.send(embed=embed)

@bot.command(name="weather", help="Get weather — !weather London")
async def weather(ctx, *, city: str):
    async with ctx.typing():
        embed = get_weather(city)
    if embed:
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"Couldn't find weather for **{city}**.")

@bot.command(name="poll", help="Create a poll — !poll Question | Opt1 | Opt2 | Opt3")
async def poll(ctx, *, args: str):
    parts = [p.strip() for p in args.split("|")]
    if len(parts) < 2:
        await ctx.send(" Format: `!poll Question | Option1 | Option2`")
        return
    question = parts[0]
    options  = parts[1:7]   

    number_emojis = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣"]
    description   = "\n".join(
        f"{number_emojis[i]} {opt}" for i, opt in enumerate(options)
    )
    embed   = make_embed(f" {question}", description, colour=0xEC4899)
    message = await ctx.send(embed=embed)
    for emoji in number_emojis[:len(options)]:
        await message.add_reaction(emoji)

@bot.command(name="remind", help="Set a reminder — !remind 5 Take a break")
async def remind(ctx, minutes: float, *, message: str):
    if minutes <= 0 or minutes > 1440:
        await ctx.send(" Minutes must be between 1 and 1440.")
        return
    await ctx.send(
        f" Got it! I'll remind you about **{message}** in {minutes} minute(s)."
    )
    await asyncio.sleep(minutes * 60)
    try:
        await ctx.author.send(
            embed=make_embed(" Reminder!", message, colour=0xF97316)
        )
    except discord.Forbidden:
        await ctx.send(f" {ctx.author.mention} — reminder: **{message}**")

@bot.command(name="stats", help="Bot statistics")
async def stats(ctx):
    uptime  = datetime.now(timezone.utc) - start_time
    hours   = int(uptime.total_seconds() // 3600)
    minutes = int((uptime.total_seconds() % 3600) // 60)
    embed   = make_embed(" Bot Stats", colour=0x6366F1)
    embed.add_field(name="Uptime",   value=f"{hours}h {minutes}m", inline=True)
    embed.add_field(name="Servers",  value=str(len(bot.guilds)),    inline=True)
    embed.add_field(name="Commands used", value=str(command_count), inline=True)
    embed.add_field(name="Ping",     value=f"{round(bot.latency*1000)}ms", inline=True)
    await ctx.send(embed=embed)



@tasks.loop(hours=24)
async def daily_fact():
    
    for guild in bot.guilds:
        channel = discord.utils.get(guild.text_channels, name="general")
        if channel:
            await channel.send(
                embed=make_embed("📅 Daily Fact", random.choice(FACTS),
                                 colour=0x10B981)
            )

@daily_fact.before_loop
async def before_daily():
    await bot.wait_until_ready()



if __name__ == "__main__":
    
    bot.run(TOKEN)