#!/usr/bin/env python3

import config
import requests, sys, time, webbrowser
from wxpy import *

DEBUG_MODE = False
MAX_RETRY = 5
receivers = []

def init():
    bot = Bot()
    for receiver in config.receivers:
        receivers.append(bot.friends().search(receiver)[0])
    print(receivers)
    return len(receivers) != 0
    #embed()

def monitor():
    results = requests.get(config.check_url, headers=config.headers).json()
    stores = results['stores']
    messages = []
    reserve_urls = {}
    for store in config.stores:
        if store in stores:
            inventories = stores[store]
            for model in inventories:
                if inventories[model]['availability']['unlocked'] and model in config.models_selected:
                    storeName = config.stores[store]
                    modelName = config.models_selected[model]
                    messages.append('{} {}店有货！'.format(modelName, storeName))
                    reserve_urls[model] = config.reserve_url.format(store, model)
    most_desired = None
    for model in config.models_selected:
        if model in reserve_urls:
            print(reserve_urls[model])
            most_desired = reserve_urls[model]
            break
    if most_desired:
        webbrowser.open_new(most_desired)
    if messages:
        print(messages)
        for receiver in receivers:
            for msg in messages:
                receiver.send(msg)
        return True
    else:
        return False

def notify_error(count):
    for receiver in receivers:
            receiver.send('received exception {}/{} at {}'.format(count, MAX_RETRY, now()))

def now():
    return time.asctime(time.localtime(time.time()))

if __name__ == '__main__':
    if not DEBUG_MODE:
        if not init():
            print('init failed')
            sys.exit(0)

    count = 0
    done = False
    print('start monitoring')
    while(True):
        try:
            done = monitor()
        except Exception as e:
            count += 1
            print(e.messages, " at {}".format(now()))
            if count > MAX_RETRY:
                sys.exit(0)
            notify_error(count)
            time.sleep(30)
        if done:
            print("found @", now())
            if DEBUG_MODE:
                break
            time.sleep(60);
