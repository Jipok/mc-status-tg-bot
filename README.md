Telegram bot that displays the number of playing players on a specified Minecraft server

You can try it without installing: [@mc_status_bot](https://t.me/mc_status_bot)
## Installation
1. Need python 3.7 or higher
2. `git clone https://github.com/Jipok/mc-status-tg-bot`
3. `cd mc-status-tg-bot`
4. `python3 -m venv venv`
5. `source venv/bin/activate`
6. `pip install -r requirements.txt`
7. Using [@BotFather](https://telegram.me/botfather), create a bot
8. Change the BOT_TOKEN in the script to value from [@BotFather](https://telegram.me/botfather)

## Run
#### Way 1
`python3 mc-status-tg-bot.py`
#### Way 2
Do it once: `chmod +x mc-status-tg-bot`

and then always call like this: `./mc-status-tg-bot`

### Usage
Write to the bot or add it to the group and write there:

`/check host port`

The bot will reply and update the message every 15 seconds. To stop updating:

`/stop`

**Tip:** Only one server per chat can be specified. When specifying a new one, old messages will stop updating.

**Tip:** You can pin a bot message so that everyone can easily see online count. For this, the bot was created.
