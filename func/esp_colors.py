from PySide6 import QtWidgets, QtGui, QtCore
import json
import os
import time

# Т - тимейт / team
# E - враг / enemy

def load_settings():
    attempts = 5  # Максимальное количество попыток
    for _ in range(attempts):
        try:
            config_dir = f"{os.environ['LOCALAPPDATA']}\\temp\\SpectrusCS"
            config_file = os.path.join(config_dir, "config.json")
            with open(config_file, "r") as f:
                settings = json.load(f)
            return settings
        except Exception as e:
            print(f"Ошибка при загрузке настроек: {e}")
            time.sleep(1)  # Подождите перед следующей попыткой
    return {}

def get_box_color_t(settings):
    box_r_t = settings.get("box_color_t_r", 0)
    box_g_t = settings.get("box_color_t_g", 0)
    box_b_t = settings.get("box_color_t_b", 0)
    return(box_r_t,box_g_t,box_b_t)

def get_box_color_e(settings):
    box_r_e = settings.get("box_color_e_r", 0)
    box_g_e = settings.get("box_color_e_g", 0)
    box_b_e = settings.get("box_color_e_b", 0)
    return(box_r_e, box_g_e, box_b_e)    

def get_color_bones(settings):
    bones_r = settings.get("bones_color_e_r", 0)
    bones_g = settings.get("bones_color_e_g", 0) #скилет врагов
    bones_b = settings.get("bones_color_e_b", 0)
    return (bones_r, bones_g, bones_b) 

def get_color_t_bones(settings):
    bones_t_r = settings.get("bones_color_t_r",0)
    bones_t_g = settings.get("bones_color_t_g",0) # скилет тима
    bones_t_b = settings.get("bones_color_t_b",0)
    return(bones_t_r,bones_t_g,bones_t_b)

def get_color_name_e(settings):
    nick_r = settings.get("nickname_color_e_r",0)
    nick_g = settings.get("nickname_color_e_g",0) #имена врагов
    nick_b = settings.get("nickname_color_e_b",0)
    return (nick_r, nick_g, nick_b)

def get_color_name_t(settings):
    nick_t_r = settings.get("nickname_color_t_r", 0)
    nick_t_g = settings.get("nickname_color_t_g", 0) # имена тимейтов
    nick_t_b = settings.get("nickname_color_t_b", 0)
    return(nick_t_r, nick_t_g, nick_t_b)

def get_color_radius(settings):
    radius_r = settings.get("radius_aim_bot_color_r", 0)
    radius_g = settings.get("radius_aim_bot_color_g", 0) # радиус для аима
    radius_b = settings.get("radius_aim_bot_color_b", 0)  
    return (radius_r, radius_g, radius_b)

def hp_bar_t(settings):
    hp_bar_t_r = settings.get("hp_bar_color_t_r", 0) 
    hp_bar_t_g = settings.get("hp_bar_color_t_g", 0) # хп бар тима
    hp_bar_t_b = settings.get("hp_bar_color_t_b", 0)
    return(hp_bar_t_r, hp_bar_t_g, hp_bar_t_b)

def hp_bar_e(settings):
    hp_bar_e_r = settings.get("hp_bar_color_e_r", 0) 
    hp_bar_e_g = settings.get("hp_bar_color_e_g", 0) # хп бар враги
    hp_bar_e_b = settings.get("hp_bar_color_e_b", 0)
    return(hp_bar_e_r, hp_bar_e_g, hp_bar_e_b)

def get_color_watermark(settings):
    Watermark_fps_r = settings.get("Watermark_fps_color_r", 0)
    Watermark_fps_g = settings.get("Watermark_fps_color_g", 0) # вотермарк и фпс
    Watermark_fps_b = settings.get("Watermark_fps_color_b", 0)
    return(Watermark_fps_r, Watermark_fps_g, Watermark_fps_b)

def get_e_line_color(settings):
    line_e_r = settings.get("line_color_e_r", 0)
    line_e_g = settings.get("line_color_e_g", 0) # линий на тимейтов
    line_e_b = settings.get("line_color_e_b", 0)
    return(line_e_r, line_e_g, line_e_b)

def get_t_line_color(settings):
    line_t_r = settings.get("line_color_t_r", 0)
    line_t_g = settings.get("line_color_t_g", 0) # линий на врагов
    line_t_b = settings.get("line_color_t_b", 0)
    return(line_t_r, line_t_g, line_t_b)

def get_head_t_color(settings):
    head_t_r = settings.get("head_hitbox_color_t_r",0)
    head_t_g = settings.get("head_hitbox_color_t_g",0) # голова тим
    head_t_b = settings.get("head_hitbox_color_t_b",0)
    return(head_t_r, head_t_g, head_t_b)

def get_head_e_color(settings):
    head_e_r = settings.get("head_hitbox_color_e_r",0)
    head_e_g = settings.get("head_hitbox_color_e_g",0) # голова враги
    head_e_b = settings.get("head_hitbox_color_e_b",0)
    return(head_e_r, head_e_g, head_e_b)
