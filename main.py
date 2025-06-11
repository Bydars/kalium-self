from discord.ext import commands
import discord
import asyncio
import os
import sys
import re
import aiohttp
from colorama import init, Fore, Style
from pypresence import Presence
import threading
import time

COMMAND_PREFIX = "." 
DEFAULT_ACTIVITY = discord.Streaming(
    name="kalium",
    url="https://twitch.tv/bydars_"
)
RPC_CLIENT_ID = "1382363647702995074"

init(autoreset=True)

token = input("🔑 Enter your token: ").strip()

class KaliumRPC:
    def __init__(self, client_id):
        self.client_id = client_id
        self.rpc = None
        self.running = True

        self.details = "Fuck"
        self.state = "streaming kalium"
        self.large_image = "large"
        self.large_text = "Kalium Selfbot"
        self.small_image = "d"
        self.small_text = "Kalium Selfbot"
        self.party_id = "kalium-party-001"
        self.party_size = [1, 5]
        self.join_secret = "kalium-join-key"
        self.start_time = time.time()

    def start(self):
        def run():
            while self.running:
                try:
                    if self.rpc is None:
                        self.rpc = Presence(self.client_id)
                        self.rpc.connect()

                    self.rpc.update(
                        details=self.details,
                        state=self.state,
                        large_image=self.large_image,
                        large_text=self.large_text,
                        small_image=self.small_image,
                        small_text=self.small_text,
                        party_id=self.party_id,
                        party_size=self.party_size,
                        join=self.join_secret,
                        start=self.start_time
                    )
                except Exception as e:
                    print(f"[RPC Error] {e}")
                time.sleep(15)

        threading.Thread(target=run, daemon=True).start()

kalium_rpc = KaliumRPC(RPC_CLIENT_ID)

def startup_banner(user):
    print(Fore.CYAN + "╔════════════════════════════════════════════════════════════════╗")
    print("║" + Fore.LIGHTGREEN_EX + "                       🔐 Kalium Selfbot                " + Fore.CYAN + "║")
    print("║" + Fore.LIGHTBLUE_EX + "             Custom Presence | RPC | DM Utility           " + Fore.CYAN + "║")
    print("╠════════════════════════════════════════════════════════════════╣")
    print(f"║ 🤖 User: {Fore.LIGHTYELLOW_EX}{user.name}#{user.discriminator:<40}{Fore.CYAN}║")
    print(f"║ 🆔 ID: {Fore.LIGHTYELLOW_EX}{user.id:<54}{Fore.CYAN}║")
    print(f"║ 🎮 Presence: {Fore.LIGHTMAGENTA_EX}{DEFAULT_ACTIVITY.name:<44}{Fore.CYAN}║")
    print(f"║ 💀 RPC: {Fore.LIGHTGREEN_EX}{kalium_rpc.state:<44}{Fore.CYAN}║")
    print("╚════════════════════════════════════════════════════════════════╝" + Style.RESET_ALL)

bot = commands.Bot(command_prefix=COMMAND_PREFIX, self_bot=True, help_command=None)

@bot.event
async def on_ready():
    await bot.change_presence(activity=DEFAULT_ACTIVITY)
    kalium_rpc.start()
    startup_banner(bot.user)

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
        "📣 `.say [amount] [message]` – Sends a message multiple times (works in both DMs and channels)\n"
        "👋 `.logout` – Shut down Kalium\n"
    )
    await ctx.send(msg)

@bot.command()
async def activity(ctx, type: str = None, *, args: str = None):
    await ctx.message.delete()

    if not type or not args:
        return await ctx.send("❌ Usage: `.activity [type] [text]`", delete_after=6)

    type = type.lower()
    rpc_types = {
        "playing": "Playing",
        "streaming": "Streaming",
        "listening": "Listening to",
        "watching": "Watching"
    }

    if type not in rpc_types:
        return await ctx.send("❌ Invalid type. Use: playing, streaming, listening, watching", delete_after=6)

    try:
        if type == "playing":
            activity = discord.Game(name=args)
        elif type == "streaming":
            activity = discord.Streaming(name=args, url="https://twitch.tv/")
        elif type == "listening":
            activity = discord.Activity(type=discord.ActivityType.listening, name=args)
        elif type == "watching":
            activity = discord.Activity(type=discord.ActivityType.watching, name=args)

        await bot.change_presence(activity=activity)

        kalium_rpc.state = f"{rpc_types[type]} {args}"

        await ctx.send(f"✅ Presence updated: `{rpc_types[type]}` – `{args}`")

    except Exception as e:
        await ctx.send(f"❌ Error: {e}", delete_after=6)

@bot.command()
async def embed(ctx):
    await ctx.message.delete()

    def check(m): return m.author == ctx.author and m.channel == ctx.channel

    try:
        await ctx.send("📝 **Enter the title:** *(type `cancel` to abort)*")
        title = await bot.wait_for("message", check=check, timeout=60)
        if title.content.lower() == "cancel":
            return await ctx.send("❌ Embed creation canceled.", delete_after=4)
        await title.delete()

        await ctx.send("📝 **Enter the description:** *(type `cancel` to abort)*")
        desc = await bot.wait_for("message", check=check, timeout=60)
        if desc.content.lower() == "cancel":
            return await ctx.send("❌ Embed creation canceled.", delete_after=4)
        await desc.delete()

        formatted = (
            f"╔══════════════════════════╗\n"
            f"📣 **{title.content}**\n"
            f"{desc.content}\n"
            f"╚══════════════════════════╝"
        )

        await ctx.send(formatted)

    except asyncio.TimeoutError:
        await ctx.send("⌛ Timeout. Try again.", delete_after=5)
    except Exception as e:
        await ctx.send(f"❌ Error: `{e}`", delete_after=6)

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
        await ctx.send(f"🧹 Cleared {deleted} messages.",
        delete_after=11)
    except Exception as e:
        await ctx.send(f"❌ Error while clearing: {e}", delete_after=6)

@bot.command()
async def dm(ctx, guild_id: str, cantidad: str, *, mensaje: str):
    await ctx.message.delete()

    if not guild_id.isdigit() or not cantidad.isdigit():
        return await ctx.send("❌ Guild ID y cantidad deben ser números válidos.", delete_after=6)

    guild_id = int(guild_id)
    cantidad = int(cantidad)

    if cantidad > 50:
        await ctx.send("⚠️ Máximo 50 usuarios. Enviando solo a los primeros 50...", delete_after=6)
    cantidad = min(cantidad, 50)

    guild = discord.utils.get(bot.guilds, id=guild_id)
    if not guild:
        return await ctx.send("❌ No se encontró el servidor.", delete_after=5)

    sent, skipped, failed = 0, 0, 0
    members = [
        m for m in guild.members
        if not m.bot and m != bot.user and not m.guild_permissions.administrator
    ]
    for member in members[:cantidad]:
        try:
            await member.send(mensaje)
            print(f"✅ Sent to {member}")
            sent += 1
        except discord.Forbidden:
            print(f"⛔ Cannot DM {member} (forbidden - likely has DMs closed)")
            skipped += 1
        except discord.HTTPException:
            print(f"❌ HTTP error with {member}")
            failed += 1
        except Exception as e:
            print(f"❌ Error with {member}: {e}")
            failed += 1

        await asyncio.sleep(0.75)  # evita rate limit

    await ctx.send(
        f"📨 Finalizado.\n"
        f"✅ Enviados: {sent}\n"
        f"⛔ DMs cerrados o admin: {skipped}\n"
        f"❌ Fallidos: {failed}",
        delete_after=11
    )

def safe_filename(name):
    return re.sub(r'[<>:"/\\|?*]', '_', name)

@bot.command()
async def emojis(ctx, guild_id: int, *, path: str = None):
    await ctx.message.delete()

    guild = discord.utils.get(bot.guilds, id=guild_id)
    if not guild:
        return await ctx.send("❌ Guild not found.", delete_after=5)

    try:
        base_dir = os.path.abspath(path or os.path.join("stickers", str(guild.id)))
        if not os.path.isdir(base_dir):
            os.makedirs(base_dir, exist_ok=True)
    except Exception:
        base_dir = os.path.abspath(os.path.join("stickers", str(guild.id)))

    emoji_dir = os.path.join(base_dir, "emojis")
    sticker_dir = os.path.join(base_dir, "stickers")
    os.makedirs(emoji_dir, exist_ok=True)
    os.makedirs(sticker_dir, exist_ok=True)

    total_emojis = 0
    total_stickers = 0

    async with aiohttp.ClientSession() as session:
        for emoji in guild.emojis:
            ext = "gif" if emoji.animated else "png"
            filename = safe_filename(emoji.name)
            url = f"https://cdn.discordapp.com/emojis/{emoji.id}.{ext}"
            path = os.path.join(emoji_dir, f"{filename}.{ext}")
            try:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        with open(path, "wb") as f:
                            f.write(await resp.read())
                        total_emojis += 1
            except Exception as e:
                print(f"❌ Failed emoji {emoji.name}: {e}")

        for sticker in guild.stickers:
            filename = safe_filename(sticker.name)
            url = str(sticker.url)
            path = os.path.join(sticker_dir, f"{filename}.png")
            try:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        with open(path, "wb") as f:
                            f.write(await resp.read())
                        total_stickers += 1
            except Exception as e:
                print(f"❌ Failed sticker {sticker.name}: {e}")

    await ctx.send(f"📦 Saved {total_emojis} emojis and {total_stickers} stickers to: `{base_dir}`",
        delete_after=11)

@bot.command()
async def reopendm(ctx):
    await ctx.message.delete()

    reopened = 0
    skipped = 0

    targets = [
        dm for dm in bot.private_channels
        if isinstance(dm, discord.DMChannel) and dm.recipient and not dm.recipient.bot
    ]

    async def try_send(dm):
        nonlocal reopened, skipped
        try:
            await dm.send("\u200b")
            reopened += 1
        except Exception:
            skipped += 1

    await asyncio.gather(*(try_send(dm) for dm in targets))

    await ctx.send(
        f"📬 Attempted to reopen {reopened + skipped} DMs.\n"
        f"✅ Success: {reopened}\n"
        f"❌ Skipped/Failed: {skipped}",
        delete_after=11
    )

@bot.command()
async def say(ctx, cantidad: int, *, mensaje: str):
    await ctx.message.delete()

    if cantidad > 25:
        return await ctx.send("⚠️ Max 25 messages allowed per use.", delete_after=6)

    destino = ctx.channel

    sent = 0
    for _ in range(cantidad):
        try:
            await destino.send(mensaje)
            sent += 1
        except discord.HTTPException:
            break
        except Exception as e:
            return await ctx.send(f"❌ Stopped after {sent} messages.\nError: `{e}`", delete_after=6)

    try:
        await ctx.send(f"📣 Sent `{sent}` messages.", delete_after=5)
    except:
        pass

@bot.command()
async def logout(ctx):
    await ctx.message.delete()
    await ctx.send("👋 Kalium shutting down...")
    await bot.close()

while True:
    try:
        bot.run(token)
    except Exception as e:
        print(f"❌ Bot crashed: {e}")
        time.sleep(10)
        print("🔁 Attempting to reconnect...")