from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtCore import QFileSystemWatcher, QCoreApplication, QObject, Signal, Slot
import requests
import pymem
import pymem.process
import win32con
import win32gui
from pynput.mouse import Controller, Button
from win32gui import GetWindowText, GetForegroundWindow
import json
import os
import sys
import time
from .esp_colors import get_color_bones, get_color_t_bones, get_color_name_e, get_color_name_t, get_color_radius, get_color_watermark, get_e_line_color, get_t_line_color, hp_bar_t, hp_bar_e
from .esp_colors import get_head_t_color, get_head_e_color, get_box_color_t, get_box_color_e

def esp():
    print("ESP process started.")
    def load_settings():
        while True:
            try:
                config_dir = f"{os.environ['LOCALAPPDATA']}\\temp\\SpectrusCS"
                config_file = os.path.join(config_dir, "config.json")
                with open(config_file, "r") as f:
                    settings = json.load(f)
                break
            except:
                pass
    
        return settings
    
    # Определение собственного исключения
    class PainterError(Exception):
        pass
    
    # Функция для получения оффсетов и client.dll
    def get_offsets_and_client_dll():
        offsets = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/offsets.json').json()
        client_dll = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/client_dll.json').json()
        return offsets, client_dll
    
    # Функция для получения размеров клиентской зоны окна
    def get_window_size(window_title):
        hwnd = win32gui.FindWindow(None, window_title)
        if hwnd:
            rect = win32gui.GetClientRect(hwnd)
            return rect[2], rect[3]
        return None, None
    
    # Функция для перевода координат в экранные
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
    
    def draw_bones(painter, pm, bone_matrix, view_matrix, width, height, bones_color):

        bone_ids = {
            "head": 6,
            "neck": 5,
            "spine": 4,
            "pelvis": 0,
            "left_shoulder": 13,
            "left_elbow": 14,
            "left_wrist": 15,
            "right_shoulder": 9,
            "right_elbow": 10,
            "right_wrist": 11,
            "left_hip": 25,
            "left_knee": 26,
            "left_ankle": 27,
            "right_hip": 22,
            "right_knee": 23,
            "right_ankle": 24,
        }
    
        bone_connections = [
            ("head", "neck"),
            ("neck", "spine"),
            ("spine", "pelvis"),
            ("pelvis", "left_hip"),
            ("left_hip", "left_knee"),
            ("left_knee", "left_ankle"),
            ("pelvis", "right_hip"),
            ("right_hip", "right_knee"),
            ("right_knee", "right_ankle"),
            ("neck", "left_shoulder"),
            ("left_shoulder", "left_elbow"),
            ("left_elbow", "left_wrist"),
            ("neck", "right_shoulder"),
            ("right_shoulder", "right_elbow"),
            ("right_elbow", "right_wrist"),
        ]
    
        bone_positions = {}
    
        try:
            for bone_name, bone_id in bone_ids.items():
                boneX = pm.read_float(bone_matrix + bone_id * 0x20)
                boneY = pm.read_float(bone_matrix + bone_id * 0x20 + 0x4)
                boneZ = pm.read_float(bone_matrix + bone_id * 0x20 + 0x8)
    
                bone_pos = w2s(view_matrix, boneX, boneY, boneZ, width, height)
                if bone_pos[0] != -999 and bone_pos[1] != -999:
                    bone_positions[bone_name] = bone_pos
    
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            painter.setPen(QtGui.QPen(bones_color, 2))

            for connection in bone_connections:
                if connection[0] in bone_positions and connection[1] in bone_positions:
                    painter.drawLine(
                        bone_positions[connection[0]][0], bone_positions[connection[0]][1],
                        bone_positions[connection[1]][0], bone_positions[connection[1]][1]
                    )
        except Exception as e:
            print(f"Error drawing bones: {e}")

    # Основная функция ESP
    def esp(painter, pm, client, offsets, client_dll, window_width, window_height, settings):
        if settings['esp_rendering'] == 0:
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
        for i in range(32):
            temp_mat_val = pm.read_float(client + dwViewMatrix + i * 4)
            view_matrix.append(temp_mat_val)
    
        local_player_pawn_addr = pm.read_longlong(client + dwLocalPlayerPawn)
    
        try:
            local_player_team = pm.read_int(local_player_pawn_addr + m_iTeamNum)
        except:
            return
    
        no_center_x = window_width / 2
        no_center_y = window_height * 0.75
    
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
            
            settings = load_settings()

            line_e_color_values = get_e_line_color(settings)
            line_t_color_values = get_t_line_color(settings)
            
            name_e_values = get_color_name_e(settings)
            name_t_values = get_color_name_t(settings)

            hp_bar_e_values = hp_bar_e(settings)
            hp_bar_t_values = hp_bar_t(settings)

            bone_color_values = get_color_bones(settings)
            bone_t_color_values = get_color_t_bones(settings)

            radius_color_values = get_color_radius(settings)

            head_t_values = get_head_t_color(settings)
            head_e_values = get_head_e_color(settings)

            box_t_values = get_box_color_t(settings)
            box_e_values = get_box_color_e(settings)

            color = QtGui.QColor(0, 255, 0) if entity_team == local_player_team else QtGui.QColor(255, 0, 0) # тут цвет для собз противников зеленый + красный вроде
            line_color = QtGui.QColor(*line_t_color_values) if entity_team == local_player_team else QtGui.QColor(*line_e_color_values)
            name_color = QtGui.QColor(*name_t_values) if entity_team == local_player_team else QtGui.QColor(*name_e_values)
            hp_bar_color = QtGui.QColor(*hp_bar_t_values) if entity_team == local_player_team else QtGui.QColor(*hp_bar_e_values)
            bones_color = QtGui.QColor(*bone_t_color_values) if entity_team == local_player_team else QtGui.QColor(*bone_color_values)
            head_color = QtGui.QColor(*head_t_values) if entity_team == local_player_team else QtGui.QColor(*head_e_values)
            box_color = QtGui.QColor(*box_t_values) if entity_team == local_player_team else QtGui.QColor(*box_e_values)
            
            game_scene = pm.read_longlong(entity_pawn_addr + m_pGameSceneNode)
            bone_matrix = pm.read_longlong(game_scene + m_modelState + 0x80)
    
            try:
                headX = pm.read_float(bone_matrix + 6 * 0x20)
                headY = pm.read_float(bone_matrix + 6 * 0x20 + 0x4)
                headZ = pm.read_float(bone_matrix + 6 * 0x20 + 0x8) + 8
    
                head_pos = w2s(view_matrix, headX, headY, headZ, window_width, window_height)
    
                if settings['line_rendering'] == 1: # линия
                    legZ = pm.read_float(bone_matrix + 28 * 0x20 + 0x8)
                    leg_pos = w2s(view_matrix, headX, headY, legZ, window_width, window_height)
    
                    bottom_left_x = head_pos[0] - (head_pos[0] - leg_pos[0]) // 2
                    bottom_y = leg_pos[1]
    
                    painter.setRenderHint(QtGui.QPainter.Antialiasing)
                    painter.setPen(QtGui.QPen(line_color, 2)) # цвеи линий
                    painter.drawLine(bottom_left_x, bottom_y, no_center_x, no_center_y)
    
                legZ = pm.read_float(bone_matrix + 28 * 0x20 + 0x8)
                leg_pos = w2s(view_matrix, headX, headY, legZ, window_width, window_height)
    
                deltaZ = abs(head_pos[1] - leg_pos[1])
                leftX = head_pos[0] - deltaZ // 3
                rightX = head_pos[0] + deltaZ // 3
    
                if settings['box_rendering'] ==1:
                    painter.setRenderHint(QtGui.QPainter.Antialiasing)
                    painter.setPen(QtGui.QPen(box_color, 2))
                    painter.setBrush(QtCore.Qt.NoBrush)
                    painter.drawRect(QtCore.QRectF(leftX, head_pos[1], rightX - leftX, leg_pos[1] - head_pos[1]))

                if settings['line_corn_rendering'] == 1:  # Рисование углов
                    legZ = pm.read_float(bone_matrix + 28 * 0x20 + 0x8)
                    leg_pos = w2s(view_matrix, headX, headY, legZ, window_width, window_height)

                    deltaZ = abs(head_pos[1] - leg_pos[1])
                    leftX = head_pos[0] - deltaZ // 3
                    rightX = head_pos[0] + deltaZ // 3

                    painter.setRenderHint(QtGui.QPainter.Antialiasing)
                    painter.setPen(QtGui.QPen(box_color, 2))  # Цвет углов
                    painter.setBrush(QtCore.Qt.NoBrush)

                    # Рисование углов
                    # Верхний левый угол
                    painter.drawLine(leftX, head_pos[1], leftX + 10, head_pos[1])  # Горизонтальная линия
                    painter.drawLine(leftX, head_pos[1], leftX, head_pos[1] + 10)  # Вертикальная линия

                    # Верхний правый угол
                    painter.drawLine(rightX - 10, head_pos[1], rightX, head_pos[1])  # Горизонтальная линия
                    painter.drawLine(rightX, head_pos[1], rightX, head_pos[1] + 10)  # Вертикальная линия

                    # Нижний левый угол
                    painter.drawLine(leftX, leg_pos[1], leftX + 10, leg_pos[1])  # Горизонтальная линия
                    painter.drawLine(leftX, leg_pos[1], leftX, leg_pos[1] - 10)  # Вертикальная линия

                    # Нижний правый угол
                    painter.drawLine(rightX - 10, leg_pos[1], rightX, leg_pos[1])  # Горизонтальная линия
                    painter.drawLine(rightX, leg_pos[1], rightX, leg_pos[1] - 10)  # Вертикальная линия
                    
                if settings['hp_bar_rendering'] == 1: # хп бар
                    entity_hp = pm.read_int(entity_pawn_addr + m_iHealth)
                    max_hp = 100
                    hp_percentage = min(1.0, max(0.0, entity_hp / max_hp))
            
                    # Размеры полоски
                    hp_bar_width = 2
                    hp_bar_height = deltaZ
            
                    # Позиция полоски слева от хитбокса
                    hp_bar_x_left = leftX - hp_bar_width - 2  # Отступаем слева от хитбокса
                    hp_bar_y_top = head_pos[1]  # Верхняя точка полоски совпадает с верхней точкой хитбокса
            
                    # Отрисовка фона полоски
                    painter.setRenderHint(QtGui.QPainter.Antialiasing)
                    painter.setPen(QtGui.QPen(QtCore.Qt.NoPen))
                    painter.setBrush(QtGui.QColor(0, 0, 0))
                    painter.drawRect(QtCore.QRectF(hp_bar_x_left, hp_bar_y_top, hp_bar_width, hp_bar_height))
            
                    # Отрисовка текущего значения здоровья
                    painter.setPen(QtGui.QPen(hp_bar_color, 2))
                    current_hp_height = hp_bar_height * hp_percentage
                    hp_bar_y_bottom = hp_bar_y_top + hp_bar_height - current_hp_height  # Для вертикального уменьшения
                    painter.drawRect(QtCore.QRectF(hp_bar_x_left, hp_bar_y_bottom, hp_bar_width, current_hp_height))
    
                if settings['hp_text_rendering'] == 1:  # Условие для отрисовки текста HP
                    entity_hp = pm.read_int(entity_pawn_addr + m_iHealth)
                    max_hp = 100
                    hp_percentage = min(1.0, max(0.0, entity_hp / max_hp))

                    # Позиция текста справа от хитбокса
                    hp_text_x = rightX + 5  # Отступаем вправо от хитбокса
                    hp_text_y = head_pos[1] + (leg_pos[1] - head_pos[1]) / 5

                    # Отрисовка текста
                    painter.setPen(QtGui.QPen(hp_bar_color))  # Цвет такой же, как у полоски HP
                    font = QtGui.QFont('DejaVu Sans', 10, QtGui.QFont.Bold)  # Настройка шрифта
                    painter.setFont(font)
                    painter.drawText(hp_text_x, hp_text_y, f"{entity_hp}")
                    
                if settings['head_hitbox_rendering'] == 1:
                    head_hitbox_size = (rightX - leftX) / 5
                    head_hitbox_radius = head_hitbox_size * 2 ** 0.5 / 2
                    head_hitbox_x = leftX + 2.5 * head_hitbox_size
                    head_hitbox_y = head_pos[1] + deltaZ / 9
                    painter.setRenderHint(QtGui.QPainter.Antialiasing)
                    painter.setBrush(QtGui.QColor(head_color)) # голова
                    painter.drawEllipse(QtCore.QPointF(head_hitbox_x, head_hitbox_y), head_hitbox_radius, head_hitbox_radius)
    
                # Отрисовка костей, если включена в настройках
                if settings.get('bons', 0) == 1:
                    draw_bones(painter, pm, bone_matrix, view_matrix, window_width, window_height, bones_color)
    
                if settings.get('nickname', 0) == 1:
                    player_name = pm.read_string(entity_controller + m_iszPlayerName, 32)
                    settings = load_settings()

                    # Определяем параметры для выравнивания по ширине
                    font_size = max(6, min(18, deltaZ / 25))
                    font = QtGui.QFont('DejaVu Sans', font_size, QtGui.QFont.Bold)
                    
                    # Создаем QPainterPath для определения размера текста
                    path = QtGui.QPainterPath()
                    path.addText(0, 0, font, player_name)
                    text_rect = path.boundingRect()
                
                    name_x = head_pos[0] - text_rect.width() / 2  # Центрируем текст по горизонтали
                    name_y = head_pos[1] - deltaZ / 8  # Положение текста по вертикали
                
                    painter.setPen(QtGui.QPen(name_color, 2))
                    painter.setFont(font)  # Устанавливаем шрифт и размер
                
                    # Отрисовываем текст с выравниванием по центру
                    painter.drawText(name_x, name_y, player_name)
    
                # Проверка наличия переменной 'radius' в настройках
                if 'radius' in settings:
                    if settings['radius'] != 0:
                        settings = load_settings()
                        radius_color_values = get_color_radius(settings)
                        # Получаем центр экрана
                        center_x = window_width / 2
                        center_y = window_height / 2
                    
                        # Преобразуем радиус из процентов в пиксели
                        screen_radius = settings['radius'] / 100.0 * min(center_x, center_y)
                    
                        # Отрисовка окружности
                        painter.setRenderHint(QtGui.QPainter.Antialiasing)
                        painter.setPen(QtGui.QPen(QtGui.QColor(*radius_color_values), 0.5))  # Тонкая белая линия
                        painter.setBrush(QtCore.Qt.NoBrush)
                        painter.drawEllipse(QtCore.QPointF(center_x, center_y), screen_radius, screen_radius)
                
            except:
                painter.end()
                return
    
    class ESPWindow(QtWidgets.QWidget):
        def __init__(self, settings):
            super().__init__()
            self.settings = settings
            self.setWindowTitle('ESP Overlay')
            
            self.fps_x = self.settings.get('fps_x', 10)
            self.fps_y = self.settings.get('fps_y', 20)
            self.dragging_fps = False  # Флаг для отслеживания перетаскивания
            
            # Получение размеров окна игры
            self.window_width, self.window_height = get_window_size("Counter-Strike 2")
            if self.window_width is None or self.window_height is None:
                print("Ошибка: окно игры не найдено.")
                sys.exit(1)
    
            self.setGeometry(0, 0, self.window_width, self.window_height)
            self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
            self.setAttribute(QtCore.Qt.WA_NoSystemBackground)
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Tool)
    
            hwnd = self.winId()
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)
    
            # Настройка отслеживания изменений в конфигурационном файле
            config_dir = f"{os.environ['LOCALAPPDATA']}\\temp\\SpectrusCS"
            config_file = os.path.join(config_dir, "config.json")
            self.file_watcher = QFileSystemWatcher([config_file])
            self.file_watcher.fileChanged.connect(self.reload_settings)
    
            self.offsets, self.client_dll = get_offsets_and_client_dll()
            self.pm = pymem.Pymem("cs2.exe")
            self.client = pymem.process.module_from_name(self.pm.process_handle, "client.dll").lpBaseOfDll
    
            self.timer = QtCore.QTimer(self)
            self.timer.timeout.connect(self.update)
            self.timer.start(0)
    
            self.last_time = time.time()
            self.frame_count = 0
            self.fps = 0
    
        def reload_settings(self):
            # Перезагружаем настройки при изменении файла
            self.settings = load_settings()
            
            # Обновляем позиции FPS-счётчика
            self.fps_x = self.settings.get('fps_x', 10)
            self.fps_y = self.settings.get('fps_y', 20)
            
            # Обновляем размеры окна игры
            self.window_width, self.window_height = get_window_size("Counter-Strike 2")
            if self.window_width is None or self.window_height is None:
                print("Ошибка: окно игры не найдено.")
                sys.exit(1)
                
            self.setGeometry(0, 0, self.window_width, self.window_height)
            self.update()
    
        def paintEvent(self, event):
            painter = QtGui.QPainter(self)
            try:
                esp(painter, self.pm, self.client, self.offsets, self.client_dll, self.window_width, self.window_height, self.settings)
                
                # Отрисовка FPS
                if self.settings['fps_rendering'] == 1:
                    fps_color_values = get_color_watermark(self.settings)
                    # Рассчет FPS
                    current_time = time.time()
                    self.frame_count += 1
                    if current_time - self.last_time >= 1.0:
                        self.fps = self.frame_count
                        self.frame_count = 0
                        self.last_time = current_time

                    # Установка цвета и шрифта для текста FPS
                    #painter.setPen(QtGui.QPen(QtGui.QColor(*fps_color_values)))
                    #font = QtGui.QFont('DejaVu Sans', 12, QtGui.QFont.Bold)
                    #painter.setFont(font)
                    #painter.drawText(self.fps_x, self.fps_y, f"Spectrus | FPS: {self.fps}")

            except PainterError as e:
                print(f"Painter Error: {e}")

        def mousePressEvent(self, event):
            # Проверяем, если клик был в пределах текста FPS, включаем перетаскивание
            print(f"Mouse pressed at: {event.x()}, {event.y()}")
            if (self.fps_x - 20 <= event.x() <= self.fps_x + 120 and
                self.fps_y - 20 <= event.y() <= self.fps_y + 40):
                self.dragging_fps = True
                self.drag_start_x = event.x() - self.fps_x
                self.drag_start_y = event.y() - self.fps_y

        def mouseReleaseEvent(self, event):
            if self.dragging_fps:
                self.dragging_fps = False
                self.settings['fps_x'] = self.fps_x
                self.settings['fps_y'] = self.fps_y
                self.save_settings()  # Сохраняем новые координаты

        def mouseReleaseEvent(self, event):
            if self.dragging_fps:
                # Сохраняем новые координаты, когда отпускается кнопка
                self.dragging_fps = False
                self.settings['fps_x'] = self.fps_x
                self.settings['fps_y'] = self.fps_y                

        def save_settings(self):
            """Сохраняем настройки в config.json"""
            config_dir = f"{os.environ['LOCALAPPDATA']}\\temp\\SpectrusCS"
            config_file = os.path.join(config_dir, "config.json")
            
            try:
                with open(config_file, 'w') as f:
                    json.dump(self.settings, f, indent=4)
            except Exception as e:
                print(f"Ошибка при сохранении настроек: {e}")

    def main_window():
        settings = load_settings()  # Загружаем настройки
        # Запуск интерфейса в главном потоке
        app = QtWidgets.QApplication(sys.argv)
        window = ESPWindow(settings)
        window.show()

        sys.exit(app.exec())
    main_window()


