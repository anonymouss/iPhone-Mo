#!/usr/bin/env python3

import config
import requests, sys, time
from wxpy import *

DEBUG_MODE = False
receivers = []

def init():
    bot = Bot()
    for receiver in config.receivers:
        receivers.append(bot.friends().search(receiver)[0])
    print(receivers)
    return len(receivers) != 0
    #embed()

def monitor():
    print('start monitor')
    results = requests.get(config.url, headers=config.headers).json()
    stores = results['stores']
    messages = []
    for store in config.stores:
        if store in stores:
            inventories = stores[store]
            for model in inventories:
                if inventories[model]['availability']['unlocked'] and model in config.models:
                    storeName = config.stores[store]
                    modelName = config.models[model]
                    messages.append('{} {}店有货！'.format(modelName, storeName))
    if messages:
        print(messages)
        for receiver in receivers:
            for msg in messages:
                receiver.send(msg)
        return True
    else:
        return False


if __name__ == '__main__':
    if not DEBUG_MODE:
        if not init():
            print('init failed')
            sys.exit(0)

    while(True):
        if monitor():
            print("found @",  time.asctime(time.localtime(time.time())))
            if DEBUG_MODE:
                break
            time.sleep(30);
