import pygame
import sys
import random
import datetime
import json
from pygame import mixer

# Inicializar pygame
pygame.init()
mixer.init()

# Configuración de la pantalla
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sistema de Citas Médicas")

# Colores
GRIS = (200, 200, 200)
GRIS_OSCURO = (100, 100, 100)
AZUL = (0, 120, 215)
AZUL_OSCURO = (0, 80, 160)
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
ROJO = (255, 0, 0)
VERDE = (0, 255, 0)

# Fuentes
font_large = pygame.font.SysFont('Arial', 32)
font_medium = pygame.font.SysFont('Arial', 24)
font_small = pygame.font.SysFont('Arial', 16)

# Variables globales
current_screen = "login"
user_id = ""
user_type = ""
admin_code = ""
selected_date = None
selected_time = None
citas = {}
input_text = ""
active_input = False
verification_code = ""
show_verification = False
admin_password = "Nomedis1"  # Contraseña oculta para admin
pending_action = None  # Para acciones que requieren verificación
action_data = {}  # Datos para la acción pendiente

# Cargar datos de citas desde archivo
try:
    with open('citas.json', 'r') as f:
        citas = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    citas = {}

# Sonidos
try:
    click_sound = mixer.Sound('click.wav')
    error_sound = mixer.Sound('error.wav')
    success_sound = mixer.Sound('success.wav')
except:
    click_sound = mixer.Sound(buffer=bytearray(0))
    error_sound = mixer.Sound(buffer=bytearray(0))
    success_sound = mixer.Sound(buffer=bytearray(0))

def generate_admin_code():
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    numbers = "0123456789"
    code = []
    for i in range(6):
        if i % 2 == 0:
            code.append(random.choice(letters))
        else:
            code.append(random.choice(numbers))
    return ''.join(code)

def draw_button(text, x, y, width, height, color, hover_color, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    
    if x < mouse[0] < x + width and y < mouse[1] < y + height:
        pygame.draw.rect(screen, hover_color, (x, y, width, height))
        if click[0] == 1 and action is not None:
            click_sound.play()
            pygame.time.delay(200)
            return action
    else:
        pygame.draw.rect(screen, color, (x, y, width, height))
    
    text_surf = font_medium.render(text, True, BLANCO)
    text_rect = text_surf.get_rect(center=(x + width/2, y + height/2))
    screen.blit(text_surf, text_rect)
    return None

def draw_input_box(x, y, width, height, color, active_color, text, active):
    if active:
        pygame.draw.rect(screen, active_color, (x, y, width, height), 2)
    else:
        pygame.draw.rect(screen, color, (x, y, width, height), 2)
    
    text_surf = font_medium.render(text, True, NEGRO)
    screen.blit(text_surf, (x + 10, y + 10))

def is_valid_id(id_str):
    return id_str.isdigit() and (len(id_str) == 7 or len(id_str) == 8)  # Acepta 7 u 8 dígitos

def get_available_dates():
    today = datetime.date.today()
    max_date = today + datetime.timedelta(days=730)  # 2 años
    available_dates = []
    
    current_date = today
    while current_date <= max_date:
        if current_date.weekday() < 5:  # Lunes a viernes
            date_str = current_date.strftime("%Y-%m-%d")
            if date_str not in citas or len(citas[date_str]) < 8:
                available_dates.append(current_date)
        current_date += datetime.timedelta(days=1)
    
    return available_dates

def get_available_times(date):
    date_str = date.strftime("%Y-%m-%d")
    existing_times = citas.get(date_str, {}).keys()
    all_times = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00"]
    return [time for time in all_times if time not in existing_times]

def save_citas():
    with open('citas.json', 'w') as f:
        json.dump(citas, f)

def login_screen():
    global current_screen, user_id, user_type, active_input, input_text
    
    screen.fill(GRIS)
    
    title = font_large.render("Sistema de Citas Médicas", True, AZUL_OSCURO)
    screen.blit(title, (WIDTH/2 - title.get_width()/2, 50))
    
    instructions = font_medium.render("Ingrese su ID (7 u 8 dígitos):", True, NEGRO)
    screen.blit(instructions, (WIDTH/2 - instructions.get_width()/2, 150))
    
    active = active_input and current_screen == "login"
    draw_input_box(WIDTH/2 - 150, 200, 300, 50, GRIS_OSCURO, AZUL, input_text, active)
    
    action = draw_button("Ingresar", WIDTH/2 - 100, 280, 200, 50, AZUL, AZUL_OSCURO, "ingresar")
    if action == "ingresar":
        if input_text == admin_password:
            user_type = "admin"
            current_screen = "admin_menu"
            input_text = ""
        elif is_valid_id(input_text):
            user_id = input_text
            user_type = "user"
            current_screen = "user_menu"
            input_text = ""
        else:
            error_sound.play()
    
    if current_screen == "login" and len(input_text) > 0 and not is_valid_id(input_text) and input_text != admin_password:
        error_msg = font_small.render("ID inválido. Debe ser de 7 u 8 dígitos.", True, ROJO)
        screen.blit(error_msg, (WIDTH/2 - error_msg.get_width()/2, 350))

def admin_verification_screen():
    global current_screen, input_text, active_input, verification_code, pending_action, action_data
    
    screen.fill(GRIS)
    
    title = font_large.render("Verificación Requerida", True, AZUL_OSCURO)
    screen.blit(title, (WIDTH/2 - title.get_width()/2, 50))
    
    code_text = font_medium.render(f"Código de verificación: {admin_code}", True, NEGRO)
    screen.blit(code_text, (WIDTH/2 - code_text.get_width()/2, 150))
    
    instructions = font_medium.render("Ingrese el código para confirmar:", True, NEGRO)
    screen.blit(instructions, (WIDTH/2 - instructions.get_width()/2, 200))
    
    active = active_input and current_screen == "admin_verification"
    draw_input_box(WIDTH/2 - 150, 250, 300, 50, GRIS_OSCURO, AZUL, input_text, active)
    
    action = draw_button("Confirmar", WIDTH/2 - 100, 330, 200, 50, AZUL, AZUL_OSCURO, "confirmar")
    if action == "confirmar":
        if input_text == admin_code:
            verification_code = input_text
            execute_pending_action()
            input_text = ""
        else:
            error_sound.play()
    
    action = draw_button("Cancelar", WIDTH/2 - 100, 400, 200, 50, GRIS_OSCURO, AZUL_OSCURO, "cancelar")
    if action == "cancelar":
        current_screen = "admin_menu"
        pending_action = None
        input_text = ""

def execute_pending_action():
    global current_screen, pending_action, action_data, admin_code
    
    if pending_action == "mark_completed":
        date_str = action_data["date_str"]
        time_str = action_data["time_str"]
        citas[date_str][time_str]["completed"] = True
        save_citas()
        success_sound.play()
        current_screen = "admin_menu"
    
    elif pending_action == "admin_cancel":
        date_str = action_data["date_str"]
        time_str = action_data["time_str"]
        del citas[date_str][time_str]
        if not citas[date_str]:
            del citas[date_str]
        save_citas()
        success_sound.play()
        current_screen = "admin_menu"
    
    pending_action = None
    action_data = {}
    admin_code = generate_admin_code()

def user_menu_screen():
    global current_screen
    
    screen.fill(GRIS)
    
    title = font_large.render(f"Bienvenido Usuario {user_id}", True, AZUL_OSCURO)
    screen.blit(title, (WIDTH/2 - title.get_width()/2, 50))
    
    y_pos = 150
    options = [
        ("Agendar Cita", "schedule_appointment"),
        ("Cancelar Cita", "cancel_appointment"),
        ("Ver Mis Citas", "view_appointments"),
        ("Cerrar Sesión", "logout")
    ]
    
    for text, action in options:
        btn_action = draw_button(text, WIDTH/2 - 150, y_pos, 300, 50, AZUL, AZUL_OSCURO, action)
        if btn_action == action:
            current_screen = action
        y_pos += 70

def admin_menu_screen():
    global current_screen
    
    screen.fill(GRIS)
    
    title = font_large.render("Panel de Administrador", True, AZUL_OSCURO)
    screen.blit(title, (WIDTH/2 - title.get_width()/2, 50))
    
    y_pos = 150
    options = [
        ("Ver Todas las Citas", "view_all_appointments"),
        ("Cancelar Cita", "admin_cancel_appointment"),
        ("Marcar Cita Realizada", "mark_completed"),
        ("Cerrar Sesión", "logout")
    ]
    
    for text, action in options:
        btn_action = draw_button(text, WIDTH/2 - 150, y_pos, 300, 50, AZUL, AZUL_OSCURO, action)
        if btn_action == action:
            current_screen = action
        y_pos += 70

def schedule_appointment_screen():
    global current_screen, selected_date, selected_time
    
    screen.fill(GRIS)
    
    title = font_large.render("Agendar Nueva Cita", True, AZUL_OSCURO)
    screen.blit(title, (WIDTH/2 - title.get_width()/2, 30))
    
    available_dates = get_available_dates()
    
    date_text = font_medium.render("Seleccione una fecha disponible:", True, NEGRO)
    screen.blit(date_text, (50, 100))
    
    y_pos = 150
    for i, date in enumerate(available_dates[:5]):
        date_str = date.strftime("%d/%m/%Y")
        btn_action = draw_button(date_str, 50, y_pos, 200, 40, AZUL, AZUL_OSCURO, f"select_date_{i}")
        if btn_action == f"select_date_{i}":
            selected_date = date
            selected_time = None
        y_pos += 50
    
    if selected_date:
        date_display = font_medium.render(f"Fecha seleccionada: {selected_date.strftime('%d/%m/%Y')}", True, NEGRO)
        screen.blit(date_display, (300, 100))
        
        available_times = get_available_times(selected_date)
        
        if available_times:
            time_text = font_medium.render("Seleccione una hora disponible:", True, NEGRO)
            screen.blit(time_text, (300, 150))
            
            y_pos = 200
            for time in available_times:
                btn_action = draw_button(time, 300, y_pos, 100, 40, AZUL, AZUL_OSCURO, f"select_time_{time}")
                if btn_action == f"select_time_{time}":
                    selected_time = time
                y_pos += 50
        else:
            no_times = font_medium.render("No hay horas disponibles para este día.", True, ROJO)
            screen.blit(no_times, (300, 150))
    
    if selected_date and selected_time:
        confirm_text = font_medium.render(f"Confirmar cita para {selected_date.strftime('%d/%m/%Y')} a las {selected_time}", True, NEGRO)
        screen.blit(confirm_text, (50, 400))
        
        btn_action = draw_button("Confirmar Cita", 50, 450, 200, 50, VERDE, (0, 200, 0), "confirm_appointment")
        if btn_action == "confirm_appointment":
            date_str = selected_date.strftime("%Y-%m-%d")
            if date_str not in citas:
                citas[date_str] = {}
            
            citas[date_str][selected_time] = {
                "user_id": user_id,
                "completed": False
            }
            save_citas()
            success_sound.play()
            current_screen = "user_menu"
    
    btn_action = draw_button("Regresar", WIDTH - 250, 450, 200, 50, GRIS_OSCURO, AZUL_OSCURO, "regresar")
    if btn_action == "regresar":
        current_screen = "user_menu"

def cancel_appointment_screen():
    global current_screen
    
    screen.fill(GRIS)
    
    title = font_large.render("Cancelar Cita", True, AZUL_OSCURO)
    screen.blit(title, (WIDTH/2 - title.get_width()/2, 30))
    
    user_appointments = []
    for date_str, times in citas.items():
        for time, details in times.items():
            if details["user_id"] == user_id:
                user_appointments.append((date_str, time, details["completed"]))
    
    if not user_appointments:
        no_appointments = font_medium.render("No tienes citas agendadas.", True, NEGRO)
        screen.blit(no_appointments, (WIDTH/2 - no_appointments.get_width()/2, 150))
    else:
        appointments_text = font_medium.render("Tus citas agendadas:", True, NEGRO)
        screen.blit(appointments_text, (50, 100))
        
        y_pos = 150
        for i, (date_str, time, completed) in enumerate(user_appointments):
            date = datetime.datetime.strptime(date_str, "%Y-%m-%d").strftime("%d/%m/%Y")
            status = "Realizada" if completed else "Pendiente"
            appointment_text = font_small.render(f"{date} a las {time} - {status}", True, NEGRO)
            screen.blit(appointment_text, (50, y_pos))
            
            if not completed:  # Solo permitir cancelar citas pendientes
                btn_action = draw_button("Cancelar", 400, y_pos, 100, 30, ROJO, (200, 0, 0), f"cancel_{i}")
                if btn_action == f"cancel_{i}":
                    del citas[date_str][time]
                    if not citas[date_str]:
                        del citas[date_str]
                    save_citas()
                    success_sound.play()
                    current_screen = "cancel_appointment"  # Recargar pantalla
            
            y_pos += 40
    
    btn_action = draw_button("Regresar", WIDTH - 250, 450, 200, 50, GRIS_OSCURO, AZUL_OSCURO, "regresar")
    if btn_action == "regresar":
        current_screen = "user_menu"

def view_appointments_screen():
    global current_screen
    
    screen.fill(GRIS)
    
    title = font_large.render("Mis Citas", True, AZUL_OSCURO)
    screen.blit(title, (WIDTH/2 - title.get_width()/2, 30))
    
    user_appointments = []
    for date_str, times in citas.items():
        for time, details in times.items():
            if details["user_id"] == user_id:
                user_appointments.append((date_str, time, details["completed"]))
    
    if not user_appointments:
        no_appointments = font_medium.render("No tienes citas agendadas.", True, NEGRO)
        screen.blit(no_appointments, (WIDTH/2 - no_appointments.get_width()/2, 150))
    else:
        appointments_text = font_medium.render("Tus citas agendadas:", True, NEGRO)
        screen.blit(appointments_text, (50, 100))
        
        y_pos = 150
        for date_str, time, completed in user_appointments:
            date = datetime.datetime.strptime(date_str, "%Y-%m-%d").strftime("%d/%m/%Y")
            status = "Realizada" if completed else "Pendiente"
            color = VERDE if completed else NEGRO
            appointment_text = font_small.render(f"{date} a las {time} - {status}", True, color)
            screen.blit(appointment_text, (50, y_pos))
            y_pos += 40
    
    btn_action = draw_button("Regresar", WIDTH - 250, 450, 200, 50, GRIS_OSCURO, AZUL_OSCURO, "regresar")
    if btn_action == "regresar":
        current_screen = "user_menu"

def view_all_appointments_screen():
    global current_screen
    
    screen.fill(GRIS)
    
    title = font_large.render("Todas las Citas", True, AZUL_OSCURO)
    screen.blit(title, (WIDTH/2 - title.get_width()/2, 30))
    
    if not citas:
        no_appointments = font_medium.render("No hay citas agendadas en el sistema.", True, NEGRO)
        screen.blit(no_appointments, (WIDTH/2 - no_appointments.get_width()/2, 150))
    else:
        y_pos = 100
        for date_str, times in citas.items():
            date = datetime.datetime.strptime(date_str, "%Y-%m-%d").strftime("%d/%m/%Y")
            date_text = font_medium.render(f"Fecha: {date}", True, AZUL_OSCURO)
            screen.blit(date_text, (50, y_pos))
            y_pos += 40
            
            for time, details in times.items():
                status = "Realizada" if details["completed"] else "Pendiente"
                color = VERDE if details["completed"] else NEGRO
                appointment_text = font_small.render(f"Hora: {time} - ID Usuario: {details['user_id']} - {status}", True, color)
                screen.blit(appointment_text, (70, y_pos))
                y_pos += 30
            y_pos += 20
    
    btn_action = draw_button("Regresar", WIDTH - 250, 450, 200, 50, GRIS_OSCURO, AZUL_OSCURO, "regresar")
    if btn_action == "regresar":
        current_screen = "admin_menu"

def admin_cancel_appointment_screen():
    global current_screen, input_text, active_input, pending_action, action_data, admin_code
    
    screen.fill(GRIS)
    
    title = font_large.render("Cancelar Cita (Admin)", True, AZUL_OSCURO)
    screen.blit(title, (WIDTH/2 - title.get_width()/2, 30))
    
    instructions = font_medium.render("Ingrese fecha (DD/MM/AAAA) y hora (HH:MM):", True, NEGRO)
    screen.blit(instructions, (50, 100))
    
    date_active = active_input and current_screen == "admin_cancel_appointment" and "date" in input_text
    draw_input_box(50, 150, 200, 40, GRIS_OSCURO, AZUL, input_text.replace("date:", ""), date_active)
    
    time_active = active_input and current_screen == "admin_cancel_appointment" and "time" in input_text
    draw_input_box(300, 150, 100, 40, GRIS_OSCURO, AZUL, input_text.replace("time:", ""), time_active)
    
    btn_action = draw_button("Buscar Cita", 450, 150, 150, 40, AZUL, AZUL_OSCURO, "buscar_cita")
    if btn_action == "buscar_cita":
        try:
            date_parts = input_text.replace("date:", "").split("/")
            date_obj = datetime.datetime.strptime(f"{date_parts[0]}/{date_parts[1]}/{date_parts[2]}", "%d/%m/%Y")
            date_str = date_obj.strftime("%Y-%m-%d")
            time_str = input_text.replace("time:", "")
            
            if date_str in citas and time_str in citas[date_str]:
                details = citas[date_str][time_str]
                detail_text = font_medium.render(f"ID Usuario: {details['user_id']} - {'Realizada' if details['completed'] else 'Pendiente'}", True, NEGRO)
                screen.blit(detail_text, (50, 220))
                
                btn_action = draw_button("Cancelar Cita", 50, 270, 200, 40, ROJO, (200, 0, 0), "cancelar_cita_admin")
                if btn_action == "cancelar_cita_admin":
                    pending_action = "admin_cancel"
                    action_data = {
                        "date_str": date_str,
                        "time_str": time_str
                    }
                    admin_code = generate_admin_code()
                    current_screen = "admin_verification"
                    input_text = ""
        except:
            error_msg = font_medium.render("Formato inválido.", True, ROJO)
            screen.blit(error_msg, (50, 220))
            error_sound.play()
    
    btn_action = draw_button("Regresar", WIDTH - 250, 450, 200, 50, GRIS_OSCURO, AZUL_OSCURO, "regresar")
    if btn_action == "regresar":
        current_screen = "admin_menu"

def mark_completed_screen():
    global current_screen, input_text, active_input, pending_action, action_data, admin_code
    
    screen.fill(GRIS)
    
    title = font_large.render("Marcar Cita como Realizada", True, AZUL_OSCURO)
    screen.blit(title, (WIDTH/2 - title.get_width()/2, 30))
    
    instructions = font_medium.render("Ingrese fecha (DD/MM/AAAA) y hora (HH:MM):", True, NEGRO)
    screen.blit(instructions, (50, 100))
    
    date_active = active_input and current_screen == "mark_completed" and "date" in input_text
    draw_input_box(50, 150, 200, 40, GRIS_OSCURO, AZUL, input_text.replace("date:", ""), date_active)
    
    time_active = active_input and current_screen == "mark_completed" and "time" in input_text
    draw_input_box(300, 150, 100, 40, GRIS_OSCURO, AZUL, input_text.replace("time:", ""), time_active)
    
    btn_action = draw_button("Buscar Cita", 450, 150, 150, 40, AZUL, AZUL_OSCURO, "buscar_cita")
    if btn_action == "buscar_cita":
        try:
            date_parts = input_text.replace("date:", "").split("/")
            date_obj = datetime.datetime.strptime(f"{date_parts[0]}/{date_parts[1]}/{date_parts[2]}", "%d/%m/%Y")
            date_str = date_obj.strftime("%Y-%m-%d")
            time_str = input_text.replace("time:", "")
            
            if date_str in citas and time_str in citas[date_str]:
                details = citas[date_str][time_str]
                detail_text = font_medium.render(f"ID Usuario: {details['user_id']} - {'Realizada' if details['completed'] else 'Pendiente'}", True, NEGRO)
                screen.blit(detail_text, (50, 220))
                
                if not details["completed"]:
                    btn_action = draw_button("Marcar como Realizada", 50, 270, 250, 40, VERDE, (0, 200, 0), "marcar_realizada")
                    if btn_action == "marcar_realizada":
                        pending_action = "mark_completed"
                        action_data = {
                            "date_str": date_str,
                            "time_str": time_str
                        }
                        admin_code = generate_admin_code()
                        current_screen = "admin_verification"
                        input_text = ""
                else:
                    already_text = font_medium.render("Esta cita ya fue marcada como realizada.", True, VERDE)
                    screen.blit(already_text, (50, 270))
            else:
                error_msg = font_medium.render("Cita no encontrada.", True, ROJO)
                screen.blit(error_msg, (50, 220))
                error_sound.play()
        except:
            error_msg = font_medium.render("Formato inválido.", True, ROJO)
            screen.blit(error_msg, (50, 220))
            error_sound.play()
    
    btn_action = draw_button("Regresar", WIDTH - 250, 450, 200, 50, GRIS_OSCURO, AZUL_OSCURO, "regresar")
    if btn_action == "regresar":
        current_screen = "admin_menu"

# Bucle principal
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if current_screen == "login":
                if WIDTH/2 - 150 < event.pos[0] < WIDTH/2 + 150 and 200 < event.pos[1] < 250:
                    active_input = True
                else:
                    active_input = False
            
            elif current_screen == "admin_verification":
                if WIDTH/2 - 150 < event.pos[0] < WIDTH/2 + 150 and 250 < event.pos[1] < 300:
                    active_input = True
                else:
                    active_input = False
            
            elif current_screen in ["admin_cancel_appointment", "mark_completed"]:
                if 50 < event.pos[0] < 250 and 150 < event.pos[1] < 190:
                    active_input = True
                    input_text = "date:"
                elif 300 < event.pos[0] < 400 and 150 < event.pos[1] < 190:
                    active_input = True
                    input_text = "time:"
                else:
                    active_input = False
        
        if event.type == pygame.KEYDOWN:
            if active_input:
                if event.key == pygame.K_RETURN:
                    active_input = False
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                elif event.key == pygame.K_TAB:
                    active_input = False
                else:
                    if current_screen == "login" and len(input_text) < 8 and (event.unicode.isdigit() or event.unicode == admin_password[len(input_text)] if len(input_text) < len(admin_password) else False):
                        input_text += event.unicode
                    elif current_screen == "admin_verification" and len(input_text) < 6:
                        input_text += event.unicode
                    elif current_screen in ["admin_cancel_appointment", "mark_completed"]:
                        if "date:" in input_text and len(input_text) < 15:
                            input_text += event.unicode
                        elif "time:" in input_text and len(input_text) < 8:
                            input_text += event.unicode
    
    # Dibujar la pantalla actual
    if current_screen == "login":
        login_screen()
    elif current_screen == "admin_verification":
        admin_verification_screen()
    elif current_screen == "user_menu":
        user_menu_screen()
    elif current_screen == "admin_menu":
        admin_menu_screen()
    elif current_screen == "schedule_appointment":
        schedule_appointment_screen()
    elif current_screen == "cancel_appointment":
        cancel_appointment_screen()
    elif current_screen == "view_appointments":
        view_appointments_screen()
    elif current_screen == "view_all_appointments":
        view_all_appointments_screen()
    elif current_screen == "admin_cancel_appointment":
        admin_cancel_appointment_screen()
    elif current_screen == "mark_completed":
        mark_completed_screen()
    elif current_screen == "logout":
        current_screen = "login"
        user_id = ""
        user_type = ""
        input_text = ""
    
    pygame.display.flip()
    pygame.time.Clock().tick(30)

pygame.quit()
sys.exit()