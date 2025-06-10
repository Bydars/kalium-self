from discord.ext import commands
import discord
import asyncio
from colorama import init, Fore, Style
import aiohttp
import os


COMMAND_PREFIX = "."
DEFAULT_ACTIVITY = discord.Game(name="Kalium ☢️")

from colorama import init, Fore, Style
init()

print(Fore.CYAN + "╔════════════════════════════════════════════╗")
print("║" + Fore.LIGHTGREEN_EX + "             🔐  Kalium Selfbot             " + Fore.CYAN + "║")
print("║" + Fore.LIGHTBLUE_EX + "        Custom Presence & DM Utility        " + Fore.CYAN + "║")
print("╚════════════════════════════════════════════╝" + Style.RESET_ALL)


token = input("🔑 Enter your token: ").strip()

bot = commands.Bot(command_prefix=COMMAND_PREFIX, self_bot=True, help_command=None)

@bot.event
async def on_ready():
    await bot.change_presence(activity=DEFAULT_ACTIVITY)
    print(f"""
╔════════════════════════════════════════╗
✅ Logged in as: {bot.user}
📡 Default Status: {DEFAULT_ACTIVITY.name}
🧠 Kalium is fully loaded.
╚════════════════════════════════════════╝
""")

@bot.command()
async def help(ctx):
    await ctx.message.delete()
    msg = (
        "**🧠 Kalium Commands:**\n\n"
        "🎮 `.activity [type] [text]` – Set a custom activity. Types: playing, streaming, listening, watching\n"
        "🎮 `.status [text]` – Shortcut for `.activity playing`\n"
        "📝 `.embed` – Create a styled embed using prompts\n"
        "📨 `.dm [guild_id] [amount] [message]` – Sends a DM to members (non-admins, open DMs only)\n"
        "🧹 `.clear [amount]` – Deletes your messages\n"
        "📦 `.emojis [guild_id]` – Save all emojis and stickers from the server\n"
        "👋 `.logout` – Shut down Kalium\n"
    )
    await ctx.send(msg)

@bot.command()
async def activity(ctx, type: str, *, text: str):
    await ctx.message.delete()

    type = type.lower()
    if type == "playing":
        act = discord.Game(name=text)
    elif type == "streaming":
        act = discord.Streaming(name=text, url="https://twitch.tv/change-me")
    elif type == "listening":
        act = discord.Activity(type=discord.ActivityType.listening, name=text)
    elif type == "watching":
        act = discord.Activity(type=discord.ActivityType.watching, name=text)
    else:
        return await ctx.send("❌ Invalid type. Use: playing, streaming, listening, watching", delete_after=6)

    await bot.change_presence(activity=act)

    msg = f"✅ **Status updated**\n• Type: `{type}`\n• Text: `{text}`"
    await ctx.send(msg)

@bot.command()
async def status(ctx, *, text):
    await ctx.invoke(bot.get_command("activity"), type="playing", rest=text)

@bot.command()
async def embed(ctx):
    await ctx.message.delete()
    def check(m): return m.author == ctx.author and m.channel == ctx.channel

    await ctx.send("📝 Embed title:")
    title = await bot.wait_for("message", check=check)
    await title.delete()

    await ctx.send("📝 Embed description:")
    desc = await bot.wait_for("message", check=check)
    await desc.delete()

    await ctx.send("🎨 Hex color (e.g. #7289da):")
    color = await bot.wait_for("message", check=check)
    await color.delete()

    try:
        color_val = int(color.content.replace("#", "0x"), 16)
    except:
        color_val = 0x7289da

    final = (
        f"📣 **{title.content}**\n"
        f"{desc.content}\n\n"
        f"`Color: #{hex(color_val)[2:]}`"
    )

    await ctx.send(final)

@bot.command()
async def clear(ctx, amount: int = 5):
    await ctx.message.delete()
    count = 0
    async for msg in ctx.channel.history(limit=100):
        if msg.author == bot.user:
            try:
                await msg.delete()
                count += 1
                await asyncio.sleep(0.75)
                if count >= amount:
                    break
            except:
                continue
    await ctx.send(f"🧹 Cleared {count} messages.", delete_after=4)

@bot.command()
async def dm(ctx, guild_id: int, cantidad: int, *, mensaje: str):
    await ctx.message.delete()
    
    guild = discord.utils.get(bot.guilds, id=guild_id)
    if not guild:
        return await ctx.send("❌ Guild not found. Make sure you're in that server.", delete_after=5)

    count_sent = 0
    count_skipped = 0
    count_failed = 0

    for member in guild.members:
        if count_sent >= cantidad:
            break

        if member.bot or member == bot.user:
            continue

        if member.guild_permissions.administrator:
            count_skipped += 1
            continue

        try:
            await member.send(mensaje)
            print(f"✅ Sent to {member}")
            count_sent += 1
        except discord.Forbidden:
            print(f"⛔ Cannot DM {member} (DMs closed or blocked)")
            count_skipped += 1
        except Exception as e:
            print(f"❌ Error with {member}: {e}")
            count_failed += 1

        await asyncio.sleep(1.5) 

    await ctx.send(
        f"📨 Done.\n✅ Sent: {count_sent}\n⛔ Skipped (DMs/Admin): {count_skipped}\n❌ Failed: {count_failed}",
        delete_after=10
    )

@bot.command()
async def emojis(ctx, guild_id: int):
    await ctx.message.delete()

    guild = discord.utils.get(bot.guilds, id=guild_id)
    if not guild:
        return await ctx.send("❌ Guild not found.", delete_after=5)

    base_dir = os.path.join(os.getcwd(), "stickers", str(guild.id))
    emoji_dir = os.path.join(base_dir, "emojis")
    sticker_dir = os.path.join(base_dir, "stickers")

    os.makedirs(emoji_dir, exist_ok=True)
    os.makedirs(sticker_dir, exist_ok=True)

    async with aiohttp.ClientSession() as session:
        for emoji in guild.emojis:
            ext = "gif" if emoji.animated else "png"
            url = f"https://cdn.discordapp.com/emojis/{emoji.id}.{ext}"
            file_path = os.path.join(emoji_dir, f"{emoji.name}.{ext}")
            try:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        with open(file_path, "wb") as f:
                            f.write(await resp.read())
            except Exception as e:
                print(f"❌ Failed emoji {emoji.name}: {e}")

        for sticker in guild.stickers:
            url = str(sticker.url)
            file_path = os.path.join(sticker_dir, f"{sticker.name}.png")
            try:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        with open(file_path, "wb") as f:
                            f.write(await resp.read())
            except Exception as e:
                print(f"❌ Failed sticker {sticker.name}: {e}")

    await ctx.send(f"📦 Assets saved to: `stickers/{guild.id}`", delete_after=7)

@bot.command()
async def logout(ctx):
    await ctx.message.delete()
    await ctx.send("👋 Kalium shutting down...")
    await bot.close()

bot.run(token)