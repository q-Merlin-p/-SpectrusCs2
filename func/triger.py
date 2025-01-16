from PySide6.QtCore import QFileSystemWatcher, QCoreApplication, QObject, Signal, Slot
import threading
import requests
import pymem
import pymem.process
import win32api
from pynput.mouse import Controller, Button
from win32gui import GetWindowText, GetForegroundWindow
import json
import os
import sys
import time

def triggerbot():
    print("Triggerbot process started.")
    
    # Получение смещений и данных клиента из URL
    offsets = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/refs/heads/main/output/offsets.json').json()
    client_dll = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/refs/heads/main/output/client_dll.json').json()

    # Обновляем значения смещений
    dwEntityList = offsets['client.dll']['dwEntityList']
    dwLocalPlayerPawn = offsets['client.dll']['dwLocalPlayerPawn']
    dwViewMatrix = offsets['client.dll']['dwViewMatrix']
    dwPlantedC4 = offsets['client.dll']['dwPlantedC4']
    m_iTeamNum = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_iTeamNum']
    m_lifeState = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_lifeState']
    m_pGameSceneNode = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_pGameSceneNode']
    m_modelState = client_dll['client.dll']['classes']['CSkeletonInstance']['fields']['m_modelState']
    m_hPlayerPawn = client_dll['client.dll']['classes']['CCSPlayerController']['fields']['m_hPlayerPawn']
    m_iHealth = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_iHealth']
    m_iszPlayerName = client_dll['client.dll']['classes']['CBasePlayerController']['fields']['m_iszPlayerName']
    m_pClippingWeapon = client_dll['client.dll']['classes']['C_CSPlayerPawnBase']['fields']['m_pClippingWeapon']
    m_AttributeManager = client_dll['client.dll']['classes']['C_EconEntity']['fields']['m_AttributeManager']
    m_Item = client_dll['client.dll']['classes']['C_AttributeContainer']['fields']['m_Item']
    m_iItemDefinitionIndex = client_dll['client.dll']['classes']['C_EconItemView']['fields']['m_iItemDefinitionIndex']
    m_ArmorValue = client_dll['client.dll']['classes']['C_CSPlayerPawn']['fields']['m_ArmorValue']
    m_vecAbsOrigin = client_dll['client.dll']['classes']['CGameSceneNode']['fields']['m_vecAbsOrigin']
    m_flTimerLength = client_dll['client.dll']['classes']['C_PlantedC4']['fields']['m_flTimerLength']
    m_flDefuseLength = client_dll['client.dll']['classes']['C_PlantedC4']['fields']['m_flDefuseLength']
    m_bBeingDefused = client_dll['client.dll']['classes']['C_PlantedC4']['fields']['m_bBeingDefused']
    m_iIDEntIndex = client_dll['client.dll']['classes']['C_CSPlayerPawnBase']['fields']['m_iIDEntIndex']

    # Инициализация мыши
    mouse = Controller()

    # Путь к файлу конфигурации
    config_dir = f"{os.environ['LOCALAPPDATA']}\\temp\\SpectrusCS"
    config_path = os.path.join(config_dir, "config.json")

    # Дефолтные настройки
    default_settings = {
        "keyboards": "X",
        "trigger_bot_active": 1,
        "esp_mode": 1,
        "delay_before_shot": 0
    }

    # Функция загрузки настроек
    def load_settings():
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    settings = json.load(f)
                    return settings
            except json.JSONDecodeError as e:
                pass  # Ошибка в чтении файла конфигурации, возвращаем дефолтные настройки
        else:
            return default_settings

    def main(settings):
        pm = pymem.Pymem("cs2.exe")
        client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll
        
        while True:
            try:
                # Загрузка актуальных настроек каждый раз
                trigger_bot_active = settings["trigger_bot_active"]
                attack_all = settings["esp_mode"]
                keyboards = settings["keyboards"]
                delay_before_shot = settings.get("delay_before_shot", 0)

                # Проверка, что значение не 0 и корректное
                if isinstance(delay_before_shot, (int, float)) and delay_before_shot > 0:
                    delay_before_shot = delay_before_shot / 1000  # Переводим в секунды
                else:
                    delay_before_shot = 0.1  # Если ошибка, дефолтная задержка

                # Проверка, что окно активное
                if not GetWindowText(GetForegroundWindow()) == "Counter-Strike 2":
                    time.sleep(0.1)
                    continue

                # Проверка нажатия клавиши активации
                if win32api.GetAsyncKeyState(ord(keyboards)):
                    # Проверяем активен ли триггер-бот
                    if trigger_bot_active == 1:
                        try:
                            # Ждем перед выстрелом
                            time.sleep(delay_before_shot)
                            player = pm.read_longlong(client + dwLocalPlayerPawn)
                            
                            # Чтение ID сущности игрока
                            entityId = pm.read_int(player + m_iIDEntIndex)
                            
                            if entityId > 0:
                                # Чтение адреса списка сущностей
                                entList = pm.read_longlong(client + dwEntityList)
                                
                                # Чтение адреса сущности по ID
                                entEntry = pm.read_longlong(entList + 0x8 * (entityId >> 9) + 0x10)
                                entity = pm.read_longlong(entEntry + 120 * (entityId & 0x1FF))
                                
                                # Чтение команды игрока и команды сущности
                                entityTeam = pm.read_int(entity + m_iTeamNum)
                                playerTeam = pm.read_int(player + m_iTeamNum)
                                
                                # Определение условия для стрельбы
                                if (attack_all == 1) or (entityTeam != playerTeam and attack_all == 0):
                                    entityHp = pm.read_int(entity + m_iHealth)
                                    if entityHp > 0:
                                        time.sleep(0.03)
                                        mouse.press(Button.left)
                                        time.sleep(0.03)
                                        mouse.release(Button.left)

                        except Exception:
                            pass  # Игнорирование всех исключений

                    time.sleep(0.03)
                else:
                    time.sleep(0.1)

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Ошибка в основном цикле: {e}")
                time.sleep(1)


    # Обработчик изменения файла конфигурации
    def on_config_changed():
        print("Настройки обновлены")

    # Функция запуска основного цикла в отдельном потоке
    def start_main_thread(settings):
        while True:
            main(settings)

    # Функция инициализации QFileSystemWatcher
    def setup_watcher(app, settings):
        watcher = QFileSystemWatcher()
        watcher.addPath(config_path)

        def reload_settings():
            new_settings = load_settings()
            settings.update(new_settings)  # Обновляем настройки
            on_config_changed()

        watcher.fileChanged.connect(reload_settings)
        app.exec()

    # Главная функция
    def main_program():
        app = QCoreApplication(sys.argv)
        settings = load_settings()
        threading.Thread(target=start_main_thread, args=(settings,), daemon=True).start()
        setup_watcher(app, settings)

    main_program()

