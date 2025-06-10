# 🔐 Kalium Selfbot

**Kalium** is a powerful and aesthetic Discord selfbot written in Python. It features a clean console UI, DM automation, emoji/sticker saving, status customization, and built-in Discord Rich Presence (RPC) via `pypresence`.

---

## ⚙️ Features

- 🎮 Custom activity types (`playing`, `streaming`, `listening`, `watching`)
- 📝 Embed-style message creation
- 🧹 Fast self-message clearing
- 📬 Reopen closed DMs automatically
- 📦 Download emojis & stickers from any server
- 🧠 Live Rich Presence (RPC) support
- 🔐 Token-based login with custom status

---

## 📦 Requirements

Make sure you have **Python 3.9 or newer** installed.

### 🛠 Install dependencies manually:

```bash
pip install git+https://github.com/dolfies/discord.py-self.git
pip install aiohttp colorama pypresence
```

## 📄 Or install with a requirements.txt:

```txt
git+https://github.com/dolfies/discord.py-self.git
aiohttp
colorama
pypresence
```

## Then install everything at once:

```bash
pip install -r requirements.txt
```

### 🚀 How to Run
## Clone or download this repository.

## Open kalium.py and update your Rich Presence Client ID:
```py
RPC_CLIENT_ID = "ur_discord_bot_client_id"
```

# You must create a Discord Application at discord.com/developers/applications, go to Rich Presence > Art Assets, and upload your image size 1024x1024 (e.g. large) there.

## remember the name that you put when you upload
# now change this part of the code (line:30):

```py
large_image="change-me",
```

## Run Kalium from terminal:
```python
python kalium.py
```

## Paste your token when prompted.

## ✅ You're now logged in and Kalium Selfbot is active!

 📖 Available Commands
 Command	Description
 .activity [type] [text]	Set a custom activity (types: playing, streaming, listening, watching)
 .status [text]	Shortcut for .activity playing
 .embed	Create a styled message through prompt
 .dm [guild_id] [amount] [message]	DM up to 50 non-admin users with open DMs
 .clear [amount]	Delete your own messages in the channel
 .emojis [guild_id] (optional_path)	Download all emojis & stickers from the server
 .reopendm	Reopens closed DMs by sending blank messages
 .logout Shuts down Kalium selfbot safely
