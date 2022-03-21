import time
import random
import datetime
import telepot
from telepot.loop import MessageLoop



def handle(msg):
    global bot
    global datetime
    chat_id = msg['chat']['id']
    command = msg['text']

    print('Got command: %s' % command)

    if command == '/hey':
        bot.sendMessage(chat_id, "Hey right back at ya!")
    elif command == '/time':
        bot.sendMessage(chat_id, str(datetime.datetime.now()))

tokenStr = ""
for ele in token: 
        tokenStr += ele

print("in bot.py now!")
print(tokenStr)
bot = telepot.Bot('5213493698:AAHAfFGdUtotyq1Lzl7OJv6FcinSdjXukGE')

print(bot.getMe())

if tried == True:
    MessageLoop(bot, handle).run_as_thread()
    print('I am listening ...') 
    while 1:
        time.sleep(10)
