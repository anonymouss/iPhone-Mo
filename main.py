#!/usr/bin/env python3

import config
import requests, time, webbrowser, traceback, threading
from wxpy import *
from pytimedinput import timedInput, timedKey

DEBUG_MODE = False
MAX_RETRIES = 100
receivers = []
stop_requested = False

def logout_cb():
    receivers.clear()
    input_text, timedout = timedInput("Logged out. Relogin? 1 for yes, 0 for no: ", timeout=60)
    relogin = (input_text == '1')
    if timedout or not relogin:
        print("Continue running without WeChat")
    else:
        init_wechat()


def init_wechat():
    bot = Bot(logout_callback=logout_cb)
    for receiver in config.receivers:
        receivers.append(bot.friends().search(receiver)[0])
    print(receivers)

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
                    store_name = config.stores[store]
                    model_name = config.models_selected[model]
                    messages.append('{} {}店有货！'.format(model_name, store_name))
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
        notify_receivers(messages)
        return True
    else:
        return False

def notify_error(error):
    for receiver in receivers:
            receiver.send('received exception: {} at {}'.format(error, now()))

def notify_receivers(messages):
    for receiver in receivers:
            for msg in messages:
                receiver.send(msg)

def now():
    return time.asctime(time.localtime(time.time()))


def user_request_exit():
    global stop_requested
    _, _ = timedKey("Press q/Q to stop monitor", allowCharacters="qQ", timeout=-1)
    stop_requested = True

if __name__ == '__main__':
    if not DEBUG_MODE:
        init_wechat()

    key_thread = threading.Thread(target=user_request_exit, name='key-event-thread')
    key_thread.setDaemon(True)
    key_thread.start()

    error_count = 0
    done = False
    print('start monitor')
    notify_receivers(['start monitor'])
    while(error_count < MAX_RETRIES):
        if stop_requested:
            print('user requests to stop.')
            break
        try:
            done = monitor()
        except Exception as e:
            error_count += 1
            print('Exception @ ', now())
            traceback.print_exc()
            notify_error(repr(e))
            time.sleep(60 * 5)
        if done:
            print("found @ ", now())
            if DEBUG_MODE:
                break
            time.sleep(60 * 5);

    print("Exit.")
    notify_receivers(['stop monitor'])
