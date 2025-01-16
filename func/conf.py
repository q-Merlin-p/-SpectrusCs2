from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtCore import QFileSystemWatcher, QCoreApplication, QObject, Signal, Slot
from pynput.mouse import Controller, Button
from win32gui import GetWindowText, GetForegroundWindow
import json
import os
import sys

def resource_path(relative_path):
    """ Get the absolute path to the resource, works for dev and for PyInstaller. """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def configurator():
    def load_settings():
            config_dir = os.path.join(os.environ['LOCALAPPDATA'], 'temp', 'SpectrusCS')
            config_file = os.path.join(config_dir, 'config.json')
        
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)
        
            if not os.path.exists(config_file):
                default_settings = {
                    "esp_rendering": 1,
                    "box_rendering": 0,
                    "line_corn_rendering": 1,

                    "fps_rendering": 1,
                    "fps_x" : 30,
                    "fps_y" : 30,
                    
                    "bunnyHopActivity":0,
                    
                    "delay_before_shot": 0.2,

                    "esp_mode": 0,
                    "line_rendering": 1,
                    "hp_bar_rendering": 1,
                    "head_hitbox_rendering": 1,
                    "bons": 1,
                    "nickname": 1,
                    "radius": 14,
                    "keyboard": "X",
                    "aim_active": 1,
                    "aim_mode": 1,
                    "aim_mode_distance": 0,
                    "trigger_bot_active": 1,
                    "keyboards": "X",
                    "line_color_t_r": 122,
                    "line_color_t_g": 122,
                    "line_color_t_b": 255,
                    "line_color_t_alpha": 255,
                    "line_color_e_r": 255,
                    "line_color_e_g": 122,
                    "line_color_e_b": 255,
                    "line_color_e_alpha": 255,
                    "hp_bar_color_t_r": 122,
                    "hp_bar_color_t_g": 122,
                    "hp_bar_color_t_b": 255,
                    "hp_bar_color_t_alpha": 255,
                    "hp_bar_color_e_r": 255,
                    "hp_bar_color_e_g": 122,
                    "hp_bar_color_e_b": 255,
                    "hp_bar_color_e_alpha": 255,
                    "head_hitbox_color_t_r": 122,
                    "head_hitbox_color_t_g": 122,
                    "head_hitbox_color_t_b": 255,
                    "head_hitbox_color_t_alpha": 255,
                    "head_hitbox_color_e_r": 255,
                    "head_hitbox_color_e_g": 122,
                    "head_hitbox_color_e_b": 255,
                    "head_hitbox_color_e_alpha": 255,
                    "bones_color_t_r": 122,
                    "bones_color_t_g": 122,
                    "bones_color_t_b": 255,
                    "bones_color_t_alpha": 255,
                    "bones_color_e_r": 255,
                    "bones_color_e_g": 122,
                    "bones_color_e_b": 255,
                    "bones_color_e_alpha": 255,
                    "nickname_color_t_r": 122,
                    "nickname_color_t_g": 122,
                    "nickname_color_t_b": 255,
                    "nickname_color_t_alpha": 255,
                    "nickname_color_e_r": 255,
                    "nickname_color_e_g": 122,
                    "nickname_color_e_b": 255,
                    "nickname_color_e_alpha": 255,
                    "radius_aim_bot_color_r": 255,
                    "radius_aim_bot_color_g": 255,
                    "radius_aim_bot_color_b": 255,
                    "radius_aim_bot_color_alpha": 255,
                    "Watermark_fps_color_r": 122,
                    "Watermark_fps_color_g": 0,
                    "Watermark_fps_color_b": 0,
                    "Watermark_fps_color_alpha": 255,
                    "box_color_t_r": 122,
                    "box_color_t_g": 122,
                    "box_color_t_b": 122,
                    "box_color_t_alpha": 255,
                    "box_color_e_r": 122,
                    "box_color_e_g": 122,
                    "box_color_e_b": 255,
                    "box_color_e_alpha": 255
                }
                with open(config_file, "w") as f:
                    json.dump(default_settings, f, indent=4)
        
            with open(config_file, "r") as f:
                settings = json.load(f)
        
            return settings
    
    class ConfigWindow(QtWidgets.QWidget):
        def __init__(self):
            super().__init__()
            self.settings = load_settings()
            self.initUI()
    
            # Переменные для управления перемещением окна
            self.is_dragging = False
            self.drag_start_position = None


    
        def initUI(self):
            # Настройки окна
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
            self.setFixedSize(850, 680)  # Сделаем окно горизонтальным
            self.setStyleSheet("""
                QWidget {
                    background-color: rgb(27, 27, 34);
                    color: white;
                    font-family: 'DejaVu Sans';
                    border-radius: 10px;
                }
                QLabel {
                    font-size: 20px;
                }
                QPushButton {
                    background-color: rgb(46, 43, 63);
                    border: none;
                    padding: 10px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: rgb(66, 63, 83);
                }
                QCheckBox {
                    font-size: 18px;
                }
                QComboBox {
                    background-color: rgb(27, 27, 34);
                    border: 1px solid rgb(46, 43, 63);
                    padding: 5px;
                    border-radius: 5px;
                    color: white;
                    font-size: 18px;
                }
                QLineEdit {
                    background-color: rgb(27, 27, 34);
                    border: 1px solid rgb(46, 43, 63);
                    padding: 5px;
                    border-radius: 5px;
                    color: white;
                    font-size: 18px;
                }
                QSlider::groove:horizontal {
                    border: 1px solid rgb(46, 43, 63);
                    height: 35px;
                    background: rgb(32, 34, 45);
                }
                QSlider::handle:horizontal {
                    background: rgb(27, 27, 34);
                    border: 1px solid rgb(46, 43, 63);
                    width: 16px;
                    height: 16px;
                    border-radius: 8px;
                }
                QSlider::handle:horizontal:hover {
                    background: rgb(66, 63, 83);
                }
                .container {
                    background-color: rgb(32, 34, 45);
                    border-radius: 5px;
                    padding: 10px;
                }
                QScrollBar:vertical {
                background-color: rgb(32, 34, 45);
                width: 15px;
                margin: 15px 3px 15px 3px;
                border-radius: 4px;
                }
                QScrollBar::handle:vertical {
                    background-color: rgb(46, 43, 63);
                    min-height: 20px;
                    border-radius: 4px;
                }
                QScrollBar::handle:vertical:hover {
                    background-color: rgb(66, 63, 83);
                }
                QScrollBar::sub-line:vertical,
                QScrollBar::add-line:vertical {
                    height: 0px;
                }
            """)
        
            main_layout = QtWidgets.QHBoxLayout()

            # Создаем QStackedWidget для хранения страниц
            self.pages = QtWidgets.QStackedWidget()

            sidebar = QtWidgets.QWidget()
            sidebar.setFixedWidth(75)
            sidebar.setStyleSheet("background-color: rgb(46, 43, 63);")
            sidebar_layout = QtWidgets.QVBoxLayout(sidebar)
            sidebar_layout.setContentsMargins(0, 0, 0, 0)
            sidebar_layout.setSpacing(20)
            # Кнопки для страниц
            icon_path = resource_path("assets")

            self.shooting_button = self.create_icon_button(os.path.join(icon_path, "pistol.png"))
            self.view_button = self.create_icon_button(os.path.join(icon_path, "view.png"))
            self.settings_button = self.create_icon_button(os.path.join(icon_path, "settings.png"))

            # Кнопки для страниц
            sidebar_layout.addWidget(self.shooting_button)
            sidebar_layout.addWidget(self.view_button)
            sidebar_layout.addWidget(self.settings_button)
            sidebar_layout.addStretch()
            
            # Страницы
            self.shooting_page = self.create_shooting_page()
            self.view_page = self.create_view_page()
            self.settings_page = self.create_settings_page()
            
            # Добавляем страницы в QStackedWidget
            self.pages.addWidget(self.shooting_page)
            self.pages.addWidget(self.view_page)
            self.pages.addWidget(self.settings_page)
            
            # Добавляем боковую панель и страницы в основной лэйаут
            main_layout.addWidget(sidebar)
            main_layout.addWidget(self.pages, 1)
            
            # Подключаем кнопки к страницам
            self.shooting_button.clicked.connect(lambda: self.pages.setCurrentWidget(self.shooting_page))
            self.view_button.clicked.connect(lambda: self.pages.setCurrentWidget(self.view_page))
            self.settings_button.clicked.connect(lambda: self.pages.setCurrentWidget(self.settings_page))
            self.setLayout(main_layout)
     
        def create_icon_button(self, icon_path):
            button = QtWidgets.QPushButton()
            button.setIcon(QtGui.QIcon(icon_path))
            button.setIconSize(QtCore.QSize(80, 80))
            button.setFixedSize(70, 70)
            button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.1);
                    border-radius: 10px;
                }
            """)
            return button

        def create_shooting_page(self):
            page = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(page)
            
            # Главный заголовок страницы
            layout.addWidget(QtWidgets.QLabel("Настройки стрельбы", alignment=QtCore.Qt.AlignCenter))
            
            # Горизонтальный контейнер для заголовков секций
            title_container = QtWidgets.QWidget()
            title_layout = QtWidgets.QHBoxLayout(title_container)
            
            trigger_label = QtWidgets.QLabel("Trigger Bot Settings")
            trigger_label.setAlignment(QtCore.Qt.AlignCenter)
            title_layout.addWidget(trigger_label, alignment=QtCore.Qt.AlignCenter)
            
            aim_label = QtWidgets.QLabel("Aim Settings")
            aim_label.setAlignment(QtCore.Qt.AlignCenter)
            title_layout.addWidget(aim_label, alignment=QtCore.Qt.AlignCenter)
            
            layout.addWidget(title_container)
            
            # Основной контейнер для настроек (Trigger Bot и Aim)
            main_container = QtWidgets.QWidget()
            main_layout = QtWidgets.QHBoxLayout(main_container)
            
            # Левая часть: Trigger Bot
            left_container = QtWidgets.QWidget()
            left_container.setStyleSheet("background-color: rgb(27, 27, 34); border-radius: 5px; padding: 5px;")
            left_layout = QtWidgets.QVBoxLayout()

            # Trigger Bot
            trigger_container = QtWidgets.QWidget()
            trigger_container.setStyleSheet("background-color: rgb(32, 34, 45); border-radius: 5px; padding: 5px;")
            trigger_container.setFixedHeight(150) # Уменьшаем размер контейнера
            trigger_layout = QtWidgets.QVBoxLayout()

            self.trigger_bot_active_cb = QtWidgets.QCheckBox("Enable Trigger Bot")
            self.trigger_bot_active_cb.setChecked(self.settings["trigger_bot_active"] == 1)
            self.trigger_bot_active_cb.stateChanged.connect(self.save_settings)
            trigger_layout.addWidget(self.trigger_bot_active_cb)

            self.trigger_key_input = QtWidgets.QLineEdit()
            self.trigger_key_input.setText(self.settings["keyboards"])
            self.trigger_key_input.textChanged.connect(self.save_settings)
            trigger_layout.addWidget(QtWidgets.QLabel("Trigger Key:"))
            trigger_layout.addWidget(self.trigger_key_input)

            trigger_container.setLayout(trigger_layout)
            left_layout.addWidget(trigger_container, alignment=QtCore.Qt.AlignTop)  # Выровняем контейнер сверху
            left_container.setLayout(left_layout)
            main_layout.addWidget(left_container, alignment=QtCore.Qt.AlignTop)  # Выровняем левую часть сверху

            # Правая часть: Aim
            right_container = QtWidgets.QWidget()
            right_container.setStyleSheet("background-color: rgb(27, 27, 34); border-radius: 5px; padding: 5px;")
            right_layout = QtWidgets.QVBoxLayout()
            
            aim_container = QtWidgets.QWidget()
            aim_container.setStyleSheet("background-color: rgb(32, 34, 45); border-radius: 5px; padding: 10px;")
            aim_layout = QtWidgets.QVBoxLayout()

            self.aim_active_cb = QtWidgets.QCheckBox("Enable Aim")
            self.aim_active_cb.setChecked(self.settings["aim_active"] == 1)
            self.aim_active_cb.stateChanged.connect(self.save_settings)
            aim_layout.addWidget(self.aim_active_cb)

            self.radius_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
            self.radius_slider.setMinimum(0)
            self.radius_slider.setMaximum(100)
            self.radius_slider.setValue(self.settings["radius"])
            self.radius_slider.valueChanged.connect(self.save_settings)
            aim_layout.addWidget(QtWidgets.QLabel("Aim Radius:"))
            aim_layout.addWidget(self.radius_slider)

            self.keyboard_input = QtWidgets.QLineEdit()
            self.keyboard_input.setText(self.settings["keyboard"])
            self.keyboard_input.textChanged.connect(self.save_settings)
            aim_layout.addWidget(QtWidgets.QLabel("Aim Key:"))
            aim_layout.addWidget(self.keyboard_input)

            self.aim_mode_cb = QtWidgets.QComboBox()
            self.aim_mode_cb.addItems(["Body", "Head"])
            self.aim_mode_cb.setCurrentIndex(self.settings["aim_mode"])
            self.aim_mode_cb.currentIndexChanged.connect(self.save_settings)
            aim_layout.addWidget(QtWidgets.QLabel("Aim Mode:"))
            aim_layout.addWidget(self.aim_mode_cb)

            self.aim_mode_distance_cb = QtWidgets.QComboBox()
            self.aim_mode_distance_cb.addItems(["Closest to Crosshair", "Closest in 3D"])
            self.aim_mode_distance_cb.setCurrentIndex(self.settings["aim_mode_distance"])
            self.aim_mode_distance_cb.currentIndexChanged.connect(self.save_settings)
            aim_layout.addWidget(QtWidgets.QLabel("Aim Distance Mode:"))
            aim_layout.addWidget(self.aim_mode_distance_cb)

            aim_container.setLayout(aim_layout)
            right_layout.addWidget(aim_container)
            right_container.setLayout(right_layout)
            main_layout.addWidget(right_container)

            # Добавляем основной контейнер в главный layout
            layout.addWidget(main_container)
            
            return page

        def create_view_page(self):
            page = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(page)
            layout.addWidget(QtWidgets.QLabel("Настройки визуала", alignment=QtCore.Qt.AlignCenter))
            # Тут добавляйте элементы управления для визуала
            left_layout = QtWidgets.QVBoxLayout()
            spacer_item = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
            layout.addLayout(left_layout)
            
                        # ESP
            esp_container = QtWidgets.QWidget()
            esp_container.setStyleSheet("background-color: rgb(32, 34, 45); border-radius: 5px; padding: 10px;")
            esp_layout = QtWidgets.QVBoxLayout()
            
            esp_label = QtWidgets.QLabel("ESP Settings")
            esp_label.setAlignment(QtCore.Qt.AlignCenter)
            esp_layout.addWidget(esp_label)
        
            self.esp_rendering_cb = QtWidgets.QCheckBox("Enable ESP")
            self.esp_rendering_cb.setChecked(self.settings["esp_rendering"] == 1)
            self.esp_rendering_cb.stateChanged.connect(self.save_settings)
            esp_layout.addWidget(self.esp_rendering_cb)
        
            self.esp_mode_cb = QtWidgets.QComboBox()
            self.esp_mode_cb.addItems(["Enemies Only", "All Players"])
            self.esp_mode_cb.setCurrentIndex(self.settings["esp_mode"])
            self.esp_mode_cb.currentIndexChanged.connect(self.save_settings)
            esp_layout.addWidget(self.esp_mode_cb)
        
            self.line_rendering_cb = QtWidgets.QCheckBox("Draw Lines")
            self.line_rendering_cb.setChecked(self.settings["line_rendering"] == 1)
            self.line_rendering_cb.stateChanged.connect(self.save_settings)
            esp_layout.addWidget(self.line_rendering_cb)
        
            self.hp_bar_rendering_cb = QtWidgets.QCheckBox("Draw HP Bars")
            self.hp_bar_rendering_cb.setChecked(self.settings["hp_bar_rendering"] == 1)
            self.hp_bar_rendering_cb.stateChanged.connect(self.save_settings)
            esp_layout.addWidget(self.hp_bar_rendering_cb)
        
            self.head_hitbox_rendering_cb = QtWidgets.QCheckBox("Draw Head Hitbox")
            self.head_hitbox_rendering_cb.setChecked(self.settings["head_hitbox_rendering"] == 1)
            self.head_hitbox_rendering_cb.stateChanged.connect(self.save_settings)
            esp_layout.addWidget(self.head_hitbox_rendering_cb)
        
            self.bons_cb = QtWidgets.QCheckBox("Draw Bones")
            self.bons_cb.setChecked(self.settings["bons"] == 1)
            self.bons_cb.stateChanged.connect(self.save_settings)
            esp_layout.addWidget(self.bons_cb)
        
            self.nickname_cb = QtWidgets.QCheckBox("Show Nickname")
            self.nickname_cb.setChecked(self.settings["nickname"] == 1)
            self.nickname_cb.stateChanged.connect(self.save_settings)
            esp_layout.addWidget(self.nickname_cb)
        
            esp_container.setLayout(esp_layout)
            esp_container.setFixedWidth(300)  # Замените 300 на ширину блока Aim
            left_layout.addWidget(esp_container)
        
            left_layout.addItem(spacer_item)
            page.setLayout(layout)

            # Функция для добавления строки настройки цвета
            color_scroll_area = QtWidgets.QScrollArea()
            color_scroll_area.setWidgetResizable(True)
            color_scroll_area.setFixedHeight(300)

            color_settings_container = QtWidgets.QWidget()
            color_layout = QtWidgets.QVBoxLayout(color_settings_container)
            color_scroll_area.setWidget(color_settings_container)  # Добавляем контейнер в scroll area

            # Функция для добавления строки настройки цвета
            def add_color_setting(label_text, color_key):
                row_layout = QtWidgets.QGridLayout()
                row_layout.setHorizontalSpacing(5)
                row_layout.setContentsMargins(0, 2, 0, 2)

                # Цветовой квадрат - индикатор цвета
                color_square = QtWidgets.QLabel()
                color_square.setFixedSize(20, 20)
                color_square.setObjectName(f"{color_key}_square")
                row_layout.addWidget(color_square, 0, 0)

                # Название параметра
                label = QtWidgets.QLabel(label_text)
                label.setFixedWidth(120)
                row_layout.addWidget(label, 0, 1)

                # Поля для RGB и альфа-значений
                r_input = QtWidgets.QLineEdit()
                r_input.setPlaceholderText("R")
                r_input.setMaximumWidth(90)
                r_input.setText(str(self.settings.get(f"{color_key}_r", 255)))

                g_input = QtWidgets.QLineEdit()
                g_input.setPlaceholderText("G")
                g_input.setMaximumWidth(90)
                g_input.setText(str(self.settings.get(f"{color_key}_g", 0)))

                b_input = QtWidgets.QLineEdit()
                b_input.setPlaceholderText("B")
                b_input.setMaximumWidth(90)
                b_input.setText(str(self.settings.get(f"{color_key}_b", 0)))

                a_input = QtWidgets.QLineEdit()
                a_input.setPlaceholderText("Alpha")
                a_input.setMaximumWidth(90)
                a_input.setText(str(self.settings.get(f"{color_key}_alpha", 255)))

                # Обновляем цвет после установки значений по умолчанию
                self.update_color_square(color_square, color_key, r_input.text(), g_input.text(), b_input.text(), a_input.text())

                # Подключаем события для обновления цвета и сохранения
                def save_color():
                    self.settings[f"{color_key}_r"] = r_input.text()
                    self.settings[f"{color_key}_g"] = g_input.text()
                    self.settings[f"{color_key}_b"] = b_input.text()
                    self.settings[f"{color_key}_alpha"] = a_input.text()

                # Подключение событий для обновления цвета
                r_input.textChanged.connect(lambda: (self.update_color_square(color_square, color_key, r_input.text(), g_input.text(), b_input.text(), a_input.text()), save_color()))
                g_input.textChanged.connect(lambda: (self.update_color_square(color_square, color_key, r_input.text(), g_input.text(), b_input.text(), a_input.text()), save_color()))
                b_input.textChanged.connect(lambda: (self.update_color_square(color_square, color_key, r_input.text(), g_input.text(), b_input.text(), a_input.text()), save_color()))
                a_input.textChanged.connect(lambda: (self.update_color_square(color_square, color_key, r_input.text(), g_input.text(), b_input.text(), a_input.text()), save_color()))

                # Добавление элементов в layout
                row_layout.addWidget(r_input, 0, 2)
                row_layout.addWidget(g_input, 0, 3)
                row_layout.addWidget(b_input, 0, 4)
                row_layout.addWidget(a_input, 0, 5)

                def update_and_save_color():
                    self.update_color_square(color_square, color_key, r_input.text(), g_input.text(), b_input.text(), a_input.text())
                    self.save_color_and_update_file(color_key, r_input.text(), g_input.text(), b_input.text(), a_input.text())

                r_input.textChanged.connect(update_and_save_color)
                g_input.textChanged.connect(update_and_save_color)
                b_input.textChanged.connect(update_and_save_color)
                a_input.textChanged.connect(update_and_save_color)

                color_layout.addLayout(row_layout)  # Здесь добавляем row_layout в color_layout
        # Примените настройку цвета для каждого параметра
            add_color_setting("Box E", "box_color_e")
            add_color_setting("Box T", "box_color_t")

            add_color_setting("Hp Bar T", "hp_bar_color_t")
            add_color_setting("Hp Bar E", "hp_bar_color_e")

            add_color_setting("Bones T", "bones_color_t")
            add_color_setting("Bones E", "bones_color_e")

            add_color_setting("Name T", "nickname_color_t")
            add_color_setting("Name E", "nickname_color_e")

            add_color_setting("Head E", "head_hitbox_color_e")
            add_color_setting("Head T", "head_hitbox_color_t")

            add_color_setting("lines T", "line_color_t")
            add_color_setting("lines E", "line_color_e")

            add_color_setting("Aim Radius", "radius_aim_bot_color")
            add_color_setting("Watermark", "Watermark_fps_color")

            # Добавьте в основной layout
            left_layout.addWidget(color_scroll_area)
            return page

        def create_settings_page(self):
            page = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(page)
            layout.addWidget(QtWidgets.QLabel("Настройки", alignment=QtCore.Qt.AlignCenter))
            # Тут добавляйте элементы управления для общих настроек
            return page

        # Обновление и выбор цвета
        def update_color_square(self, color_square, color_key, r, g, b, a):
            try:
                r, g, b, a = int(r), int(g), int(b), int(a)
                color_square.setStyleSheet(f"background-color: rgba({r}, {g}, {b}, {a});")
            except ValueError:
                pass  # Игнорируем некорректные значения, если пользователь вводит не числа

        def choose_color(self, color_key):
            color = QtWidgets.QColorDialog.getColor()
            if color.isValid():
                self.settings[f"{color_key}_r"] = color.red()
                self.settings[f"{color_key}_g"] = color.green()
                self.settings[f"{color_key}_b"] = color.blue()
                self.settings[f"{color_key}_alpha"] = color.alpha()
                self.update_color_square(self.findChild(QtWidgets.QLabel, color_key + "_square"), color_key)

        def save_color_and_update_file(self, color_key, r, g, b, a):
            # Сохранение цветовых значений в словарь настроек
            self.settings[f"{color_key}_r"] = int(r)
            self.settings[f"{color_key}_g"] = int(g)
            self.settings[f"{color_key}_b"] = int(b)
            self.settings[f"{color_key}_alpha"] = int(a)

            # Сохранение конфигурации в файл
            config_dir = f"{os.environ['LOCALAPPDATA']}\\temp\\SpectrusCS"
            config_file = os.path.join(config_dir, "config.json")
            with open(config_file, "w") as f:
                json.dump(self.settings, f, indent=4)

        def save_settings(self):
            self.settings["esp_rendering"] = 1 if self.esp_rendering_cb.isChecked() else 0
            self.settings["esp_mode"] = self.esp_mode_cb.currentIndex()
            self.settings["line_rendering"] = 1 if self.line_rendering_cb.isChecked() else 0
            self.settings["hp_bar_rendering"] = 1 if self.hp_bar_rendering_cb.isChecked() else 0
            self.settings["head_hitbox_rendering"] = 1 if self.head_hitbox_rendering_cb.isChecked() else 0
            self.settings["bons"] = 1 if self.bons_cb.isChecked() else 0
            self.settings["nickname"] = 1 if self.nickname_cb.isChecked() else 0
            self.settings["aim_active"] = 1 if self.aim_active_cb.isChecked() else 0
            self.settings["radius"] = self.radius_slider.value()
            self.settings["keyboard"] = self.keyboard_input.text()
            self.settings["aim_mode"] = self.aim_mode_cb.currentIndex()
            self.settings["aim_mode_distance"] = self.aim_mode_distance_cb.currentIndex()
            self.settings["trigger_bot_active"] = 1 if self.trigger_bot_active_cb.isChecked() else 0
            self.settings["keyboards"] = self.trigger_key_input.text()
    
            # Сохранение цветовых параметров
            for color_key in ["line_color_t", "line_color_e", "hp_bar_color_t", "hp_bar_color_e", 
                            "head_hitbox_color_t", "head_hitbox_color_e", "bones_color_t", 
                            "bones_color_e", "nickname_color_t", "nickname_color_e"]:
                self.settings[f"{color_key}_r"] = int(self.settings.get(f"{color_key}_r", 255))
                self.settings[f"{color_key}_g"] = int(self.settings.get(f"{color_key}_g", 0))
                self.settings[f"{color_key}_b"] = int(self.settings.get(f"{color_key}_b", 0))
                self.settings[f"{color_key}_alpha"] = int(self.settings.get(f"{color_key}_alpha", 255))


            config_dir = f"{os.environ['LOCALAPPDATA']}\\temp\\SpectrusCS"
            config_file = os.path.join(config_dir, "config.json")
    
            with open(config_file, "w") as f:
                json.dump(self.settings, f, indent=4)
            
        def mousePressEvent(self, event: QtGui.QMouseEvent):
            if event.button() == QtCore.Qt.LeftButton:
                self.is_dragging = True
                self.drag_start_position = event.globalPosition().toPoint()
    
        def mouseMoveEvent(self, event: QtGui.QMouseEvent):
            if self.is_dragging:
                delta = event.globalPosition().toPoint() - self.drag_start_position
                self.move(self.pos() + delta)
                self.drag_start_position = event.globalPosition().toPoint()
    
        def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
            if event.button() == QtCore.Qt.LeftButton:
                self.is_dragging = False
    
    app = QtWidgets.QApplication(sys.argv)
    window = ConfigWindow()
    window.show()
    sys.exit(app.exec())