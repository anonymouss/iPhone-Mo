#!/usr/bin/env python3

import config
import requests, time, webbrowser, traceback, threading, os
from wxpy import *
from pytimedinput import timedKey


DEBUG_MODE = False
MAX_RETRIES = 100
receivers = []
stop_requested = False
hint = "Press q/Q to stop monitor\n"
bot = None


def logout_cb():
    global hint
    receivers.clear()
    hint += "WeChat logged out, you can input r/R to relogin\n"
    print(hint)


# just to avoid clearing the screen
def login_cb():
    if os.path.exists('QR.png'):
        os.remove('QR.png')


def init_wechat():
    global hint
    bot = Bot(cache_path=True, login_callback=login_cb, logout_callback=logout_cb)
    print('{} login in successfully'.format(bot.self.name))
    for receiver in config.receivers:
        receivers.append(bot.friends().search(receiver)[0])
    if len(receivers) != 0:
        hint = hint.split('\n')[0] + '\n'
        print('Receivers:', end=' ')
        for recv in receivers:
            print(recv.name, end = ' ')
        print()
    else:
        print("No matched receiver found, please check receiver info")


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


def key_event_monitor():
    global stop_requested
    global hint
    while not stop_requested:
        print(hint)
        input_text, _ = timedKey(timeout=-1, allowCharacters='qQrR')
        if input_text == 'q' or input_text == 'Q':
            stop_requested = True
        elif (input_text == 'r' or input_text == 'R') and len(receivers) == 0:
            init_wechat()
        else:
            print("I can't understand your input")



if __name__ == '__main__':
    if not DEBUG_MODE:
        init_wechat()

    key_thread = threading.Thread(target=key_event_monitor, name='key-event-thread')
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
            print(hint)
            notify_error(repr(e))
            time.sleep(60 * 5)
        if done:
            print("found @ ", now())
            if DEBUG_MODE:
                break
            print(hint)
            time.sleep(60 * 5);

    print("Exit.")
    notify_receivers(['stop monitor'])
