import win32api
import pymem
import funcs
import math
import json
import threading
import win32api, win32con
import time

class Offsets:
    def __init__(self, offsets_dict):
        # Inicializa o objeto com o dicionário de offsets
        self.__dict__ = offsets_dict
    
    # Método para representar os valores em hexadecimal
    def __getattr__(self, name):
        value = self.__dict__.get(name)
        if value is not None:
            return value
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

# Carregar os offsets do arquivo JSON
with open('offsets.json', 'r') as f:
    offsets_data = json.load(f)

# Criar a instância da classe Offsets
offsets = Offsets(offsets_data)


mem = pymem.Pymem("cs2.exe")
client = pymem.pymem.process.module_from_name(mem.process_handle, "client.dll").lpBaseOfDll
glow_color_hex = 0x80FF0000  # Cor vermelha
player_fov_value = 0
aimbot_key = "Button.right"
trigger_key = "Key.alt_l"
Aimbot_focus = "Head"
Aimbot_smooth = 0.008
Aimbot_Steps = 10
AimbotFovActive = False
AimbotFovRadio = 70
closest_enemy_glow_color = 0x80F601F7
AimbotCloseDistanceSwitch = False







AimbotThread = False
















############################################# AIMBOT #############################################
def is_mouse_pressed(target_button):
    """
    Verifica se o botão do mouse especificado está pressionado.
    """
    button_map = {
        "Button.left": win32con.VK_LBUTTON,
        "Button.right": win32con.VK_RBUTTON,
        "Button.middle": win32con.VK_MBUTTON,
        "Button.x1": win32con.VK_XBUTTON1,
        "Button.x2": win32con.VK_XBUTTON2
    }
    vk_code = button_map.get(target_button)
    return vk_code and win32api.GetAsyncKeyState(vk_code) < 0

def is_key_pressed(target_key):
    """
    Verifica se a tecla especificada está pressionada.
    """
    special_keys = {
        "Key.ctrl": win32con.VK_CONTROL,
        "Key.shift": win32con.VK_SHIFT,
        "Key.alt": win32con.VK_MENU,
        "Key.alt_l": win32con.VK_LMENU,
        "Key.alt_r": win32con.VK_RMENU,
        "Key.ctrl_l": win32con.VK_LCONTROL,
        "Key.ctrl_r": win32con.VK_RCONTROL,
        "Key.shift_l": win32con.VK_LSHIFT,
        "Key.shift_r": win32con.VK_RSHIFT,
        "Key.esc": win32con.VK_ESCAPE,
        "Key.tab": win32con.VK_TAB,
        "Key.enter": win32con.VK_RETURN,
        "Key.space": win32con.VK_SPACE,
        "Key.backspace": win32con.VK_BACK,
        "Key.delete": win32con.VK_DELETE,
        "Key.insert": win32con.VK_INSERT,
        "Key.up": win32con.VK_UP,
        "Key.down": win32con.VK_DOWN,
        "Key.left": win32con.VK_LEFT,
        "Key.right": win32con.VK_RIGHT,
        "Key.home": win32con.VK_HOME,
        "Key.end": win32con.VK_END,
        "Key.page_up": win32con.VK_PRIOR,
        "Key.page_down": win32con.VK_NEXT,
        "Key.caps_lock": win32con.VK_CAPITAL,
        "Key.num_lock": win32con.VK_NUMLOCK,
        "Key.scroll_lock": win32con.VK_SCROLL,
        "Key.f1": win32con.VK_F1,
        "Key.f2": win32con.VK_F2,
        "Key.f3": win32con.VK_F3,
        "Key.f4": win32con.VK_F4,
        "Key.f5": win32con.VK_F5,
        "Key.f6": win32con.VK_F6,
        "Key.f7": win32con.VK_F7,
        "Key.f8": win32con.VK_F8,
        "Key.f9": win32con.VK_F9,
        "Key.f10": win32con.VK_F10,
        "Key.f11": win32con.VK_F11,
        "Key.f12": win32con.VK_F12
    }

    # Verifica se é uma tecla especial
    if target_key in special_keys:
        vk_code = special_keys[target_key]
    else:
        try:
            vk_code = ord(target_key.upper())  # Para teclas alfanuméricas
        except (TypeError, ValueError):
            return False  # Retorna False se o input não for uma tecla válida

    return vk_code and win32api.GetAsyncKeyState(vk_code) < 0


def distance(p1, p2):
    return math.sqrt(pow(p1[0] - p2[0], 2) + pow(p1[1] - p2[1], 2) + pow(p1[2] - p2[2], 2))

def normalize_yaw(yaw):
    if yaw > 180.0:
        yaw -= 360.0
    elif yaw < -180.0:
        yaw += 360.0
    return yaw

def smooth_aim(current_x, current_y, target_x, target_y):
    global Aimbot_Steps
    step_x = (target_x - current_x) / Aimbot_Steps
    step_y = (target_y - current_y) / Aimbot_Steps
    for i in range(Aimbot_Steps):
        current_x += step_x
        current_y += step_y
        # Normaliza os ângulos para evitar valores inválidos
        current_x = normalize_yaw(current_x)
        current_y = max(-89.0, min(89.0, current_y))
        # Escreve os novos ângulos na memória
        mem.write_float(client + int(offsets.dwViewAngles), current_y)  # Pitch (Y)
        mem.write_float(client + int(offsets.dwViewAngles) + 0x4, current_x)  # Yaw (X)
        time.sleep(0.0009)  # Ajuste o delay conforme necessário

def calculate_angles(local_pos, target_pos, head_offset):
    delta_x = target_pos[0] - local_pos[0]
    delta_y = target_pos[1] - local_pos[1]
    delta_z = (target_pos[2] + head_offset) - local_pos[2]  # Aplica o offset na altura da cabeça
    # Calcular o Yaw (ângulo horizontal)
    yaw = math.degrees(math.atan2(delta_y, delta_x))
    # Calcular o Pitch (ângulo vertical)
    hypotenuse = math.sqrt(delta_x**2 + delta_y**2)
    pitch = math.degrees(math.atan2(-delta_z, hypotenuse))  # Negativo porque o eixo Y geralmente é invertido no jogo
    return yaw, pitch

# Função para verificar se o inimigo está dentro do círculo
def is_enemy_in_circle(center_x, center_y, radius, screen_head_pos):
    # Verifique se o inimigo está dentro do círculo
    distance = math.sqrt((screen_head_pos[0] - center_x)**2 + (screen_head_pos[1] - center_y)**2)
    return distance <= radius

def monitor_input():
    global aimbot_key, AimbotCloseDistanceSwitch, AimbotThread
    
    while AimbotThread:
        if is_mouse_pressed(aimbot_key) or is_key_pressed(aimbot_key):
            # Lendo a matriz de visualização uma vez
            Matrix = [
                [mem.read_float(client + int(offsets.dwViewMatrix + 0x0)),  mem.read_float(client + int(offsets.dwViewMatrix + 0x4)),  mem.read_float(client + int(offsets.dwViewMatrix + 0x8)),  mem.read_float(client + int(offsets.dwViewMatrix + 0xC))],
                [mem.read_float(client + int(offsets.dwViewMatrix + 0x10)), mem.read_float(client + int(offsets.dwViewMatrix + 0x14)), mem.read_float(client + int(offsets.dwViewMatrix + 0x18)), mem.read_float(client + int(offsets.dwViewMatrix + 0x1C))],
                [mem.read_float(client + int(offsets.dwViewMatrix + 0x20)), mem.read_float(client + int(offsets.dwViewMatrix + 0x24)), mem.read_float(client + int(offsets.dwViewMatrix + 0x28)), mem.read_float(client + int(offsets.dwViewMatrix + 0x2C))],
                [mem.read_float(client + int(offsets.dwViewMatrix + 0x30)), mem.read_float(client + int(offsets.dwViewMatrix + 0x34)), mem.read_float(client + int(offsets.dwViewMatrix + 0x38)), mem.read_float(client + int(offsets.dwViewMatrix + 0x3C))],
            ]

            window_size = [win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)]
            
            localplayer = mem.read_ulonglong(client + int(offsets.dwLocalPlayerPawn))
            
            localplayer_pos = [
                mem.read_float(localplayer + int(offsets.m_vOldOrigin)),
                mem.read_float(localplayer + int(offsets.m_vOldOrigin) + 4),
                mem.read_float(localplayer + int(offsets.m_vOldOrigin) + 8)
            ]

            distances = []
            for i in range(1, 64):
                entity = mem.read_ulonglong(client + int(offsets.dwEntityList))
                list_entity = mem.read_ulonglong(entity + ((8 * (i & 0x7FFF) >> 9) + 16))
                if not list_entity:
                    continue

                entity_controller = mem.read_ulonglong(list_entity + (120) * (i & 0x1FF))
                if not entity_controller:
                    continue

                entity_controller_pawn = mem.read_ulonglong(entity_controller + int(offsets.m_hPlayerPawn))
                if not entity_controller_pawn:
                    continue

                list_entity = mem.read_ulonglong(entity + (0x8 * ((entity_controller_pawn & 0x7FFF) >> 9) + 16))
                if not list_entity:
                    continue

                entity_pawn = mem.read_ulonglong(list_entity + (120) * (entity_controller_pawn & 0x1FF))
                if not entity_pawn:
                    continue
                
                if not mem.read_int(entity_pawn + int(offsets.m_iHealth)):
                    continue
                
                if entity_pawn:
                    if mem.read_int(localplayer + offsets.m_iTeamNum) != mem.read_int(entity_pawn + offsets.m_iTeamNum):
                        # Posição básica do jogador
                        player_pos_boots = [
                            mem.read_float(entity_pawn + int(offsets.m_vOldOrigin)),
                            mem.read_float(entity_pawn + int(offsets.m_vOldOrigin) + 4),
                            mem.read_float(entity_pawn + int(offsets.m_vOldOrigin) + 8)
                        ]
                        screen_boot_pos = funcs.world_to_screen(player_pos_boots, Matrix, window_size)

                        # Matriz de ossos
                        skeleton_instance_ptr = mem.read_ulonglong(entity_pawn + int(offsets.m_pGameSceneNode))
                        if not skeleton_instance_ptr:
                            continue

                        bone_array_ptr = mem.read_ulonglong(skeleton_instance_ptr + int(offsets.m_modelState + 0x80))
                        if not bone_array_ptr:
                            continue

                        
                        
                        

                        # if not (screen_boot_pos and screen_head_pos and screen_neck_pos and screen_body_pos):
                        #     continue
                        
                        # Calcular a posição do jogador inimigo (localplayer_pos e player_pos_boots já devem ser definidos)
                        distance_ = math.sqrt(
                            (localplayer_pos[0] - player_pos_boots[0])**2 +
                            (localplayer_pos[1] - player_pos_boots[1])**2 +
                            (localplayer_pos[2] - player_pos_boots[2])**2
                        )
                        

                        if Aimbot_focus == "Head":
                            # Posição do osso da cabeça
                            bone_position_head = [
                                mem.read_float(bone_array_ptr + 6 * 0x20),
                                mem.read_float(bone_array_ptr + 6 * 0x20 + 0x4),
                                mem.read_float(bone_array_ptr + 6 * 0x20 + 0x8)
                            ]
                            screen_head_pos = funcs.world_to_screen(bone_position_head, Matrix, window_size)
                            # Adicionar a distância e a posição do inimigo à lista
                            distances.append((distance_, bone_position_head))
                            
                            if not AimbotCloseDistanceSwitch:
                                if bone_position_head:
                                    # Calcular os ângulos de mira para o inimigo mais próximo
                                    target_yaw, target_pitch = calculate_angles(localplayer_pos, bone_position_head, head_offset=-65.0)
                                    # Obtém ângulos atuais
                                    current_pitch = mem.read_float(client + int(offsets.dwViewAngles))
                                    current_yaw = mem.read_float(client + int(offsets.dwViewAngles) + 0x4)
                                    # Verifica se o foco do Aimbot é na cabeça
                                    if AimbotFovActive:
                                        # Verificar se o inimigo está no campo de visão
                                        screen_head_pos = funcs.world_to_screen(bone_position_head, Matrix, window_size)
                                        if is_enemy_in_circle(int(window_size[0] // 2), int(window_size[1] // 2), AimbotFovRadio, screen_head_pos):
                                            smooth_aim(current_yaw, current_pitch, target_yaw, target_pitch)
                                    else:
                                        # Ajustar mira suavemente para outras partes do corpo
                                        smooth_aim(current_yaw, current_pitch, target_yaw, target_pitch)
                            
                            
                            
                            
                        if Aimbot_focus == "Neck":
                            # Posição do osso da cabeça
                            bone_position_neck = [
                                mem.read_float(bone_array_ptr + 5 * 0x20),
                                mem.read_float(bone_array_ptr + 5 * 0x20 + 0x4),
                                mem.read_float(bone_array_ptr + 5 * 0x20 + 0x8)
                            ]
                            screen_neck_pos = funcs.world_to_screen(bone_position_neck, Matrix, window_size)
                            # Adicionar a distância e a posição do inimigo à lista
                            distances.append((distance_, bone_position_neck))
                            
                            if not AimbotCloseDistanceSwitch:
                                if bone_position_neck:
                                    # Calcular os ângulos de mira para o inimigo mais próximo
                                    target_yaw, target_pitch = calculate_angles(localplayer_pos, bone_position_neck, head_offset=-65.0)
                                    # Obtém ângulos atuais
                                    current_pitch = mem.read_float(client + int(offsets.dwViewAngles))
                                    current_yaw = mem.read_float(client + int(offsets.dwViewAngles) + 0x4)
                                    # Verifica se o foco do Aimbot é na cabeça
                                    if AimbotFovActive:
                                        # Verificar se o inimigo está no campo de visão
                                        screen_head_pos = funcs.world_to_screen(bone_position_neck, Matrix, window_size)
                                        if is_enemy_in_circle(int(window_size[0] // 2), int(window_size[1] // 2), AimbotFovRadio, screen_neck_pos):
                                            smooth_aim(current_yaw, current_pitch, target_yaw, target_pitch)
                                    else:
                                        # Ajustar mira suavemente para outras partes do corpo
                                        smooth_aim(current_yaw, current_pitch, target_yaw, target_pitch)
                            
                        if Aimbot_focus == "Body":
                            # Posição do osso da cabeça
                            bone_position_body = [
                                mem.read_float(bone_array_ptr + 3 * 0x20),
                                mem.read_float(bone_array_ptr + 3 * 0x20 + 0x4),
                                mem.read_float(bone_array_ptr + 3 * 0x20 + 0x8)
                            ]
                            screen_body_pos = funcs.world_to_screen(bone_position_body, Matrix, window_size)
                            # Adicionar a distância e a posição do inimigo à lista
                            distances.append((distance_, bone_position_body))
                            
                            if not AimbotCloseDistanceSwitch:
                                if bone_position_body:
                                    # Calcular os ângulos de mira para o inimigo mais próximo
                                    target_yaw, target_pitch = calculate_angles(localplayer_pos, bone_position_body, head_offset=-65.0)
                                    # Obtém ângulos atuais
                                    current_pitch = mem.read_float(client + int(offsets.dwViewAngles))
                                    current_yaw = mem.read_float(client + int(offsets.dwViewAngles) + 0x4)
                                    # Verifica se o foco do Aimbot é na cabeça
                                    if AimbotFovActive:
                                        # Verificar se o inimigo está no campo de visão
                                        screen_head_pos = funcs.world_to_screen(bone_position_body, Matrix, window_size)
                                        if is_enemy_in_circle(int(window_size[0] // 2), int(window_size[1] // 2), AimbotFovRadio, screen_body_pos):
                                            smooth_aim(current_yaw, current_pitch, target_yaw, target_pitch)
                                    else:
                                        # Ajustar mira suavemente para outras partes do corpo
                                        smooth_aim(current_yaw, current_pitch, target_yaw, target_pitch)
                            

            # Após o loop, verificar qual jogador está mais próximo dentro do FOV
            if AimbotCloseDistanceSwitch:
                if distances:
                    # Filtrar inimigos dentro do FOV
                    enemies_in_fov = []
                    for distance, enemy_pos in distances:
                        # Calcular a posição na tela
                        screen_head_pos = funcs.world_to_screen(enemy_pos, Matrix, window_size)
                        
                        # Verificar se o inimigo está dentro do círculo do FOV
                        try:
                            if is_enemy_in_circle(int(window_size[0] // 2), int(window_size[1] // 2), AimbotFovRadio, screen_head_pos):
                                enemies_in_fov.append((distance, enemy_pos))
                        except:
                            pass
                    # Verificar se há inimigos no FOV
                    if enemies_in_fov:
                        # Ordenar pelos inimigos mais próximos
                        enemies_in_fov.sort(key=lambda x: x[0])  # Ordena pela distância (primeiro elemento da tupla)
                        closest_distance, closest_enemy_pos = enemies_in_fov[0]  # Pegue a menor distância e a posição associada

                        # Calibração: ajuste de altura da cabeça
                        head_offset = -65.0  # Ajuste conforme necessário

                        # Calcular os ângulos de mira para o inimigo mais próximo
                        target_yaw, target_pitch = calculate_angles(localplayer_pos, closest_enemy_pos, head_offset=head_offset)

                        # Obtém ângulos atuais
                        current_pitch = mem.read_float(client + int(offsets.dwViewAngles))
                        current_yaw = mem.read_float(client + int(offsets.dwViewAngles) + 0x4)

                        # Ajustar a mira suavemente
                        smooth_aim(current_yaw, current_pitch, target_yaw, target_pitch)

        time.sleep(Aimbot_smooth)

############################################# AIMBOT #############################################












def glow_enemy_close():
    global closest_enemy_glow_color
    window_size = [win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)]

    localplayer = mem.read_ulonglong(client + int(offsets.dwLocalPlayerPawn))
    localplayer_pos = [
        mem.read_float(localplayer + int(offsets.m_vOldOrigin)),
        mem.read_float(localplayer + int(offsets.m_vOldOrigin) + 4),
        mem.read_float(localplayer + int(offsets.m_vOldOrigin) + 8)
    ]
    distances = []
    for i in range(2, 64):
        # Lendo a matriz de visualização uma vez
        Matrix = [
            [mem.read_float(client + int(offsets.dwViewMatrix + 0x0)),  mem.read_float(client + int(offsets.dwViewMatrix + 0x4)),  mem.read_float(client + int(offsets.dwViewMatrix + 0x8)),  mem.read_float(client + int(offsets.dwViewMatrix + 0xC))],
            [mem.read_float(client + int(offsets.dwViewMatrix + 0x10)), mem.read_float(client + int(offsets.dwViewMatrix + 0x14)), mem.read_float(client + int(offsets.dwViewMatrix + 0x18)), mem.read_float(client + int(offsets.dwViewMatrix + 0x1C))],
            [mem.read_float(client + int(offsets.dwViewMatrix + 0x20)), mem.read_float(client + int(offsets.dwViewMatrix + 0x24)), mem.read_float(client + int(offsets.dwViewMatrix + 0x28)), mem.read_float(client + int(offsets.dwViewMatrix + 0x2C))],
            [mem.read_float(client + int(offsets.dwViewMatrix + 0x30)), mem.read_float(client + int(offsets.dwViewMatrix + 0x34)), mem.read_float(client + int(offsets.dwViewMatrix + 0x38)), mem.read_float(client + int(offsets.dwViewMatrix + 0x3C))],
        ]

        entity = mem.read_ulonglong(client + int(offsets.dwEntityList))
        list_entity = mem.read_ulonglong(entity + ((8 * (i & 0x7FFF) >> 9) + 16))
        if not list_entity:
            continue

        entity_controller = mem.read_ulonglong(list_entity + (120) * (i & 0x1FF))
        if not entity_controller:
            continue

        entity_controller_pawn = mem.read_ulonglong(entity_controller + int(offsets.m_hPlayerPawn))
        if not entity_controller_pawn:
            continue

        list_entity = mem.read_ulonglong(entity + (0x8 * ((entity_controller_pawn & 0x7FFF) >> 9) + 16))
        if not list_entity:
            continue

        entity_pawn = mem.read_ulonglong(list_entity + (120) * (entity_controller_pawn & 0x1FF))
        if not entity_pawn:
            continue
        
        if entity_pawn:
            if mem.read_int(localplayer + offsets.m_iTeamNum) != mem.read_int(entity_pawn + offsets.m_iTeamNum):
                # C_CSPlayerPawn m_entitySpottedState
                if mem.read_bool(entity_pawn + (0x23D0 + offsets.m_bSpottedByMask)):
                    if mem.read_int(entity_pawn + int(offsets.m_iHealth)) >= 1 and mem.read_int(entity_pawn + int(offsets.m_iHealth)) <= 100:
                        # Posição básica do jogador
                        player_pos_boots = [
                            mem.read_float(entity_pawn + int(offsets.m_vOldOrigin)),
                            mem.read_float(entity_pawn + int(offsets.m_vOldOrigin) + 4),
                            mem.read_float(entity_pawn + int(offsets.m_vOldOrigin) + 8)
                        ]
                        screen_boot_pos = funcs.world_to_screen(player_pos_boots, Matrix, window_size)

                        # Matriz de ossos
                        skeleton_instance_ptr = mem.read_ulonglong(entity_pawn + int(offsets.m_pGameSceneNode))
                        if not skeleton_instance_ptr:
                            continue

                        bone_array_ptr = mem.read_ulonglong(skeleton_instance_ptr + int(offsets.m_modelState + 0x80))
                        if not bone_array_ptr:
                            continue

                        # Posição do osso da cabeça
                        bone_position_head = [
                            mem.read_float(bone_array_ptr + 6 * 0x20),
                            mem.read_float(bone_array_ptr + 6 * 0x20 + 0x4),
                            mem.read_float(bone_array_ptr + 6 * 0x20 + 0x8)
                        ]
                        screen_head_pos = funcs.world_to_screen(bone_position_head, Matrix, window_size)

                        if not (screen_boot_pos and screen_head_pos):
                            continue
                        
                        # Calcular a posição do jogador inimigo (localplayer_pos e player_pos_boots já devem ser definidos)
                        distance_ = math.sqrt(
                            (localplayer_pos[0] - player_pos_boots[0])**2 +
                            (localplayer_pos[1] - player_pos_boots[1])**2 +
                            (localplayer_pos[2] - player_pos_boots[2])**2
                        )

                        # Adicionar a distância e a posição do inimigo à lista
                        distances.append((distance_, entity_pawn))
    # Após o loop, verificar qual jogador está mais próximo
    if distances:
        # Ordenar a lista de distâncias para obter o inimigo mais próximo
        distances.sort(key=lambda x: x[0])  # Ordena pela distância (primeiro elemento da tupla)
        closest_distance, closest_enemy_pawn = distances[0]  # Pegue a menor distância e o entity_pawn associado
        
        # Ativar o glow no inimigo mais próximo
        if closest_enemy_pawn:
            # Agora você pode usar glow_color_with_alpha no GlowColorOverride
            GlowColorOverride = closest_enemy_pawn  + int(offsets.m_Glow) + int(offsets.m_glowColorOverride)
            GlowFunction = closest_enemy_pawn  + int(offsets.m_Glow) + int(offsets.m_bGlowing)
            # Escrever os valores na memória
            mem.write_int(GlowColorOverride, closest_enemy_glow_color)  # Aplica a cor com alpha
            mem.write_int(GlowFunction, 1)  # Ativa o efeito de brilho (1 para ativar)







def MemmoActiveAimbot(Type_):
    global AimbotCloseDistanceSwitch, AimbotThread
    if Type_ == "Aimbot":
        AimbotThread = True
        thread_01 = threading.Thread(target=monitor_input, daemon=True)
        thread_01.start()
    if Type_ == "AimbotOff":
        try:
            thread_01.join()
            AimbotThread = False
        except:
            pass
    
    if Type_ == "ClosestEnemyGlowOn":
        thread_02 = threading.Thread(target=glow_enemy_close, daemon=True)
        thread_02.start()
    
    if Type_ == "CloseDistanceOn":
        AimbotCloseDistanceSwitch = True
    if Type_ == "CloseDistanceOff":
        AimbotCloseDistanceSwitch = False




















def MemmoActive(Type_):
    global glow_color_hex, entity_pawn, player_fov_value
    coords_list = []  # Lista para armazenar as coordenadas de todas as entidades

    localplayer = mem.read_ulonglong(client + int(offsets.dwLocalPlayerPawn))
    # Lendo a matriz de visualização uma vez
    Matrix = [
        [mem.read_float(client + int(offsets.dwViewMatrix + 0x0)),  mem.read_float(client + int(offsets.dwViewMatrix + 0x4)),  mem.read_float(client + int(offsets.dwViewMatrix + 0x8)),  mem.read_float(client + int(offsets.dwViewMatrix + 0xC))],
        [mem.read_float(client + int(offsets.dwViewMatrix + 0x10)), mem.read_float(client + int(offsets.dwViewMatrix + 0x14)), mem.read_float(client + int(offsets.dwViewMatrix + 0x18)), mem.read_float(client + int(offsets.dwViewMatrix + 0x1C))],
        [mem.read_float(client + int(offsets.dwViewMatrix + 0x20)), mem.read_float(client + int(offsets.dwViewMatrix + 0x24)), mem.read_float(client + int(offsets.dwViewMatrix + 0x28)), mem.read_float(client + int(offsets.dwViewMatrix + 0x2C))],
        [mem.read_float(client + int(offsets.dwViewMatrix + 0x30)), mem.read_float(client + int(offsets.dwViewMatrix + 0x34)), mem.read_float(client + int(offsets.dwViewMatrix + 0x38)), mem.read_float(client + int(offsets.dwViewMatrix + 0x3C))],
    ]

    window_size = [win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)]

    try:
        for i in range(1, 64):
            entity = mem.read_ulonglong(client + int(offsets.dwEntityList))
            list_entity = mem.read_ulonglong(entity + ((8 * (i & 0x7FFF) >> 9) + 16))
            if not list_entity:
                continue

            entity_controller = mem.read_ulonglong(list_entity + (120) * (i & 0x1FF))
            if not entity_controller:
                continue

            entity_controller_pawn = mem.read_ulonglong(entity_controller + int(offsets.m_hPlayerPawn))
            if not entity_controller_pawn:
                continue

            list_entity = mem.read_ulonglong(entity + (0x8 * ((entity_controller_pawn & 0x7FFF) >> 9) + 16))
            if not list_entity:
                continue

            entity_pawn = mem.read_ulonglong(list_entity + (120) * (entity_controller_pawn & 0x1FF))
            if not entity_pawn:
                continue
            
            if mem.read_int(localplayer + offsets.m_iTeamNum) != mem.read_int(entity_pawn + offsets.m_iTeamNum):
                if mem.read_int(entity_pawn + int(offsets.m_iHealth)) >= 1 and mem.read_int(entity_pawn + int(offsets.m_iHealth)) <= 100:
                    # Posição básica do jogador
                    player_pos_boots = [
                        mem.read_float(entity_pawn + int(offsets.m_vOldOrigin)),
                        mem.read_float(entity_pawn + int(offsets.m_vOldOrigin) + 4),
                        mem.read_float(entity_pawn + int(offsets.m_vOldOrigin) + 8)
                    ]
                    screen_boot_pos = funcs.world_to_screen(player_pos_boots, Matrix, window_size)

                    # Matriz de ossos
                    skeleton_instance_ptr = mem.read_ulonglong(entity_pawn + int(offsets.m_pGameSceneNode))
                    if not skeleton_instance_ptr:
                        continue

                    bone_array_ptr = mem.read_ulonglong(skeleton_instance_ptr + int(offsets.m_modelState + 0x80))
                    if not bone_array_ptr:
                        continue

                    # Posição do osso da cabeça
                    bone_position_head = [
                        mem.read_float(bone_array_ptr + 6 * 0x20),
                        mem.read_float(bone_array_ptr + 6 * 0x20 + 0x4),
                        mem.read_float(bone_array_ptr + 6 * 0x20 + 0x8)
                    ]
                    screen_head_pos = funcs.world_to_screen(bone_position_head, Matrix, window_size)

                    if not (screen_boot_pos and screen_head_pos):
                        continue

                    # Adiciona as coordenadas conforme o tipo
                    if Type_ == "Box":
                        coords_list.append((screen_boot_pos, screen_head_pos))

                    elif Type_ == "Name":
                        entity_name_address = mem.read_ulonglong(entity_controller + int(offsets.m_sSanitizedPlayerName))
                        entity_name = mem.read_string(entity_name_address)
                        coords_list.append((screen_head_pos[0], screen_head_pos[1], entity_name))

                    elif Type_ == "Health":
                        health_entity = mem.read_int(entity_pawn + int(offsets.m_iHealth))
                        health_armor = mem.read_int(entity_pawn + int(offsets.m_ArmorValue))
                        coords_list.append((screen_head_pos, screen_boot_pos, health_entity, health_armor))

                    elif Type_ == "Armor":
                        health_entity = mem.read_int(entity_pawn + int(offsets.m_iHealth))
                        health_armor = mem.read_int(entity_pawn + int(offsets.m_ArmorValue))
                        coords_list.append((screen_head_pos, screen_boot_pos, health_entity, health_armor))

                    elif Type_ == "Skeleton":
                        bone_connections = [
                            [6, 5], [5, 4], [4, 0], [4, 8], [8, 9], [9, 11],
                            [4, 13], [13, 14], [14, 16], [4, 2], [0, 22], [0, 25],
                            [22, 23], [23, 24], [25, 26], [26, 27]
                        ]
                        bone_positions = []
                        for bone_connection in bone_connections:
                            for bone_index in bone_connection:
                                x = mem.read_float(bone_array_ptr + bone_index * 0x20)
                                y = mem.read_float(bone_array_ptr + bone_index * 0x20 + 0x4)
                                z = mem.read_float(bone_array_ptr + bone_index * 0x20 + 0x8)
                                bone_positions.append((x, y, z))
                        for i in range(0, len(bone_positions), 2):
                            bone_1 = funcs.world_to_screen(bone_positions[i], Matrix, window_size)
                            bone_2 = funcs.world_to_screen(bone_positions[i + 1], Matrix, window_size)
                            if bone_1 and bone_2:
                                coords_list.append((bone_1, bone_2))
                    
                    if Type_ == "Glow":
                        # Agora você pode usar glow_color_with_alpha no GlowColorOverride
                        GlowColorOverride = entity_pawn + int(offsets.m_Glow) + int(offsets.m_glowColorOverride)
                        GlowFunction = entity_pawn + int(offsets.m_Glow) + int(offsets.m_bGlowing)
                        # Escrever os valores na memória
                        mem.write_int(GlowColorOverride, glow_color_hex)  # Aplica a cor com alpha
                        mem.write_int(GlowFunction, 1)  # Ativa o efeito de brilho (1 para ativar)
                        
                    if Type_ == "Line":
                        coords_list.append((screen_boot_pos, window_size))
                        
                    if Type_ == "Distance":
                        localplayer = mem.read_ulonglong(client + int(offsets.dwLocalPlayerPawn))
                        localplayer_pos = [
                            mem.read_float(localplayer + int(offsets.m_vOldOrigin)),
                            mem.read_float(localplayer + int(offsets.m_vOldOrigin) + 4),
                            mem.read_float(localplayer + int(offsets.m_vOldOrigin) + 8)
                        ]
                        
                        # Calculando a distância entre o jogador e o inimigo
                        distance = math.sqrt(
                            (localplayer_pos[0] - player_pos_boots[0])**2 +
                            (localplayer_pos[1] - player_pos_boots[1])**2 +
                            (localplayer_pos[2] - player_pos_boots[2])**2
                        )
                        coords_list.append((screen_boot_pos, distance))
                        
                    if Type_ == "FireOn":
                        mem.write_float(entity_pawn + int(offsets.m_fMolotovDamageTime), 10000.0) # Fogo On
                    elif Type_ == "FireOff":
                        mem.write_float(entity_pawn + int(offsets.m_fMolotovDamageTime), 1.0) # Fogo Off
                        
                    if Type_ == "NoFlash":
                        localplayer = mem.read_ulonglong(client + int(offsets.dwLocalPlayerPawn))
                        mem.write_float(localplayer + int(offsets.m_flFlashBangTime), 0.0) # Flashbang Off
                        
                    if Type_ == "FovChangerOn":
                        localplayer = mem.read_ulonglong(client + int(offsets.dwLocalPlayerPawn))
                        camera_services = mem.read_ulonglong(localplayer + int(offsets.m_pCameraServices))
                        mem.write_int(camera_services + int(offsets.m_iFOV, player_fov_value))
                    elif Type_ == "FovChangerOff":
                        pass
                    #     localplayer = mem.read_ulonglong(client + int(offsets.dwLocalPlayerPawn)
                    #     camera_services = mem.read_ulonglong(localplayer + int(offsets.m_pCameraServices)
                    #     mem.write_int(camera_services + int(offsets.m_iFOV, 0)

                    if Type_ == "ThirdPersonOn":
                        localplayer = mem.read_ulonglong(client + int(offsets.dwLocalPlayerPawn))
                        mem.write_int(localplayer + int(offsets.m_thirdPersonHeading), 1)
                    if Type_ == "ThirdPersonOff":
                        pass
                    #     localplayer = mem.read_ulonglong(client + int(offsets.dwLocalPlayerPawn))
                    #     mem.write_int(localplayer + int(offsets.m_thirdPersonHeading), 0)
    except:
        pass
                    
    return coords_list  # Retorna todas as coordenadas