
import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
import pymysql
from discord_slash.utils.manage_commands import create_option

mydb = pymysql.connect(
    host="localhost",
    user="ploopitadmin",
    password="Pr0jectPl00p1t!!",
    database="Login",
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor,
)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
slash = SlashCommand(bot, sync_commands=True)

@bot.event
async def on_ready():
    print(f"Bot is connected as {bot.user}")

@bot.command(name="says", description="says stuff")
async def say(ctx, message: str):
    if message == "@everyone" or message == "@here":
        await ctx.send("I'm not pinging everyone.")
    else:
        await ctx.send(message)

@slash.slash(
    name="test",
    description="Test slash command",
    options=[
        create_option(
            name="option",
            description="Test option",
            option_type=3,
            required=True
        )
    ]
)
async def test(ctx: SlashContext, option: str):
    await ctx.send(f"Test slash command response with option: {option}")

@bot.event
async def on_slash_command_error(ctx, ex):
    # Handle any error that occurs during slash command execution
    await ctx.send(f"An error occurred: {ex}")


# Run the Discord bot
bot.run('MTEwOTYwNTMzNDAzMDQ4NzczMw.GgFmz8.opu1LUgtzT6pT9iacNqTIE4VWU7-3I0WOH9uRE')
