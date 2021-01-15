#!/usr/bin/env python3
import sys
from dataclasses import dataclass
from mcstatus import MinecraftServer
import telegram
from telegram.ext import Updater, CommandHandler, CallbackContext, JobQueue
from socket import timeout


@dataclass
class CheckInfo:
    host: str
    port: int
    chat_id: int
    msg_id: int
    status: str
    job: JobQueue


# PAST YOUR TOKEN HERE
BOT_TOKEN = ""
if not len(BOT_TOKEN):
    BOT_TOKEN = sys.argv[1]
    
bot = telegram.Bot(BOT_TOKEN)
updater = Updater(BOT_TOKEN, use_context=True)

############################################################################################################

def start(update, context):
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


def check_cmd(update, context: CallbackContext):
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
    if 'job' in context.chat_data:
        info = context.chat_data['info']
        bot.edit_message_text("Stopped. Last " + info.status, info.chat_id, info.msg_id)
        context.chat_data['job'].schedule_removal()

    print(update.message.from_user.username, host, port)
    msg_id = update.message.reply_text("Started", disable_notification=True).message_id

    info = CheckInfo(host, port, chat_id, msg_id, "", JobQueue())
    # First try in 0th second. Then check every 15 seconds
    context.chat_data['job'] = context.job_queue.run_repeating(check, 15, 0, info)
    info.job = context.chat_data['job']
    context.chat_data['info'] = info


def stop(update, context):
    if 'job' in context.chat_data:
        context.chat_data['job'].schedule_removal()
        del context.chat_data['job']
        info = context.chat_data['info']
        bot.edit_message_text("Stopped. Last " + info.status, info.chat_id, info.msg_id)
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
