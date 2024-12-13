from typing import Tuple
from customtkinter import *
import firebase_admin
from firebase_admin import credentials, db
import subprocess
import datetime
import os
import json
from PIL import Image
import win32api
import win32con
import MemoryAccess
from CTkColorPicker import *
import threading
import pywinstyles
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QTimer, QRect
from PyQt5.QtGui import QFont, QFontMetrics
from pynput import keyboard, mouse
import time
import offsets

# python -m auto_py_to_exe
# pyinstaller --noconfirm --onefile --windowed --icon "gamer-zone.ico" --add-data "firebase_credentials.json;." --add-data "C:/Users/Lucas Lima/AppData/Local/Programs/Python/Python311/Lib/site-packages/customtkinter/__init__.py;customtkinter/"  "main.py"

# Configuração do Firebase
#####################################################################################################

def get_resource_path(relative_path):
    """Obter o caminho do arquivo no executável."""
    try:
        # PyInstaller cria uma pasta temporária e armazena o caminho em _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Use o mesmo nome que você especificou no campo ao lado do arquivo no auto-py-to-exe
json_path = get_resource_path('firebase_credentials.json')

# Carregar as credenciais do arquivo JSON
with open(json_path) as f:
    firebase_credentials = json.load(f)

cred = credentials.Certificate(firebase_credentials)

firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://steam-keygen-default-rtdb.firebaseio.com/'
})
#####################################################################################################

# Função para obter o HWID do PC
#####################################################################################################
def get_hwid():
    try:
        result = subprocess.check_output('wmic diskdrive get serialnumber', shell=True)
        hwid = result.decode().split('\n')[1].strip()
        return hwid
    except Exception as e:
        print(f"Erro ao obter HWID: {e}")
        return None
#####################################################################################################

# Função para centralizar a janela na tela
#####################################################################################################
def CenterWindowToDisplay(Screen: CTk, width: int, height: int):
    screen_size = (Screen.winfo_screenwidth(), Screen.winfo_screenheight())
    x, y = int((screen_size[0] / 2) - (width / 2)), int((screen_size[1] / 2) - (height / 1.5))
    return f"{width}x{height}+{x}+{y}"
#####################################################################################################




# Atualiza os offsets
offsets.start()

class LoaderWindow(CTk):
    AimbotFovRadioVar = 70
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.geometry(CenterWindowToDisplay(self, 450, 280))
        self.title("GZCC")
        self.protocol("WM_DELETE_WINDOW", lambda:os._exit(0))  # Captura o evento de fechamento da janela
        self.resizable(0,0)
        self.config(bg="#000000")

        self.layout()
        self.check_hwid_on_startup()

    def layout(self):
        self.lb_title = CTkLabel(self, text="CheatZone", font=("Anatasha Trial", 33, "bold"), bg_color="#000000")
        self.lb_title.pack(anchor=N, pady=30)
        self.lb2 = CTkLabel(self, text="Digite sua chave de acesso!", font=("Helvetica", 12, "bold"), fg_color="#000000")
        self.lb2.place(relx=0.322, rely=0.33)

        self.key = StringVar()
        self.CtkKey = CTkEntry(self, width=200, textvariable=self.key)
        self.CtkKey.pack(anchor=CENTER, pady=20)

        self.btn_check_key = CTkButton(self, text="Checar", border_width=2, command=lambda: self.check_key(), fg_color="#000000")
        self.btn_check_key.pack(anchor=CENTER)
        self.label_show_check_key = CTkLabel(self, text="", font=("Helvetica", 12, "bold"), fg_color="#000000")
        self.label_show_check_key.pack(anchor=CENTER, pady=5)

    def check_key(self):
        input_key = self.key.get()
        if self.is_key_valid(input_key):
            self.label_show_check_key.configure(text="Chave válida!")
            self.use_key(input_key)
        else:
            self.label_show_check_key.configure(text="Chave inválida!")

    def is_key_valid(self, key):
        ref = db.reference('Chaves')
        data = ref.get()
        return key in data if data else False

    def use_key(self, key):
        ref = db.reference('Chaves')
        data = ref.get()
        if key in data:
            ref.child(key).delete()
            print(f"Chave '{key}' utilizada com sucesso!")
            self.register_hwid(key)
        else:
            print(f"A chave '{key}' não existe no banco de dados.")

    def register_hwid(self, key):
        hwid = get_hwid()
        if hwid:
            if key[-2:] == "1d":
                exp_date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
            if key[-2:] == "3d":
                exp_date = (datetime.datetime.now() + datetime.timedelta(days=3)).strftime('%Y-%m-%d')
            if key[-2:] == "7d":
                exp_date = (datetime.datetime.now() + datetime.timedelta(days=7)).strftime('%Y-%m-%d')
            if key[-2:] == "30d":
                exp_date = (datetime.datetime.now() + datetime.timedelta(days=30)).strftime('%Y-%m-%d')
            if key[-2:] == "lf":
                exp_date = (datetime.datetime.now() + datetime.timedelta(days=99999)).strftime('%Y-%m-%d')
            ref = db.reference('HWIDs')
            ref.push({
                'hwid': hwid,
                'expiration_date': exp_date
            })
            print("HWID e data de expiração registrados com sucesso!")
            self.btn_check_key.destroy()
            self.label_show_check_key.destroy()
            self.lb2.destroy()
            self.CtkKey.destroy()
            self.btn_entrar = CTkButton(self, text="Entrar", font=("Helvetica", 14, "bold"), border_width=2, command=lambda: self.StartCS_Cheat(), fg_color="#000000", text_color="#F601F7").pack(anchor=CENTER, pady=30)

    def check_hwid_on_startup(self):
        hwid = get_hwid()
        if hwid:
            ref = db.reference('HWIDs')
            data = ref.get()
            if data:
                for record in data.values():
                    if record['hwid'] == hwid:
                        if datetime.datetime.now().strftime('%Y-%m-%d') > record['expiration_date']:
                            self.label_show_check_key.configure(text="Acesso bloqueado. Data de expiração atingida.")
                        else:
                            self.label_show_check_key.configure(text="HWID já registrado. Acesso permitido.")
                            self.btn_check_key.destroy()
                            self.label_show_check_key.destroy()
                            self.lb2.destroy()
                            self.CtkKey.destroy()
                            self.btn_entrar = CTkButton(self, text="Entrar", font=("Helvetica", 14, "bold"), border_width=2, command=lambda: self.StartCS_Cheat(), fg_color="#000000", text_color="#F601F7")
                            self.btn_entrar.pack(anchor=CENTER, pady=30)
                        return
                self.label_show_check_key.configure(text="HWID não registrado.")
    











    def StartCS_Cheat(self):
        self.btn_check_key.destroy()
        self.label_show_check_key.destroy()
        self.lb2.destroy()
        self.CtkKey.destroy()
        self.lb_title.destroy()
        self.geometry(CenterWindowToDisplay(self, 780, 450))
        self.visible = False
        self.resizable(0,0)
        self.overrideredirect(True)
        self.title("GZCC")
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.9)
        try:
            self.btn_entrar.destroy()
        except:
            pass
        self.config(bg="#000000")
        
        threading.Thread(target=run_pyqt, daemon=True).start()
        
        # Barra de tarefas
        self.TopFrame = CTkFrame(self, width=780, height=25, fg_color=("#000000"), bg_color="#000000")
        self.TopFrame.place(relx=0, rely=0)
        self.TopFrame.bind('<Button-1>', self.CustomTitleBar)
        
        # Margem
        CTkFrame(self, width=780, height=2, fg_color="#F601F7").place(relx=0, rely=0)
        CTkFrame(self, width=780, height=2, fg_color="#F601F7").place(relx=0, rely=0.995)
        CTkFrame(self, width=2, height=450, fg_color="#F601F7").place(relx=0, rely=0)
        CTkFrame(self, width=2, height=450, fg_color="#F601F7").place(relx=0.997, rely=0)
        
        CTkFrame(self, height=0, width=0).pack(anchor=W, pady=5) # Espaçamento



        # Sessão - Visuals
        self.Sessao_Visuals_btn = CTkButton(self, hover_color="#494949", text="       Visuals", border_width=2, height=40, fg_color=("#121212"), text_color="#ffffff", font=("Helvetica", 14, "bold"), command=lambda:self.change_menu("Visuals"))
        self.Sessao_Visuals_btn.place(relx=0.1, rely=0.07)
        # Image
        self.eye_img = CTkLabel(self, image=CTkImage(light_image=Image.open("imgs/eye.png"),size=(30, 30)), fg_color="#000001", text="")
        self.eye_img.place(relx=0.125, rely=0.08)
        # Set Image Transparency
        pywinstyles.set_opacity(self.eye_img, color="#000001")
        # Indicator
        self.Indicator_01 = CTkFrame(self, width=100, height=2, fg_color="#F601F7")
        self.Indicator_01.place(relx=0.125, rely=0.2)
        
        
        
        
        # Sessão - Aimbot
        self.Sessao_Aimbot_btn = CTkButton(self, hover_color="#494949", text="     Aimbot", border_width=2, height=40, fg_color=("#121212"), text_color="#ffffff", font=("Helvetica", 14, "bold"), command=lambda:self.change_menu("Aimbot"))
        self.Sessao_Aimbot_btn.place(relx=0.3, rely=0.07)
        # Image
        self.target_img = CTkLabel(self, image=CTkImage(light_image=Image.open("imgs/target.png"),size=(30, 30)), text="", fg_color="#000001")
        self.target_img.place(relx=0.315, rely=0.08)
        self.Indicator_02 = CTkFrame(self, width=100, height=2, fg_color="#000000")
        # Set Image Transparency
        pywinstyles.set_opacity(self.target_img, color="#000001")
        # Indicator
        self.Indicator_02.place(relx=0.325, rely=0.2)
        
        
        
        # Sessão - Misc
        self.Sessao_Misc_btn = CTkButton(self, hover_color="#494949", text="       Misc", border_width=2, height=40, fg_color=("#121212"), text_color="#ffffff", font=("Helvetica", 14, "bold"))
        self.Sessao_Misc_btn.place(relx=0.5, rely=0.07)
        # Image
        self.games_img = CTkLabel(self, image=CTkImage(light_image=Image.open("imgs/games.png"),size=(30, 30)), text="", fg_color="#000001")
        self.games_img.place(relx=0.515, rely=0.08)
        # Set Image Transparency
        pywinstyles.set_opacity(self.games_img, color="#000001")
        # Indicator
        self.Indicator_03 = CTkFrame(self, width=100, height=2, fg_color="#000000")
        self.Indicator_03.place(relx=0.525, rely=0.2)
        
        
        
        # Sessão - Config
        self.Sessao_Config_btn = CTkButton(self, hover_color="#494949", text="       Config", border_width=2, height=40, fg_color=("#121212"), text_color="#ffffff", font=("Helvetica", 14, "bold"))
        self.Sessao_Config_btn.place(relx=0.7, rely=0.07)
        # Image
        self.setting_img = CTkLabel(self, image=CTkImage(light_image=Image.open("imgs/setting.png"),size=(30, 30)), text="", fg_color="#000001")
        self.setting_img.place(relx=0.715, rely=0.08)
        # Set Image Transparency
        pywinstyles.set_opacity(self.setting_img, color="#000001")
        # Indicator
        self.Indicator_04 = CTkFrame(self, width=100, height=2, fg_color="#000000")
        self.Indicator_04.place(relx=0.725, rely=0.2)

        self.load_vars()
        self.actions_update()
        self.change_menu("Visuals")
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    def change_menu(self, menu):
        if menu == "Visuals":
            # Esp Box
            self.checkbox_01 = CTkCheckBox(self, text="Esp Box", variable=self.Esp_box_switch, onvalue=True, offvalue=False, bg_color="#000000", font=("Helvetica", 14, "bold"), checkmark_color="#F601F7", fg_color="#121212", border_color="#393939", hover_color="#ffffff", command=lambda:self.var_update("box"))
            self.checkbox_01.place(relx=0.1, rely=0.3)
            self.esp_box_btn = CTkButton(self, hover_color="#494949", width=110, height=15, text="Box Color", text_color="#ffffff", fg_color="#121212", font=("Helvetica", 13, "bold"), border_width=2, command=lambda:self.ask_color("esp_box"))
            self.esp_box_btn.place(relx=0.3, rely=0.3)
            # Esp Name
            self.checkbox_02 = CTkCheckBox(self, text="Esp Name", variable=self.Esp_name_switch, onvalue=True, offvalue=False, bg_color="#000000", font=("Helvetica", 14, "bold"), checkmark_color="#F601F7", fg_color="#121212", border_color="#393939", hover_color="#ffffff", command=lambda:self.var_update("name"))
            self.checkbox_02.place(relx=0.1, rely=0.37)
            self.esp_name_btn = CTkButton(self, hover_color="#494949", width=110, height=15, text="Name Color", text_color="#ffffff", fg_color="#121212", font=("Helvetica", 13, "bold"), border_width=2, command=lambda:self.ask_color("esp_name"))
            self.esp_name_btn.place(relx=0.3, rely=0.37)             
            # Esp Health
            self.checkbox_03 = CTkCheckBox(self, text="Esp Health", variable=self.Esp_health_switch, onvalue=True, offvalue=False, bg_color="#000000", font=("Helvetica", 14, "bold"), checkmark_color="#F601F7", fg_color="#121212", border_color="#393939", hover_color="#ffffff", command=lambda:self.var_update("health"))
            self.checkbox_03.place(relx=0.1, rely=0.44)
            self.esp_health_btn = CTkButton(self, hover_color="#494949", width=110, height=15, text="Health Color", text_color="#ffffff", fg_color="#121212", font=("Helvetica", 13, "bold"), border_width=2, command=lambda:self.ask_color("esp_health"))
            self.esp_health_btn.place(relx=0.3, rely=0.44)
            # Esp Armor
            self.checkbox_04 = CTkCheckBox(self, text="Esp Armor", variable=self.Esp_armor_switch, onvalue=True, offvalue=False, bg_color="#000000", font=("Helvetica", 14, "bold"), checkmark_color="#F601F7", fg_color="#121212", border_color="#393939", hover_color="#ffffff", command=lambda:self.var_update("armor"))
            self.checkbox_04.place(relx=0.1, rely=0.51)
            self.esp_armor_btn = CTkButton(self, hover_color="#494949", width=110, height=15, text="Armor Color", text_color="#ffffff", fg_color="#121212", font=("Helvetica", 13, "bold"), border_width=2, command=lambda:self.ask_color("esp_armor"))
            self.esp_armor_btn.place(relx=0.3, rely=0.51)
            # Esp Skeleton
            self.checkbox_05 = CTkCheckBox(self, text="Esp Skeleton", variable=self.Esp_skeleton_switch, onvalue=True, offvalue=False, bg_color="#000000", font=("Helvetica", 14, "bold"), checkmark_color="#F601F7", fg_color="#121212", border_color="#393939", hover_color="#ffffff", command=lambda:self.var_update("skeleton"))
            self.checkbox_05.place(relx=0.1, rely=0.58)
            self.esp_skeleton_btn = CTkButton(self, hover_color="#494949", width=110, height=15, text="Skeleton Color", text_color="#ffffff", fg_color="#121212", font=("Helvetica", 13, "bold"), border_width=2, command=lambda:self.ask_color("esp_skeleton"))
            self.esp_skeleton_btn.place(relx=0.3, rely=0.58)
            # Esp Line
            self.checkbox_06 = CTkCheckBox(self, text="Esp Line", variable=self.Esp_line_switch, onvalue=True, offvalue=False, bg_color="#000000", font=("Helvetica", 14, "bold"), checkmark_color="#F601F7", fg_color="#121212", border_color="#393939", hover_color="#ffffff", command=lambda:self.var_update("line"))
            self.checkbox_06.place(relx=0.1, rely=0.65)
            self.esp_line_btn = CTkButton(self, hover_color="#494949", width=110, height=15, text="Line Color", text_color="#ffffff", fg_color="#121212", font=("Helvetica", 13, "bold"), border_width=2, command=lambda:self.ask_color("esp_line"))
            self.esp_line_btn.place(relx=0.3, rely=0.65)
            # Esp Distance
            self.checkbox_07 = CTkCheckBox(self, text="Esp Distance", variable=self.Esp_distance_switch, onvalue=True, offvalue=False, bg_color="#000000", font=("Helvetica", 14, "bold"), checkmark_color="#F601F7", fg_color="#121212", border_color="#393939", hover_color="#ffffff", command=lambda:self.var_update("distance"))
            self.checkbox_07.place(relx=0.1, rely=0.72)
            self.esp_distance_btn = CTkButton(self, hover_color="#494949", width=110, height=15, text="Distance Color", text_color="#ffffff", fg_color="#121212", font=("Helvetica", 13, "bold"), border_width=2, command=lambda:self.ask_color("esp_distance"))
            self.esp_distance_btn.place(relx=0.3, rely=0.72)
            # Esp Glow
            self.checkbox_08 = CTkCheckBox(self, text="Glow", variable=self.Esp_glow_switch, onvalue=True, offvalue=False, bg_color="#000000", font=("Helvetica", 14, "bold"), checkmark_color="#F601F7", fg_color="#121212", border_color="#393939", hover_color="#ffffff", command=lambda:self.var_update("glow"))
            self.checkbox_08.place(relx=0.1, rely=0.79)
            self.esp_glow_btn = CTkButton(self, hover_color="#494949", width=110, height=15, text="Glow Color", text_color="#ffffff", fg_color="#121212", font=("Helvetica", 13, "bold"), border_width=2, command=lambda:self.ask_color("esp_glow"))
            self.esp_glow_btn.place(relx=0.3, rely=0.79)
            def visualize_esp_window():
                global Fire_enemy_switch, ThirdPerson_switch, NoFlash_switch, PlayerFov
                if self.switch_var.get() == "on":
                    self.win = CTkToplevel()
                    self.win.resizable(0,0)
                    self.win.overrideredirect(True)
                    self.win.title("GZCC")
                    self.win.attributes("-topmost", True)
                    self.win.config(bg="#000000")
                    def loop_win():
                        self.win.after(2, loop_win)
                        window_coord = self.winfo_geometry()
                        coords = window_coord.replace("x", " ").replace("+", " ")
                        coord_list = coords.split()
                        self.win.geometry(f"300x450+{int(coord_list[2])+int(coord_list[0])+5}+{coord_list[3]}")
                    loop_win()
                    # Margem
                    CTkFrame(self.win, width=300, height=2, fg_color="#F601F7").place(relx=0, rely=0)
                    CTkFrame(self.win, width=300, height=2, fg_color="#F601F7").place(relx=0, rely=0.995)
                    CTkFrame(self.win, width=2, height=450, fg_color="#F601F7").place(relx=0, rely=0)
                    CTkFrame(self.win, width=2, height=450, fg_color="#F601F7").place(relx=0.997, rely=0)
                    
                    CTkFrame(self.win, height=1, fg_color="#000000", bg_color="#000000").pack(pady=35)
                    # Player Image
                    CTkLabel(self.win, image=CTkImage(light_image=Image.open("imgs/player.png"),size=(147, 302)), text="", fg_color="#000000").pack(anchor=CENTER)
                    
                    top = CTkFrame(self.win, width=150, height=2, fg_color=Esp_box_color_art)
                    left = CTkFrame(self.win, width=2, height=320, fg_color=Esp_box_color_art)
                    bottom = CTkFrame(self.win, width=150, height=2, fg_color=Esp_box_color_art)
                    right = CTkFrame(self.win, width=2, height=320, fg_color=Esp_box_color_art)
                    name = CTkLabel(self.win, text="Enemy", text_color=Esp_name_color_art, fg_color="#000000", font=("Helvetica", 12, "bold"))
                    health = CTkFrame(self.win, width=10, height=320, fg_color=Esp_health_color_art,corner_radius=0)
                    armor = CTkFrame(self.win, width=10, height=320, fg_color=Esp_armor_color_art,corner_radius=0)
                    def active_box():
                        if status_var.get():
                            top.place(relx=0.25, rely=0.14)
                            left.place(relx=0.25, rely=0.14)
                            bottom.place(relx=0.25, rely=0.85)
                            right.place(relx=0.75, rely=0.14)
                            name.place(relx=0.425, rely=0.07)
                            health.place(relx=0.2, rely=0.14)
                            armor.place(relx=0.15, rely=0.14)
                        else:
                            try:
                                top.place(relx=10, rely=10)
                                left.place(relx=10, rely=10)
                                bottom.place(relx=10, rely=10)
                                right.place(relx=10, rely=10)
                                name.place(relx=10, rely=10)
                                health.place(relx=10, rely=10)
                                armor.place(relx=10, rely=10)
                            except:
                                pass
                    
                    status_var = BooleanVar()
                    box = CTkCheckBox(self.win, text="ESP", variable=status_var, command=active_box,onvalue=True, offvalue=False, bg_color="#000000", font=("Helvetica", 14, "bold"), checkmark_color="#F601F7", fg_color="#121212", border_color="#393939", hover_color="#ffffff")
                    box.place(relx=0.425, rely=0.9)
                    
                else:
                    self.win.destroy()
            
            # Options
            self.fire_enemy = CTkCheckBox(self, text="Fire Enemy", variable=self.Fire_enemy_switch ,onvalue=True, offvalue=False, bg_color="#000000", font=("Helvetica", 14, "bold"), checkmark_color="#F601F7", fg_color="#121212", border_color="#393939", hover_color="#ffffff", command=lambda:self.var_update(""))
            self.fire_enemy.place(relx=0.5, rely=0.3)
        
            self.NoFlash = CTkCheckBox(self, text="No Flash", variable=self.NoFlash_switch , onvalue=True, offvalue=False, bg_color="#000000", font=("Helvetica", 14, "bold"), checkmark_color="#F601F7", fg_color="#121212", border_color="#393939", hover_color="#ffffff", command=lambda:self.var_update(""))
            self.NoFlash.place(relx=0.5, rely=0.37)
            
            self.ThirdPerson = CTkCheckBox(self, text="Third Person", variable=self.ThirdPerson_switch , onvalue=True, offvalue=False, bg_color="#000000", font=("Helvetica", 14, "bold"), checkmark_color="#F601F7", fg_color="#121212", border_color="#393939", hover_color="#ffffff", command=lambda:self.var_update(""))
            self.ThirdPerson.place(relx=0.5, rely=0.44)
            
            self.Fov = CTkCheckBox(self, text="Fov", variable=self.FovPlayer_switch, onvalue=True, offvalue=False, bg_color="#000000", font=("Helvetica", 14, "bold"), checkmark_color="#F601F7", fg_color="#121212", border_color="#393939", hover_color="#ffffff", command=lambda:self.var_update(""))
            self.Fov.place(relx=0.5, rely=0.51)
            def slider_event(value):
                global PlayerFov
                PlayerFov = int(value)
            self.slider = CTkSlider(self, width=170, from_=0, to=170, number_of_steps=180, fg_color="#F601F7", bg_color="#000000", progress_color="#F601F7", button_color="#ffffff", button_hover_color="#121212", command=slider_event)
            self.slider.place(relx=0.6, rely=0.525)
            
            # Switch Other Options
            self.switch_var = StringVar(value="off")
            self.other_options = CTkSwitch(self, text="Visualize Esp", command=visualize_esp_window, variable=self.switch_var, onvalue="on", offvalue="off", border_color="#393939", border_width=2, fg_color="#121212", text_color="#ffffff", bg_color="#000000", progress_color="#F601F7", font=("Helvetica", 13, "bold"))
            self.other_options.place(relx=0.5, rely=0.59)
            
            
            
            # Aimbot
            try:
                self.Indicator_01.configure(fg_color="#F601F7")
                self.Indicator_02.configure(fg_color="#000000")
                self.Indicator_03.configure(fg_color="#000000")
                self.Indicator_04.configure(fg_color="#000000")
                self.frame_01.destroy()
                self.aimbot.destroy()
                self.aimbot_fov.destroy()
                self.color_fov_btn.destroy()
                self.lb_1.destroy()
                self.slider_fov.destroy()
                self.slider_distance.destroy()
                self.slider_smoooth.destroy()
                self.radiobutton_1.destroy()
                self.radiobutton_2.destroy()
                self.radiobutton_3.destroy()
                self.hit_sound.destroy()
                self.trigger.destroy()
                self.key_trigger_btn.destroy()
                self.delay_entry.destroy()
                self.lb_7.destroy()
                self.lb_3.destroy()
                self.lb_4.destroy()
                self.lb_5.destroy()
                self.lb_6.destroy()
                self.frame_01.destroy()
                self.frame_02.destroy()
                self.frame_03.destroy()
                self.lb_5.destroy()
                self.key_aimbot_btn.destroy()
                self.closest_enemy_glow.destroy()
                self.color_glow_btn.destroy()
            except:
                pass
            # Misc
            # Options
            
            
            
            
            
            
            
            
            
            
            
            
            
            
        if menu == "Aimbot":
            # AIMBOT
            self.frame_01 = CTkFrame(self, fg_color="#121212", width=300, height=320, bg_color="#000000", corner_radius=10, border_color="#ffffff", border_width=2)
            self.frame_01.place(relx=0.1, rely=0.27-0.04)
            self.aimbot = CTkCheckBox(self, text="Aimbot", command=lambda:self.var_update(""), variable=self.aimbot_var,onvalue=True, offvalue=False, bg_color="#121212", font=("Helvetica", 14, "bold"), checkmark_color="#F601F7", fg_color="#121212", border_color="#393939", hover_color="#ffffff")
            self.aimbot.place(relx=0.13, rely=0.3-0.04)
            
            self.aimbot_fov = CTkSwitch(self, text="Fov", command=lambda:self.var_update(""), variable=self.AimFovVar, onvalue=True, offvalue=False, border_color="#393939", border_width=2, fg_color="#191919", text_color="#ffffff", bg_color="#121212", progress_color="#F601F7", font=("Helvetica", 13, "bold"))
            self.aimbot_fov.place(relx=0.35, rely=0.3-0.04)
            
            self.color_fov_btn = CTkButton(self, hover_color="#494949", width=245, height=15, text="Fov Color", text_color="#ffffff", fg_color="#121212", font=("Helvetica", 13, "bold"), border_width=2, command=lambda:self.ask_color("fov_color"))
            self.color_fov_btn.place(relx=0.13, rely=0.38-0.04)
            
            self.AimbotFovRadioVar = 70
            def fov_slider_event(value):
                self.AimbotFovRadioVar = int(value)
                self.var_update("")
            self.lb_1 = CTkLabel(self, text="Fov Radio", fg_color="#121212", font=("Helvetica", 12, "bold"))
            self.lb_1.place(relx=0.13, rely=0.45-0.04)
            self.slider_fov = CTkSlider(self, width=170, from_=0, to=200, number_of_steps=25, border_color="#ffffff", border_width=2, fg_color="#121212", bg_color="#121212", progress_color="#F601F7", button_color="#ffffff", button_hover_color="#121212", command=fov_slider_event)
            self.slider_fov.place(relx=0.225, rely=0.463-0.04)
            
            
            self.slider_distance = CTkCheckBox(self, text="Distance Close", command=lambda:self.var_update(""), variable=self.AimbotDistance_var,onvalue=True, offvalue=False, bg_color="#121212", font=("Helvetica", 14, "bold"), checkmark_color="#F601F7", fg_color="#121212", border_color="#393939", hover_color="#ffffff")
            self.slider_distance.place(relx=0.13, rely=0.533-0.05)
            
            
            def smooth_aimbot_event(value):
                AimbotSmooth = int(value)
                MemoryAccess.Aimbot_Steps = AimbotSmooth
            self.lb_3 = CTkLabel(self, text="Aimbot Smooth", fg_color="#121212", font=("Helvetica", 12, "bold"), bg_color="#121212")
            self.lb_3.place(relx=0.13, rely=0.59-0.04)
            self.slider_smoooth = CTkSlider(self, width=148, from_=1, to=100, number_of_steps=100, border_color="#ffffff", border_width=2, fg_color="#121212", bg_color="#121212", progress_color="#F601F7", button_color="#ffffff", button_hover_color="#121212", command=smooth_aimbot_event)
            self.slider_smoooth.place(relx=0.255, rely=0.60-0.04)
            
            def radiobutton_event():
                print("radiobutton toggled, current value:", self.radio_var.get())
                self.var_update("radio_button")
            self.radio_var = IntVar(value=1)
            self.radiobutton_1 = CTkRadioButton(self, text="Head",
                                                        command=radiobutton_event, variable= self.radio_var, value=1, bg_color="#121212", border_width_checked=5,
                                                        border_width_unchecked=2, hover_color="#F601F7", fg_color="#ffffff")
            self.radiobutton_2 = CTkRadioButton(self, text="Neck",
                                                        command=radiobutton_event, variable= self.radio_var, value=2, bg_color="#121212", border_width_checked=5,
                                                        border_width_unchecked=2, hover_color="#F601F7", fg_color="#ffffff")
            self.radiobutton_3 = CTkRadioButton(self, text="Body",
                                                        command=radiobutton_event, variable= self.radio_var, value=3, bg_color="#121212", border_width_checked=5,
                                                        border_width_unchecked=2, hover_color="#F601F7", fg_color="#ffffff")
            self.radiobutton_1.place(relx=0.13, rely=0.67-0.04)
            self.radiobutton_2.place(relx=0.25, rely=0.67-0.04)
            self.radiobutton_3.place(relx=0.35, rely=0.67-0.04)
            
            self.lb_5 = CTkLabel(self, text="Aimbot Key", fg_color="#121212", font=("Helvetica", 12, "bold"), bg_color="#121212")
            self.lb_5.place(relx=0.13, rely=0.74-0.03)
            
            
            self.key_aimbot = "Button.right"
            
            def get_btn_aimbot():
                print("Pressione uma tecla ou clique com o mouse para capturar...")
                captured = {"value": None}
                # Função para capturar teclas pressionadas
                def on_key_press(key):
                    if not captured["value"]:  # Verifica se já foi capturado algo
                        try:
                            captured["value"] = key.char  # Captura teclas alfanuméricas
                        except AttributeError:
                            captured["value"] = str(key)  # Captura teclas especiais
                        return False  # Para o listener do teclado
                # Função para capturar cliques do mouse
                def on_click(x, y, button, pressed):
                    if not captured["value"] and pressed:  # Captura apenas no clique inicial
                        captured["value"] = str(button)
                        return False  # Para o listener do mouse
                # Inicializa os listeners para teclado e mouse
                keyboard_listener = keyboard.Listener(on_press=on_key_press)
                mouse_listener = mouse.Listener(on_click=on_click)
                # Inicia os listeners
                keyboard_listener.start()
                mouse_listener.start()
                # Espera até que uma entrada seja capturada
                while not captured["value"]:
                    pass
                # Para os listeners
                keyboard_listener.stop()
                mouse_listener.stop()
                self.key_aimbot = captured["value"]
                self.key_aimbot_btn.configure(text=f"{self.key_aimbot}")
                MemoryAccess.aimbot_key = f"{self.key_aimbot}"
                
            self.key_aimbot_btn = CTkButton(self, text=f"{self.key_aimbot}", command=lambda:threading.Thread(target=get_btn_aimbot).start(), hover_color="#494949", width=110, height=15, fg_color="#121212", font=("Helvetica", 13, "bold"), bg_color="#121212", border_width=2)
            self.key_aimbot_btn.place(relx=0.225, rely=0.74-0.025)
            
            
            self.closest_enemy_glow = CTkCheckBox(self, text="Closest Enemy Glow", command=lambda:self.var_update(""), variable=self.closest_enemy_glow_var,onvalue=True, offvalue=False, bg_color="#121212", font=("Helvetica", 14, "bold"), checkmark_color="#F601F7", fg_color="#121212", border_color="#393939", hover_color="#ffffff")
            self.closest_enemy_glow.place(relx=0.13, rely=0.84-0.025)
            self.color_glow_btn = CTkButton(self, hover_color="#494949", width=50, height=15, text="Color Glow", text_color="#ffffff", fg_color="#121212", font=("Helvetica", 13, "bold"), border_width=2, command=lambda:self.ask_color("closest_enemy_glow"))
            self.color_glow_btn.place(relx=0.365, rely=0.84-0.022)
            
            # Hit Sound
            self.frame_02 = CTkFrame(self, fg_color="#121212", width=300, height=70, bg_color="#000000", corner_radius=10, border_color="#ffffff", border_width=2)
            self.frame_02.place(relx=0.5, rely=0.8-0.04)
            self.hit_sound = CTkCheckBox(self, text="Hit Sound",onvalue=True, offvalue=False, bg_color="#121212", font=("Helvetica", 14, "bold"), checkmark_color="#F601F7", fg_color="#121212", border_color="#393939", hover_color="#ffffff")
            self.hit_sound.place(relx=0.53, rely=0.85-0.04)
            
            # Trigger
            self.frame_03 = CTkFrame(self, fg_color="#121212", width=300, height=135, bg_color="#000000", corner_radius=10, border_color="#ffffff", border_width=2)
            self.frame_03.place(relx=0.5, rely=0.27-0.04)
            self.trigger = CTkCheckBox(self, text="Triggerbot",onvalue=True, offvalue=False, bg_color="#121212", font=("Helvetica", 14, "bold"), checkmark_color="#F601F7", fg_color="#121212", border_color="#393939", hover_color="#ffffff")
            self.trigger.place(relx=0.53, rely=0.3-0.04)
            
            self.lb_4 = CTkLabel(self, text="Key", fg_color="#121212", font=("Helvetica", 12, "bold"), bg_color="#121212")
            self.lb_4.place(relx=0.53, rely=0.34)
            key_trigger = "Key.alt_l"
            self.key_trigger_btn = CTkButton(self, text=f"{key_trigger}", hover_color="#494949", width=110, height=15, fg_color="#121212", font=("Helvetica", 13, "bold"), bg_color="#121212", border_width=2)
            self.key_trigger_btn.place(relx=0.57, rely=0.344)
            
            self.lb_7 = CTkLabel(self, text="Triggerbot delay", fg_color="#121212", font=("Helvetica", 12, "bold"), bg_color="#121212")
            self.lb_7.place(relx=0.53, rely=0.42)
            self.lb_6 = CTkLabel(self, text="(ms)", fg_color="#121212", font=("Helvetica", 12, "bold"), bg_color="#121212")
            self.lb_6.place(relx=0.8, rely=0.42)
            self.delay_entry = CTkEntry(self, fg_color="#121212", bg_color="#121212", border_width=2, width=100)
            self.delay_entry.place(relx=0.66, rely=0.424)
            
            
            # Visuals
            try:
                self.Indicator_01.configure(fg_color="#000000")
                self.Indicator_02.configure(fg_color="#F601F7")
                self.Indicator_03.configure(fg_color="#000000")
                self.Indicator_04.configure(fg_color="#000000")
                self.checkbox_01.destroy()
                self.checkbox_02.destroy()
                self.checkbox_03.destroy()
                self.checkbox_04.destroy()
                self.checkbox_05.destroy()
                self.checkbox_06.destroy()
                self.checkbox_07.destroy()
                self.checkbox_08.destroy()
                self.esp_box_btn.destroy()
                self.esp_name_btn.destroy()
                self.esp_health_btn.destroy()
                self.esp_armor_btn.destroy()
                self.esp_skeleton_btn.destroy()
                self.esp_line_btn.destroy()
                self.esp_distance_btn.destroy()
                self.esp_glow_btn.destroy()
                self.other_options.destroy()
                self.fire_enemy.destroy()
                self.ThirdPerson.destroy()
                self.Fov.destroy()
                self.NoFlash.destroy()
                self.slider.destroy()
            except:
                pass
            
            # Misc
            # Options
        
        if menu == "Misc":
            pass
            # Visuals
            # Aimbot
            # Options
            
        if menu == "Options":
            pass
            # Visuals
            # Aimbot
            # Misc
            
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    def actions_update(self):
        self.after(100, self.actions_update)
        if win32api.GetAsyncKeyState(win32con.VK_INSERT):
            self.visible = not self.visible
            # Pressionar a tecla ESC
            win32api.keybd_event(win32con.VK_ESCAPE, 0, win32con.KEYEVENTF_UNICODE, 0)
            # Aguardar um pequeno intervalo para simular o "tempo de pressionamento"
            time.sleep(0.1)
            # Soltar a tecla ESC
            win32api.keybd_event(win32con.VK_ESCAPE, 0, win32con.KEYEVENTF_KEYUP, 0)
        
        if self.visible:
            self.withdraw()
            try:
                self.win.withdraw()
            except:
                pass
        else:
            self.deiconify()
            try:
                self.win.deiconify()
            except:
                pass
    
    def load_vars(self):
        self.Esp_box_switch       = BooleanVar()
        self.Esp_name_switch      = BooleanVar()
        self.Esp_health_switch    = BooleanVar()
        self.Esp_armor_switch     = BooleanVar()
        self.Esp_skeleton_switch  = BooleanVar()
        self.Esp_glow_switch      = BooleanVar()
        self.Esp_line_switch      = BooleanVar()
        self.Esp_distance_switch  = BooleanVar()
        self.Fire_enemy_switch    = BooleanVar()
        self.NoFlash_switch       = BooleanVar()
        self.ThirdPerson_switch   = BooleanVar()
        self.FovPlayer_switch     = BooleanVar()
        
        self.aimbot_var             = BooleanVar()
        self.AimFovVar              = BooleanVar()
        self.AimbotDistance_var     = BooleanVar()
        self.closest_enemy_glow_var = BooleanVar()
    
    def var_update(self, type_):
        global Esp_box_switch, Esp_name_switch, FovPlayer_switch, Esp_health_switch, Esp_armor_switch, Esp_skeleton_switch, Esp_glow_switch, AimbotFovRadio
        global Esp_line_switch, Esp_distance_switch, Fire_enemy_switch, NoFlash_switch, ThirdPerson_switch, Aimbot_Switch, AimbotFov_Switch, AimbotDistance
        global Esp_box_color, Esp_name_color, Esp_health_color, Esp_armor_color, Esp_skeleton_color, Esp_glow_color, Esp_line_color, Esp_distance_color, closest_enemy_glow_switch
        global Esp_box_color_art, Esp_name_color_art, Esp_health_color_art, Esp_armor_color_art, Esp_skeleton_color_art, Esp_glow_color_art, Esp_line_color_art, Esp_distance_color_art
        Esp_box_switch       = self.Esp_box_switch.get()
        Esp_name_switch      = self.Esp_name_switch.get()
        Esp_health_switch    = self.Esp_health_switch.get()
        Esp_armor_switch     = self.Esp_armor_switch.get()
        Esp_skeleton_switch  = self.Esp_skeleton_switch.get()
        Esp_glow_switch      = self.Esp_glow_switch.get()
        Esp_line_switch      = self.Esp_line_switch.get()
        Esp_distance_switch  = self.Esp_distance_switch.get()
        Fire_enemy_switch    = self.Fire_enemy_switch.get()
        NoFlash_switch       = self.NoFlash_switch.get()
        ThirdPerson_switch   = self.ThirdPerson_switch.get()
        FovPlayer_switch     = self.FovPlayer_switch.get()
        Aimbot_Switch        = self.aimbot_var.get()
        AimbotFov_Switch     = self.AimFovVar.get()
        AimbotDistance       = self.AimbotDistance_var.get()
        
        if Aimbot_Switch:
            MemoryAccess.MemmoActiveAimbot("Aimbot")
        if not Aimbot_Switch:
            MemoryAccess.MemmoActiveAimbot("AimbotOff")
        
        AimbotFovRadio            = self.AimbotFovRadioVar
        closest_enemy_glow_switch = self.closest_enemy_glow_var.get()
        
        if type_ == "radio_button":
            if self.radio_var.get() == 1:
                Aimbot_focus = "Head"
                MemoryAccess.Aimbot_focus = Aimbot_focus
            if self.radio_var.get() == 2:
                Aimbot_focus = "Neck"
                MemoryAccess.Aimbot_focus = Aimbot_focus
            if self.radio_var.get() == 3:
                Aimbot_focus = "Body"
                MemoryAccess.Aimbot_focus = Aimbot_focus
                
    
    def ask_color(self, type_color):
        global Esp_box_color, Esp_name_color, Esp_health_color, Esp_armor_color, Esp_skeleton_color, Esp_glow_color, Esp_line_color, Esp_distance_color, AimbotFovColor, Esp_glow_color_art
        # Abrir o seletor de cores do CTkColorPicker
        pick_color = AskColor(bg_color="#000000", button_color="#121212", fg_color="#000000", button_hover_color="#F601F7")  # Seletor de cores
        color = pick_color.get()  # Obtém a cor como uma string hex
        if color:
            if type_color == "closest_enemy_glow":
                # Determina se a cor é clara ou escura
                r, g, b = self.hex_to_rgb(color)
                brightness = (r * 299 + g * 587 + b * 114) / 1000  # Fórmula de luminosidade (perceptual)
                
                # Se o brilho for baixo, a cor é escura, então mudamos o texto para branco
                if brightness < 128:
                    self.color_glow_btn.configure(text_color="white")
                else:
                    self.color_glow_btn.configure(text_color="black")
                self.color_glow_btn.configure(fg_color=color)
                
                glow_hex = color
                glow_color_closest_enemy  = int(glow_hex[1:], 16)
                # O valor de cor que recebemos já é RGB, então precisamos rearranjar para BGR
                glow_color_with_alpha = (0x80 << 24) | ((glow_color_closest_enemy & 0x0000FF) << 16) | ((glow_color_closest_enemy & 0x00FF00)) | ((glow_color_closest_enemy & 0xFF0000) >> 16)
                MemoryAccess.closest_enemy_glow_color = glow_color_with_alpha
            
            
            if type_color == "fov_color":
                # Determina se a cor é clara ou escura
                r, g, b = self.hex_to_rgb(color)
                brightness = (r * 299 + g * 587 + b * 114) / 1000  # Fórmula de luminosidade (perceptual)
                
                # Se o brilho for baixo, a cor é escura, então mudamos o texto para branco
                if brightness < 128:
                    self.color_fov_btn.configure(text_color="white")
                else:
                    self.color_fov_btn.configure(text_color="black")
                self.color_fov_btn.configure(fg_color=color)
                AimbotFovColor = (r,g,b)
                
                
            
            if type_color == "esp_box":
                # Determina se a cor é clara ou escura
                r, g, b = self.hex_to_rgb(color)
                brightness = (r * 299 + g * 587 + b * 114) / 1000  # Fórmula de luminosidade (perceptual)
                
                # Se o brilho for baixo, a cor é escura, então mudamos o texto para branco
                if brightness < 128:
                    self.esp_box_btn.configure(text_color="white")
                else:
                    self.esp_box_btn.configure(text_color="black")
                self.esp_box_btn.configure(fg_color=color)
                Esp_box_color = (r,g,b)
                
                
            if type_color == "esp_name":
                # Determina se a cor é clara ou escura
                r, g, b = self.hex_to_rgb(color)
                brightness = (r * 299 + g * 587 + b * 114) / 1000  # Fórmula de luminosidade (perceptual)
                
                # Se o brilho for baixo, a cor é escura, então mudamos o texto para branco
                if brightness < 128:
                    self.esp_name_btn.configure(text_color="white")
                else:
                    self.esp_name_btn.configure(text_color="black")
                self.esp_name_btn.configure(fg_color=color)
                Esp_name_color = (r,g,b)
                
                
            if type_color == "esp_health":
                # Determina se a cor é clara ou escura
                r, g, b = self.hex_to_rgb(color)
                brightness = (r * 299 + g * 587 + b * 114) / 1000  # Fórmula de luminosidade (perceptual)
                
                # Se o brilho for baixo, a cor é escura, então mudamos o texto para branco
                if brightness < 128:
                    self.esp_health_btn.configure(text_color="white")
                else:
                    self.esp_health_btn.configure(text_color="black")
                self.esp_health_btn.configure(fg_color=color)
                Esp_health_color = (r,g,b)
                
                
            if type_color == "esp_armor":
                # Determina se a cor é clara ou escura
                r, g, b = self.hex_to_rgb(color)
                brightness = (r * 299 + g * 587 + b * 114) / 1000  # Fórmula de luminosidade (perceptual)
                
                # Se o brilho for baixo, a cor é escura, então mudamos o texto para branco
                if brightness < 128:
                    self.esp_armor_btn.configure(text_color="white")
                else:
                    self.esp_armor_btn.configure(text_color="black")
                self.esp_armor_btn.configure(fg_color=color)
                Esp_armor_color = (r,g,b)
                
                
            if type_color == "esp_skeleton":
                # Determina se a cor é clara ou escura
                r, g, b = self.hex_to_rgb(color)
                brightness = (r * 299 + g * 587 + b * 114) / 1000  # Fórmula de luminosidade (perceptual)
                
                # Se o brilho for baixo, a cor é escura, então mudamos o texto para branco
                if brightness < 128:
                    self.esp_skeleton_btn.configure(text_color="white")
                else:
                    self.esp_skeleton_btn.configure(text_color="black")
                self.esp_skeleton_btn.configure(fg_color=color)
                Esp_skeleton_color = (r,g,b)
                
                
            if type_color == "esp_line":
                # Determina se a cor é clara ou escura
                r, g, b = self.hex_to_rgb(color)
                brightness = (r * 299 + g * 587 + b * 114) / 1000  # Fórmula de luminosidade (perceptual)
                
                # Se o brilho for baixo, a cor é escura, então mudamos o texto para branco
                if brightness < 128:
                    self.esp_line_btn.configure(text_color="white")
                else:
                    self.esp_line_btn.configure(text_color="black")
                self.esp_line_btn.configure(fg_color=color)
                Esp_line_color = (r,g,b)
                
                
            if type_color == "esp_distance":
                # Determina se a cor é clara ou escura
                r, g, b = self.hex_to_rgb(color)
                brightness = (r * 299 + g * 587 + b * 114) / 1000  # Fórmula de luminosidade (perceptual)
                
                # Se o brilho for baixo, a cor é escura, então mudamos o texto para branco
                if brightness < 128:
                    self.esp_distance_btn.configure(text_color="white")
                else:
                    self.esp_distance_btn.configure(text_color="black")
                self.esp_distance_btn.configure(fg_color=color)
                Esp_distance_color = (r,g,b)
                
                
            if type_color == "esp_glow":
                # Determina se a cor é clara ou escura
                r, g, b = self.hex_to_rgb(color)
                brightness = (r * 299 + g * 587 + b * 114) / 1000  # Fórmula de luminosidade (perceptual)
                
                # Se o brilho for baixo, a cor é escura, então mudamos o texto para branco
                if brightness < 128:
                    self.esp_glow_btn.configure(text_color="white")
                else:
                    self.esp_glow_btn.configure(text_color="black")
                self.esp_glow_btn.configure(fg_color=color)
                Esp_glow_color = (r,g,b)
                Esp_glow_color_art = color
                
            
        return color

    def hex_to_rgb(self, hex_color):
        """Converte a cor hexadecimal para RGB"""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return r, g, b
    
    
    # Função responsável pelo movimento pela barra de tarefas
    def CustomTitleBar(self, event):
        xwin = self.winfo_x()
        ywin = self.winfo_y()
        startx = event.x_root
        starty = event.y_root

        ywin = ywin - starty
        xwin = xwin - startx

        def move_window(event):
            self.geometry(f"{780}x{450}" + '+{0}+{1}'.format(event.x_root + xwin, event.y_root + ywin))
        startx = event.x_root
        starty = event.y_root

        self.TopFrame.bind('<B1-Motion>', move_window)
        
    



























Esp_box_switch       = False
Esp_name_switch      = False
Esp_health_switch    = False
Esp_armor_switch     = False
Esp_skeleton_switch  = False
Esp_glow_switch      = False
Esp_line_switch      = False
Esp_distance_switch  = False
Fire_enemy_switch    = False
NoFlash_switch       = False
ThirdPerson_switch   = False
FovPlayer_switch     = False

Esp_box_color       = (255,0,0)
Esp_name_color      = (255,255,255)
Esp_health_color    = (0,255,0)
Esp_armor_color     = (0,0,255)
Esp_skeleton_color  = (0,255,255)
Esp_glow_color      = (255,0,0)
Esp_line_color      = (255,255,0)
Esp_distance_color  = (255,255,255)

Esp_box_color_art       = "#ff0000"
Esp_name_color_art      = "#ffffff"
Esp_health_color_art    = "#00ff00"
Esp_armor_color_art     = "#0000ff"
Esp_skeleton_color_art  = "#00ffff"
Esp_glow_color_art      = "#ff0000"
Esp_line_color_art      = "#ffff00"
Esp_distance_color_art  = "#ffffff"

Aimbot_Switch             = False
AimbotFov_Switch          = False
AimbotFovRadio            = 70
AimbotFovColor            = (246, 1, 247)
AimbotDistance            = False
closest_enemy_glow_switch = False

PlayerFov = 0

class MainInvisibleWindowController(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_NoChildEventsForParent, True)
        self.setWindowFlags(Qt.Window|Qt.X11BypassWindowManagerHint|Qt.WindowStaysOnTopHint|Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMouseTracking(True)  # Permite que o mouse seja rastreado na janela
        self.resize(1920, 1080)

        # Configurar Timer para atualizar a janela
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)  # Chamará o paintEvent periodicamente
        # self.timer.start(4)  # Atualiza a cada ~16ms (~60 FPS)
        self.timer.start(0)  # Atualiza a cada ~16ms (~60 FPS)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        if Esp_box_switch:
            coords_box = MemoryAccess.MemmoActive("Box")

            for screen_head_pos, screen_boot_pos in coords_box:
                if not (screen_head_pos and screen_boot_pos):
                    continue  # Pule se a conversão falhar ou as coordenadas forem inválidas

                # Calcula altura e largura da caixa
                height = screen_head_pos[1] - screen_boot_pos[1]
                width = height / 2  # Define a largura como metade da altura

                # Define os pontos da caixa
                top_left = (screen_head_pos[0] - width / 2, screen_head_pos[1])
                top_right = (screen_head_pos[0] + width / 2, screen_head_pos[1])
                bottom_left = (screen_boot_pos[0] - width / 2, screen_boot_pos[1])
                bottom_right = (screen_boot_pos[0] + width / 2, screen_boot_pos[1])

                # Desenha as bordas da caixa
                painter.drawLine(int(top_left[0]), int(top_left[1]), int(top_right[0]), int(top_right[1]))  # Linha superior
                painter.drawLine(int(bottom_left[0]), int(bottom_left[1]), int(bottom_right[0]), int(bottom_right[1]))  # Linha inferior
                painter.drawLine(int(top_left[0]), int(top_left[1]), int(bottom_left[0]), int(bottom_left[1]))  # Linha esquerda
                painter.drawLine(int(top_right[0]), int(top_right[1]), int(bottom_right[0]), int(bottom_right[1]))  # Linha direita


                    
        if Esp_name_switch:
            coords_names = MemoryAccess.MemmoActive("Name")
            if coords_names:  # Verifica se há entidades detectadas
                for head_x, head_y, names in coords_names:
                    # Configurando a fonte e a cor
                    font = QFont("Arial", 12)  # Tamanho 12
                    painter.setFont(font)
                    painter.setPen(QColor(*Esp_name_color, 255))  # Adiciona transparência diretamente

                    # Medindo o tamanho do texto
                    text_width = QFontMetrics(font).width(names)
                    text_height = QFontMetrics(font).height()

                    # Calculando a posição para centralizar o texto
                    x_pos = head_x - text_width / 2
                    y_pos = head_y - text_height / 2 - 10

                    # Desenhando o texto
                    painter.drawText(int(x_pos), int(y_pos), names)

                        
        if Esp_health_switch:
            coords_health = MemoryAccess.MemmoActive("Health")
            for screen_head_pos, screen_boot_pos, health, armor in coords_health:
                # Calcula altura e largura da caixa
                height = screen_head_pos[1] - screen_boot_pos[1]
                dx = screen_boot_pos[0] - screen_head_pos[0]

                # Porcentagens de saúde e armadura
                health_perc = health / 100.0

                health_height = height * health_perc
                bot_health_y = screen_boot_pos[1]
                bot_health_x = screen_boot_pos[0] + (height / 4) - 0
                
                top_health_y = screen_head_pos[1] +  health_height - height
                top_health_x = screen_boot_pos[0] + (height / 4) - 0 - (dx * health_perc)

                # Desenhar contorno da barra de saúde (cor mais clara)
                painter.setPen(QColor(18, 18, 18, 255))  # Verde claro para o contorno
                painter.drawLine(int(bot_health_x) - 1, int(bot_health_y) - 1, int(top_health_x) - 1, int(top_health_y) - 1)
                painter.drawLine(int(bot_health_x) + 1, int(bot_health_y) - 1, int(top_health_x) + 1, int(top_health_y) - 1)
                painter.drawLine(int(bot_health_x) - 1, int(bot_health_y) + 1, int(top_health_x) - 1, int(top_health_y) + 1)
                painter.drawLine(int(bot_health_x) + 1, int(bot_health_y) + 1, int(top_health_x) + 1, int(top_health_y) + 1)

                # Desenhar a barra de saúde (agora na posição da barra de armadura)
                pen = QPen(QColor(*Esp_health_color), 1)  # Adiciona a cor com transparência
                painter.setPen(pen)
                painter.drawLine(int(bot_health_x), int(bot_health_y), int(top_health_x), int(top_health_y))


                
        if Esp_armor_switch:
            coords_armor = MemoryAccess.MemmoActive("Armor")
            for screen_head_pos, screen_boot_pos, health, armor in coords_armor:
                # Calcula altura e largura da caixa
                height = screen_head_pos[1] - screen_boot_pos[1]
                dx = screen_boot_pos[0] - screen_head_pos[0]
                
                armor_perc = armor / 100.0

                armor_height = height * armor_perc
                bot_armor_y = screen_boot_pos[1]
                bot_armor_x = screen_boot_pos[0] - (height / 4) + 0
                top_armor_y = screen_head_pos[1] + armor_height - height
                top_armor_x = screen_boot_pos[0] - (height / 4) + 0 - (dx * armor_perc)

                # Desenhar contorno da barra de armadura (cor mais clara)
                painter.setPen(QColor(18, 18, 18, 255))  # Verde claro para o contorno
                painter.setBrush(Qt.NoBrush)  # Não preencher a forma, apenas o contorno
                painter.drawLine(int(bot_armor_x) - 1, int(bot_armor_y) - 1, int(top_armor_x) - 1, int(top_armor_y) - 1)
                painter.drawLine(int(bot_armor_x) + 1, int(bot_armor_y) - 1, int(top_armor_x) + 1, int(top_armor_y) - 1)
                painter.drawLine(int(bot_armor_x) - 1, int(bot_armor_y) + 1, int(top_armor_x) - 1, int(top_armor_y) + 1)
                painter.drawLine(int(bot_armor_x) + 1, int(bot_armor_y) + 1, int(top_armor_x) + 1, int(top_armor_y) + 1)

                # Desenhar a barra de armadura (agora na posição da barra de saúde)
                pen = QPen(QColor(*Esp_armor_color), 1)  # Adiciona a cor com transparência
                painter.setPen(pen)
                painter.drawLine(int(bot_armor_x), int(bot_armor_y), int(top_armor_x), int(top_armor_y))

                    
        if Esp_skeleton_switch:
            coords_skeleton = MemoryAccess.MemmoActive("Skeleton")
            for screen_bone_1, screen_bone_2 in coords_skeleton:
                pen = QPen(QColor(*Esp_skeleton_color), 0.5)  # Linha mais fina com espessura 0.5 (se possível)
                painter.setPen(pen)
                painter.drawLine(int(screen_bone_1[0]), int(screen_bone_1[1]), int(screen_bone_2[0]), int(screen_bone_2[1]))


        if Esp_line_switch:
            coords_line = MemoryAccess.MemmoActive("Line")
            for screen_boot_pos, window_size in coords_line:
                pen = QPen(QColor(*Esp_line_color), 0.5)  # Adiciona a cor com transparência
                painter.setPen(pen)
                painter.drawLine(int(screen_boot_pos[0]), int(screen_boot_pos[1]), int(window_size[0] / 2), int(window_size[1]))

        
        if Esp_distance_switch:
            coords_distance = MemoryAccess.MemmoActive("Distance")
            if coords_distance:  # Verifica se há entidades detectadas
                for boot, distance in coords_distance:
                    # Ajustar o tamanho da fonte com base na distância
                    font_size = int(max(10, min(30, 40 - (distance / 10))))  # Converte para inteiro
                    
                    font = QFont("Arial", font_size)  # Usando a fonte ajustada
                    painter.setFont(font)
                    text = f"{int(distance)}"
                    
                    # Calculando a largura do texto
                    text_width = painter.fontMetrics().horizontalAdvance(text)
                    
                    # Ajustando a posição do texto para centralizá-lo
                    x_pos = boot[0] - text_width / 2
                    y_pos = boot[1] - 10
                    
                    painter.setPen(QPen(QColor(*Esp_distance_color), 1))  # Adiciona a cor com transparência
                    painter.drawText(int(x_pos), int(y_pos), text)  # Ajustando a posição do texto


                
        if Esp_glow_switch:
            # Remover o '#' e converter a string para um número inteiro (base 16)
            glow_color_hex = int(Esp_glow_color_art[1:], 16)
            # Agora, converter para ARGB na ordem Alpha (0x80), Blue, Green, Red
            # Alpha vai para o primeiro byte (0x80)
            # O valor de cor que recebemos já é RGB, então precisamos rearranjar para BGR
            glow_color_with_alpha = (0x80 << 24) | ((glow_color_hex & 0x0000FF) << 16) | ((glow_color_hex & 0x00FF00)) | ((glow_color_hex & 0xFF0000) >> 16)
            MemoryAccess.glow_color_hex = glow_color_with_alpha
            MemoryAccess.MemmoActive("Glow")
        
        if Fire_enemy_switch:
            MemoryAccess.MemmoActive("FireOn")
        # elif not Fire_enemy_switch:
        #     MemoryAccess.MemmoActive("FireOff")
            
        if NoFlash_switch:
            MemoryAccess.MemmoActive("NoFlash")
            
        if FovPlayer_switch:
            MemoryAccess.player_fov_value = PlayerFov
            MemoryAccess.MemmoActive("FovChangerOn")
        elif not FovPlayer_switch:
            MemoryAccess.MemmoActive("FovChangerOff")
        
        if ThirdPerson_switch:
            MemoryAccess.MemmoActive("ThirdPersonOn")
        else:
            MemoryAccess.MemmoActive("ThirdPersonOff")

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        # if Aimbot_Switch:
        #     MemoryAccess.MemmoActiveAimbot("Aimbot")
        if AimbotFov_Switch:
            MemoryAccess.AimbotFovActive = True
            MemoryAccess.AimbotFovRadio = AimbotFovRadio
            # Desenhar o círculo
            painter.setPen(QPen(QColor(*AimbotFovColor), 1))  # Cor da borda
            painter.setBrush(Qt.NoBrush)  # Sem preenchimento
            window_size = [win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)]
            # Calcular o centro da tela
            center_x = window_size[0] // 2
            center_y = window_size[1] // 2
            # Corrigir as coordenadas do círculo
            painter.drawEllipse(
                center_x - AimbotFovRadio,  # Ajustar X pelo raio
                center_y - AimbotFovRadio,  # Ajustar Y pelo raio
                AimbotFovRadio * 2,         # Diâmetro na largura
                AimbotFovRadio * 2          # Diâmetro na altura
            )
        if not AimbotFov_Switch:
            MemoryAccess.AimbotFovActive = False
        
        if closest_enemy_glow_switch:
            MemoryAccess.MemmoActiveAimbot("ClosestEnemyGlowOn")
            
        if AimbotDistance:
            MemoryAccess.MemmoActiveAimbot("CloseDistanceOn")
        else:
            MemoryAccess.MemmoActiveAimbot("CloseDistanceOff")
            

# Função para rodar o PyQt
def run_pyqt():
    app = QApplication(sys.argv)
    window = MainInvisibleWindowController()
    window.show()
    sys.exit(app.exec_())
        
# Inicializando a aplicação Tkinter
if __name__ == "__main__":
    loader = LoaderWindow()
    loader.mainloop()
