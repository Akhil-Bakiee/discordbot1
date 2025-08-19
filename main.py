import discord
import random
from discord.ext import commands, tasks
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import os



intents = discord.Intents.default()
intents.messages = True
intents.dm_messages = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Storage
compliment_storage = {}   # {user_id: {"anon": [], "public": []}}
optout_list = set()
SPOTLIGHT_USER = None
SPOTLIGHT_CHANNEL = "compliments"   # name of the channel where spotlight happens

@bot.event
async def on_ready():
    print(f"{bot.user} is online!")
    scheduler = AsyncIOScheduler()
    scheduler.add_job(daily_spotlight, "cron", hour=12)  # every day at 12:00 UTC
    scheduler.start()
    deliver_compliments.start()

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)

async def daily_spotlight():
    """Pick a random user for spotlight and announce it."""
    global SPOTLIGHT_USER
    guild = bot.guilds[0]  # first server only
    
    # Without members intent, we can't access the member list directly
    # Instead, we'll announce that spotlight is ready and users can nominate themselves
    SPOTLIGHT_USER = None
    
    channel = discord.utils.get(guild.text_channels, name=SPOTLIGHT_CHANNEL)
    if channel:
        await channel.send(
            f"🌟 **Daily Spotlight is now open!**\n"
            f"💌 To participate in today's spotlight:\n"
            f"– Use `!join_spotlight` to enter yourself\n"
            f"– The first person to join will be today's spotlight!\n"
            f"– Then others can send compliments using `!compliment public <message>` or DM me `!compliment anon <message>`"
        )

@bot.command()
async def compliment(ctx, mode: str, *, message: str):
    global SPOTLIGHT_USER
    if not SPOTLIGHT_USER:
        await ctx.send("❌ There's no spotlight right now.")
        return

    # Anonymous compliments (via DM only)
    if mode.lower() == "anon":
        if isinstance(ctx.channel, discord.DMChannel):
            compliment_storage[SPOTLIGHT_USER.id]["anon"].append(message)
            await ctx.send("💌 Your anonymous compliment has been saved!")
        else:
            await ctx.send("❌ Anonymous compliments can only be sent via DM.")
    
    # Public compliments (in server only)
    elif mode.lower() == "public":
        if isinstance(ctx.channel, discord.TextChannel):
            compliment_storage[SPOTLIGHT_USER.id]["public"].append(
                f"{ctx.author.display_name}: {message}"
            )
            await ctx.send(f"✅ Compliment for {SPOTLIGHT_USER.mention} has been noted!")
        else:
            await ctx.send("❌ Public compliments must be sent in the server.")
    else:
        await ctx.send("❌ Use `anon` or `public` as the mode.")

@tasks.loop(hours=24)
async def deliver_compliments():
    """Deliver compliments daily to the spotlighted user."""
    global SPOTLIGHT_USER
    if SPOTLIGHT_USER and compliment_storage.get(SPOTLIGHT_USER.id):
        compliments = compliment_storage[SPOTLIGHT_USER.id]

        # Build messages
        anon_text = "\n- ".join(compliments["anon"]) if compliments["anon"] else "None"
        public_text = "\n- ".join(compliments["public"]) if compliments["public"] else "None"

        # DM user
        try:
            await SPOTLIGHT_USER.send(
                f"💖 Compliments you received today:\n\n"
                f"✨ Public Compliments:\n{public_text}\n\n"
                f"🌸 Anonymous Compliments:\n{anon_text}"
            )
        except:
            print(f"Couldn't DM {SPOTLIGHT_USER}")

        # Post in channel
        guild = bot.guilds[0]
        channel = discord.utils.get(guild.text_channels, name=SPOTLIGHT_CHANNEL)
        if channel:
            await channel.send(
                f"💌 Compliments for {SPOTLIGHT_USER.mention} today:\n\n"
                f"✨ **Public**:\n{public_text}\n\n"
                f"🌸 **Anonymous**:\n{anon_text}"
            )

    # Reset
    SPOTLIGHT_USER = None
    compliment_storage.clear()

@bot.command()
async def join_spotlight(ctx):
    global SPOTLIGHT_USER
    if SPOTLIGHT_USER:
        await ctx.send(f"❌ Today's spotlight is already taken by {SPOTLIGHT_USER.mention}!")
        return
    
    if ctx.author.id in optout_list:
        await ctx.send("❌ You've opted out of spotlights. Use `!optin` to participate again.")
        return
    
    SPOTLIGHT_USER = ctx.author
    compliment_storage[SPOTLIGHT_USER.id] = {"anon": [], "public": []}
    
    await ctx.send(
        f"🌟 Congratulations {SPOTLIGHT_USER.mention}! You're today's spotlight!\n"
        f"💌 Everyone can now send you compliments:\n"
        f"– Use `!compliment public <message>` here to send with their name\n"
        f"– Or DM me `!compliment anon <message>` to stay anonymous"
    )

@bot.command()
async def optout(ctx):
    optout_list.add(ctx.author.id)
    await ctx.send("✅ You will no longer be spotlighted.")

@bot.command()
async def optin(ctx):
    optout_list.discard(ctx.author.id)
    await ctx.send("✅ You can now participate in spotlights again!")

@bot.command()
async def spotlight(ctx):
    await daily_spotlight()

@bot.command()
async def spotlight_random(ctx):
    global SPOTLIGHT_USER
    
    if SPOTLIGHT_USER:
        await ctx.send(f"❌ Today's spotlight is already taken by {SPOTLIGHT_USER.mention}!")
        return
    
    guild = ctx.guild
    members = [m for m in guild.members if not m.bot and m.id not in optout_list]
    
    if not members:
        await ctx.send("❌ No available members for spotlight!")
        return
    
    SPOTLIGHT_USER = random.choice(members)
    compliment_storage[SPOTLIGHT_USER.id] = {"anon": [], "public": []}
    
    await ctx.send(
        f"🌟 **Random spotlight selected: {SPOTLIGHT_USER.mention}!**\n"
        f"💌 Everyone can now send them compliments:\n"
        f"– Use `!compliment public <message>` here to send with your name\n"
        f"– Or DM me `!compliment anon <message>` to stay anonymous"
    )

@bot.command()
async def bothelp(ctx):
    help_text = """
🌟 **Compliment Bot Commands** 🌟

**📍 User Commands:**
`!join_spotlight` - Join today's spotlight (first person becomes the spotlight)
`!compliment public <message>` - Send a public compliment to spotlight user (in server)
`!compliment anon <message>` - Send anonymous compliment to spotlight user (via DM)
`!optout` - Opt out of being selected for future spotlights
`!optin` - Opt back into spotlight participation

**🔧 Admin/Testing Commands:**
`!spotlight` - Manually trigger a new daily spotlight announcement
`!spotlight_random` - Randomly select someone for spotlight immediately
`!bothelp` - Show this help message

**💡 How it works:**
1. Daily at 12:00 UTC, bot announces spotlight is open
2. First person to use `!join_spotlight` becomes today's spotlight
3. Others send compliments using the compliment commands
4. After 24 hours, all compliments are delivered to the spotlight user

**📝 Notes:**
• Public compliments must be sent in server channels
• Anonymous compliments must be sent via DM to the bot
• The bot posts in the "compliments" channel
    """
    await ctx.send(help_text)

# Run bot
token = os.getenv("TOKEN")
if not token:
    print("Error: No Discord bot token found! Please set the TOKEN environment variable.")
    exit(1)

bot.run(token)