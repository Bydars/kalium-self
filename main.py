from discord.ext import commands
import discord
import asyncio
import os
import aiohttp
from colorama import init, Fore, Style
from pypresence import Presence
import threading
import time

COMMAND_PREFIX = "."
DEFAULT_ACTIVITY = discord.Game(name="Kalium ☢️")
RPC_CLIENT_ID = "client_id"  

init()
print(Fore.CYAN + "╔════════════════════════════════════════════╗")
print("║" + Fore.LIGHTGREEN_EX + "             🔐  Kalium Selfbot             " + Fore.CYAN + "║")
print("║" + Fore.LIGHTBLUE_EX + "        Custom Presence & DM Utility        " + Fore.CYAN + "║")
print("╚════════════════════════════════════════════╝" + Style.RESET_ALL)

token = input("🔑 Enter your token: ").strip()
class KaliumRPC:
    def __init__(self, client_id):
        self.client_id = client_id
        self.rpc = None
        self.running = True
        self.state = "streaming"
        self.details = "Kalium ☢️"
        self.image = "change-me"

    def start(self):
        def run():
            try:
                self.rpc = Presence(self.client_id)
                self.rpc.connect()
                while self.running:
                    self.rpc.update(
                        state=self.state,
                        details=self.details,
                        large_image=self.image,
                        large_text="Kalium Selfbot",
                        start=time.time()
                    )
                    time.sleep(15)
            except Exception as e:
                print(f"[RPC Error] {e}")

        threading.Thread(target=run, daemon=True).start()

    def update_status(self, status_text, status_type):
        self.state = f"{status_type} {status_text}"


kalium_rpc = KaliumRPC(RPC_CLIENT_ID)
kalium_rpc.start()

bot = commands.Bot(command_prefix=COMMAND_PREFIX, self_bot=True, help_command=None)

@bot.event
async def on_ready():
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
        "📝 `.embed` – Create a styled embed using prompts\n"
        "📨 `.dm [guild_id] [amount] [message]` – Sends a DM to members max 50 (non-admins, open DMs only)\n"
        "🧹 `.clear [amount]` – Deletes your messages\n"
        "📦 `.emojis [guild_id] (opcional_path)` – Save all emojis and stickers from the server\n"
        "📬 `.reopendm` – Reopens recent closed DMs by sending invisible messages\n"
        "👋 `.logout` – Shut down Kalium\n"
    )
    await ctx.send(msg)

@bot.command()
async def activity(ctx, type: str, *, text: str):
    await ctx.message.delete()

    rpc_types = {
        "playing": "Playing",
        "streaming": "Streaming",
        "listening": "Listening to",
        "watching": "Watching"
    }

    type = type.lower()
    if type not in rpc_types:
        return await ctx.send("❌ Invalid type. Use: playing, streaming, listening, watching", delete_after=6)

    try:
        kalium_rpc.update_status(text, rpc_types[type])
        await ctx.send(f"✅ Rich Presence updated:\n• Type: `{type}`\n• Text: `{text}`")
    except Exception as e:
        await ctx.send(f"❌ Failed to update RPC: {str(e)}", delete_after=6)

@bot.command()
async def embed(ctx):
    await ctx.message.delete()

    def check(m): return m.author == ctx.author and m.channel == ctx.channel

    await ctx.send("📝 Enter the title:")
    title = await bot.wait_for("message", check=check)
    await title.delete()

    await ctx.send("📝 Enter the description:")
    desc = await bot.wait_for("message", check=check)
    await desc.delete()

    message = (
        f"📣 **{title.content}**\n"
        f"{desc.content}"
    )

    await ctx.send(message)

@bot.command()
async def clear(ctx, amount: int = 5):
    await ctx.message.delete()
    deleted = 0

    try:
        async for msg in ctx.channel.history(limit=1000):
            if msg.author == bot.user:
                try:
                    await msg.delete()
                    deleted += 1
                    await asyncio.sleep(0.25)
                    if deleted >= amount:
                        break
                except discord.HTTPException:
                    continue
        await ctx.send(f"🧹 Cleared {deleted} messages.", delete_after=4)
    except Exception as e:
        await ctx.send(f"❌ Error while clearing: {e}", delete_after=6)

@bot.command()
async def dm(ctx, guild_id: int, cantidad: int, *, mensaje: str):
    await ctx.message.delete()

    if cantidad > 50:
        await ctx.send("⚠️ Maximum limit is 50 users. Sending to first 50 members...", delete_after=6)
    cantidad = min(cantidad, 50)

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
            await asyncio.wait_for(member.send(mensaje), timeout=4)
            print(f"✅ Sent to {member}")
            count_sent += 1
        except (discord.Forbidden, discord.HTTPException):
            print(f"⛔ Cannot DM {member}")
            count_skipped += 1
        except asyncio.TimeoutError:
            print(f"⏳ Timeout while trying to DM {member}")
            count_failed += 1
        except Exception as e:
            print(f"❌ Error with {member}: {e}")
            count_failed += 1

        await asyncio.sleep(1.5)

    await ctx.send(
        f"📨 Done sending messages.\n✅ Sent: {count_sent}\n⛔ Skipped (DMs/Admin): {count_skipped}\n❌ Failed: {count_failed}",
        delete_after=10
    )


@bot.command()
async def emojis(ctx, guild_id: int, *, path: str = None):
    await ctx.message.delete()

    guild = discord.utils.get(bot.guilds, id=guild_id)
    if not guild:
        return await ctx.send("❌ Guild not found.", delete_after=5)

    base_dir = os.path.abspath(path or os.path.join("stickers", str(guild.id)))
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
                print(f"❌ Failed to download emoji {emoji.name}: {e}")

        for sticker in guild.stickers:
            url = str(sticker.url)
            ext = "png" if "image" in sticker.format else "json"
            file_path = os.path.join(sticker_dir, f"{sticker.name}.{ext}")
            try:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        with open(file_path, "wb") as f:
                            f.write(await resp.read())
            except Exception as e:
                print(f"❌ Failed to download sticker {sticker.name}: {e}")

    await ctx.send(f"📦 Assets saved to: `{base_dir}`", delete_after=7)

@bot.command()
async def reopendm(ctx):
    await ctx.message.delete()
    reopened = 0
    skipped = 0

    for dm in bot.private_channels:
        if isinstance(dm, discord.DMChannel):
            try:
                await dm.send("\u200b")  
                reopened += 1
                await asyncio.sleep(1)  
            except Exception:
                skipped += 1

    await ctx.send(
        f"📬 Attempted to reopen {reopened + skipped} DMs.\n✅ Success: {reopened}\n❌ Skipped/Failed: {skipped}",
        delete_after=8
    )

@bot.command()
async def logout(ctx):
    await ctx.message.delete()
    await ctx.send("👋 Kalium shutting down...")
    await bot.close()

bot.run(token)