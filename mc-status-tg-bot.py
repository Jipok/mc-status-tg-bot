#!/usr/bin/env python3
import sys
from dataclasses import dataclass
from typing import Optional
from mcstatus import MinecraftServer
import telegram
from telegram.update import Update
from telegram.ext import CallbackContext, CommandHandler, JobQueue, Job, Updater
from socket import timeout


@dataclass
class CheckTask:
    host: str
    port: int
    username: str
    chat_id: int
    msg_id: int
    status: str
    job: Optional[Job]


# PAST YOUR TOKEN HERE
BOT_TOKEN = ""
if not len(BOT_TOKEN):
    BOT_TOKEN = sys.argv[1]
    
bot = telegram.Bot(BOT_TOKEN)
updater = Updater(BOT_TOKEN, use_context=True)
tasks = {}

############################################################################################################

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Hi! I can track the number of players on a minecraft server.\n" 
        "Usage: /check host port\n"
        "For stop: /stop\n"
        "\n"
        "Usage example:\n"
        "1) Add me to your telegram group\n"
        "2) `/check 192.169.1.2 25565`\n"
        "3) Pin my message\n"
        "4) ???\n"
        "5) PROFIT!\n"
        "\n"
        "Source code:\n"
        "https://github.com/Jipok/mc-status-tg-bot\n"
        , parse_mode = "Markdown")


def check(context):
    info = context.job.context
    try:
        status = MinecraftServer(info.host, info.port).status()
        new_text = "Online: %i" % status.players.online
    except Exception as e:
        new_text = "Offline"

    if info.status != new_text:
        try:
            bot.edit_message_text(new_text, info.chat_id, info.msg_id)
            info.status = new_text
        except Exception as e:
            info.job.schedule_removal()
            print(info.host + ' checker removed')


def check_cmd(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    try:
        host = str(context.args[0])
        port = int(context.args[1])
        MinecraftServer(host, port).status()
    except (IndexError, ValueError):
        try:
            update.message.reply_text("Correct usage:\n/check host port")
        except:
            pass
        return
    except Exception as e:
        update.message.reply_text("Error: {}".format(e))
        return

    # Add job to queue and stop current one if there is a timer already
    if chat_id in tasks:
        task = tasks[chat_id]
        bot.edit_message_text("Stopped. Last " + task.status, task.chat_id, task.msg_id)
        task.job.schedule_removal()
    msg_id = update.message.reply_text("Started", disable_notification=True).message_id
    task = CheckTask(host, port, update.message.from_user.username, chat_id, msg_id, "", None)
    tasks[chat_id] = task
    print(task.username, host, port)

    # First try in 1th second. Then check every 15 seconds
    task.job = context.job_queue.run_repeating(check, 15, 1, context = task)


def stop(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    if chat_id in tasks:
        task = tasks[chat_id]
        task.job.schedule_removal()
        bot.edit_message_text("Stopped. Last " + task.status, task.chat_id, task.msg_id)
        del tasks[chat_id]
    else:
        update.message.reply_text("Nothing to stop")

############################################################################################################

# Get the dispatcher to register handlers
dp = updater.dispatcher
dp.add_handler(CommandHandler("check", check_cmd, pass_args=True, pass_job_queue=True,pass_chat_data=True))
dp.add_handler(CommandHandler("stop", stop))
dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("help", start))

# Start the Bot
updater.start_polling()
# Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
# SIGABRT. This should be used most of the time, since start_polling() is
# non-blocking and will stop the bot gracefully.
updater.idle()