from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtCore import QFileSystemWatcher, QCoreApplication, QObject, Signal, Slot
import threading
import requests
import keyboard
import pymem
import pymem.process
import win32api
import win32con
import win32gui
from pynput.mouse import Controller, Button
from win32gui import GetWindowText, GetForegroundWindow
import json
import os
import sys
import time

def aim():
    print("Aim process started.")
    # Путь к файлу конфигурации
    config_dir = f"{os.environ['LOCALAPPDATA']}\\temp\\SpectrusCS"
    config_path = os.path.join(config_dir, "config.json")
    
    # Дефолтные настройки
    default_settings = {
        'esp_rendering': 1,
        'esp_mode': 1,
        'keyboard': "C",
        'aim_active': 1,
        'aim_mode': 1,
        'radius': 20,
        'aim_mode_distance': 1
    }
    
    def get_window_size(window_name="Counter-Strike 2"):
        hwnd = win32gui.FindWindow(None, window_name)
        if hwnd:
            rect = win32gui.GetClientRect(hwnd)
            width = rect[2] - rect[0]
            height = rect[3] - rect[1]
            return width, height
        return 1920, 1080  # Дефолтное значение, если окно не найдено
    
    
    # Функция загрузки настроек
    def load_settings():
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    settings = json.load(f)
                    return settings
            except json.JSONDecodeError:
                pass  # Ошибка в чтении файла конфигурации, возвращаем дефолтные настройки
        return default_settings
    
    def get_offsets_and_client_dll():
        offsets = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/refs/heads/main/output/offsets.json').json()
        client_dll = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/refs/heads/main/output/client_dll.json').json()
        return offsets, client_dll
    
    def w2s(mtx, posx, posy, posz, width, height):
        screenW = (mtx[12] * posx) + (mtx[13] * posy) + (mtx[14] * posz) + mtx[15]
    
        if screenW > 0.001:
            screenX = (mtx[0] * posx) + (mtx[1] * posy) + (mtx[2] * posz) + mtx[3]
            screenY = (mtx[4] * posx) + (mtx[5] * posy) + (mtx[6] * posz) + mtx[7]
    
            camX = width / 2
            camY = height / 2
    
            x = camX + (camX * screenX / screenW)//1
            y = camY - (camY * screenY / screenW)//1
    
            return [x, y]
    
        return [-999, -999]
    
    def esp(pm, client, offsets, client_dll, settings, target_list, window_size):
        width, height = window_size
        if settings['aim_active'] == 0:
            return
        
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
    
        view_matrix = []
        for i in range(16):
            temp_mat_val = pm.read_float(client + dwViewMatrix + i * 4)
            view_matrix.append(temp_mat_val)
    
        local_player_pawn_addr = pm.read_longlong(client + dwLocalPlayerPawn)
    
        try:
            local_player_team = pm.read_int(local_player_pawn_addr + m_iTeamNum)
        except:
            return
    
        for i in range(64):
            entity = pm.read_longlong(client + dwEntityList)
    
            if not entity:
                continue
    
            list_entry = pm.read_longlong(entity + ((8 * (i & 0x7FFF) >> 9) + 16))
    
            if not list_entry:
                continue
    
            entity_controller = pm.read_longlong(list_entry + (120) * (i & 0x1FF))
    
            if not entity_controller:
                continue
    
            entity_controller_pawn = pm.read_longlong(entity_controller + m_hPlayerPawn)
    
            if not entity_controller_pawn:
                continue
    
            list_entry = pm.read_longlong(entity + (0x8 * ((entity_controller_pawn & 0x7FFF) >> 9) + 16))
    
            if not list_entry:
                continue
    
            entity_pawn_addr = pm.read_longlong(list_entry + (120) * (entity_controller_pawn & 0x1FF))
    
            if not entity_pawn_addr or entity_pawn_addr == local_player_pawn_addr:
                continue
            
            entity_alive = pm.read_int(entity_pawn_addr + m_lifeState)
    
            if entity_alive != 256:
                continue
            entity_team = pm.read_int(entity_pawn_addr + m_iTeamNum)
    
            if entity_team == local_player_team and settings['esp_mode'] == 0:
                continue
    
            game_scene = pm.read_longlong(entity_pawn_addr + m_pGameSceneNode)
            bone_matrix = pm.read_longlong(game_scene + m_modelState + 0x80)
    
            try:
                # Выбор кости для прицеливания в зависимости от aim_mode
                if settings['aim_mode'] == 1:
                    bone_id = 6  # Кость головы
                else:
                    bone_id = 4  # Кость "spine"
    
                headX = pm.read_float(bone_matrix + bone_id * 0x20)
                headY = pm.read_float(bone_matrix + bone_id * 0x20 + 0x4)
                headZ = pm.read_float(bone_matrix + bone_id * 0x20 + 0x8)
    
                head_pos = w2s(view_matrix, headX, headY, headZ, width, height)
                legZ = pm.read_float(bone_matrix + 28 * 0x20 + 0x8)
                leg_pos = w2s(view_matrix, headX, headY, legZ, width, height)
    
                deltaZ = abs(head_pos[1] - leg_pos[1])
    
                if head_pos[0] != -999 and head_pos[1] != -999:
                    if settings['aim_mode_distance'] == 1:
                        target_list.append({
                            'pos': head_pos,
                            'deltaZ': deltaZ
                        })
                    else:
                        target_list.append({
                            'pos': head_pos,
                            'deltaZ': None
                        })
    
            except Exception as e:
                pass
    
        return target_list
    
    
    def aimbot(target_list, radius, aim_mode_distance):
        if not target_list:
            return
        
        center_x = win32api.GetSystemMetrics(0) // 2
        center_y = win32api.GetSystemMetrics(1) // 2
        
        if radius == 0:
            # Когда радиус равен 0, просто выбираем ближайшую цель
            closest_target = None
            closest_dist = float('inf')
    
            for target in target_list:
                dist = ((target['pos'][0] - center_x) ** 2 + (target['pos'][1] - center_y) ** 2) ** 0.5
    
                if dist < closest_dist:
                    closest_target = target['pos']
                    closest_dist = dist
    
        else:
            # Когда радиус не равен 0, учитываем радиус
            screen_radius = radius / 100.0 * min(center_x, center_y)
            closest_target = None
            closest_dist = float('inf')
    
            if aim_mode_distance == 1:
                target_with_max_deltaZ = None
                max_deltaZ = -float('inf')
    
                for target in target_list:
                    dist = ((target['pos'][0] - center_x) ** 2 + (target['pos'][1] - center_y) ** 2) ** 0.5
    
                    if dist < screen_radius and target['deltaZ'] > max_deltaZ:
                        max_deltaZ = target['deltaZ']
                        target_with_max_deltaZ = target
    
                closest_target = target_with_max_deltaZ['pos'] if target_with_max_deltaZ else None
    
            else:
                for target in target_list:
                    dist = ((target['pos'][0] - center_x) ** 2 + (target['pos'][1] - center_y) ** 2) ** 0.5
    
                    if dist < screen_radius and dist < closest_dist:
                        closest_target = target['pos']
                        closest_dist = dist
    
        if closest_target:
            target_x, target_y = closest_target
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(target_x - center_x), int(target_y - center_y), 0, 0)
    
    
    def main(settings):
        offsets, client_dll = get_offsets_and_client_dll()
        window_size = get_window_size()  # Получение размеров окна

        pm = pymem.Pymem("cs2.exe")
        client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll

        while True:
            target_list = esp(pm, client, offsets, client_dll, settings, [], window_size)

            # Aimbot logic
            if keyboard.is_pressed(settings['keyboard']):  # Используем keyboard для проверки нажатия
                aimbot(target_list, settings['radius'], settings['aim_mode_distance'])
            time.sleep(0.01)
    
    # Обработчик изменения файла конфигурации
    
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
            settings.update(new_settings)
    
        watcher.fileChanged.connect(reload_settings)
        app.exec()
    
    # Главная функция
    def main_program():
        app = QCoreApplication(sys.argv)
    
        settings = load_settings()
        threading.Thread(target=start_main_thread, args=(settings,), daemon=True).start()
    
        setup_watcher(app, settings)
    
    main_program()
    
