import pygame  # type: ignore
import subprocess
import os
import sys
import threading

pygame.init()

display_info = pygame.display.Info()
screen_size = (display_info.current_w, display_info.current_h)

window_x = (display_info.current_w - screen_size[0]) // 2
window_y = (display_info.current_h - screen_size[1]) // 2
os.environ['SDL_VIDEO_WINDOW_POS'] = f'{window_x},{window_y}'

screen = pygame.display.set_mode(screen_size, pygame.NOFRAME)
pygame.display.set_caption("App Proporcional")

# Rutas absolutas
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
IMAGES_PATH = os.path.join(BASE_DIR, "Imagenes")
MEDICAL_APP_PATH = os.path.join(BASE_DIR, "MedicalAppointments")
USERS_SCRIPT_PATH = os.path.join(BASE_DIR, "users.py")

try:
    background = pygame.image.load(os.path.join(IMAGES_PATH, "MenuNomedis.jpg"))
    background = pygame.transform.scale(background, screen_size)
    power_image = pygame.image.load(os.path.join(IMAGES_PATH, "Power.png"))
    red_image = pygame.image.load(os.path.join(IMAGES_PATH, "Red.png"))
    folder_image = pygame.image.load(os.path.join(IMAGES_PATH, "folder.png"))
    gear_image = pygame.image.load(os.path.join(IMAGES_PATH, "engranaje.png"))
    logo_image = pygame.image.load(os.path.join(IMAGES_PATH, "logo.png"))
    salud_image = pygame.image.load(os.path.join(IMAGES_PATH, "Salud.png"))
except pygame.error as e:
    print(f"Error al cargar imágenes: {e}")
    pygame.quit()
    sys.exit()

def calcular_botones(screen_size):
    width, height = screen_size
    button_center_1 = (int(width * 147 / 1920), int(height * 905 / 1080))
    button_center_2 = (int(width * 1761 / 1920), int(height * 905 / 1080))
    button_radius_1 = int(height * 108 / 1080)
    button_radius_2 = int(height * 50 / 1080)

    rect_button_1 = pygame.Rect(
        int(width * 339 / 1920),
        int(height * 903 / 1080),
        int(width * 87 / 1920),
        int(height * 119 / 1080),
    )

    rect_button_2 = pygame.Rect(
        int(width * 1498 / 1920),
        int(height * 903 / 1080),
        int(width * 87 / 1920),
        int(height * 116 / 1080),
    )

    return button_center_1, button_center_2, button_radius_1, button_radius_2, rect_button_1, rect_button_2

button_center_1, button_center_2, button_radius_1, button_radius_2, rect_button_1, rect_button_2 = calcular_botones(screen_size)

def is_point_inside_circle(x, y, center, radius):
    return (x - center[0])**2 + (y - center[1])**2 <= radius**2

def is_point_inside_rect(x, y, rect):
    return rect.collidepoint(x, y)

def open_firefox_gmail():
    try:
        subprocess.Popen(["firefox", "https://mail.google.com"])
    except FileNotFoundError:
        print("No se encontró Firefox. Por favor instálalo.")

def open_file_manager_linux():
    file_managers = ["nautilus", "thunar", "dolphin"]
    for manager in file_managers:
        try:
            subprocess.Popen([manager, "--no-desktop"])
            break
        except FileNotFoundError:
            continue
    else:
        print("No se encontró un gestor de archivos compatible.")

def go_to_login():
    def lanzar_login():
        subprocess.Popen(["python3", USERS_SCRIPT_PATH])
        pygame.quit()
        sys.exit()
    threading.Timer(1.5, lanzar_login).start()

def open_terminal():
    try:
        subprocess.Popen(["gnome-terminal"])
    except FileNotFoundError:
        print("No se encontró el terminal. Por favor instálalo.")

def open_medical_app():
    try:
        inicio_path = os.path.join(MEDICAL_APP_PATH, "Inicio.py")
        if os.path.exists(inicio_path):
            subprocess.Popen(["python3", inicio_path])
        else:
            print(f"No se encontró el archivo: {inicio_path}")
    except Exception as e:
        print(f"Error al abrir MedicalAppointments: {e}")

menu_visible = False
font = pygame.font.SysFont(None, int(screen_size[1] * 0.05))
menu_options = ["Apagar", "Ir al inicio de sesión"]
menu_rects = []
hovered_option = None

def draw_menu():
    global menu_rects, hovered_option
    menu_rects = []
    
    option_width = int(screen_size[0] * 0.2)
    option_height = int(screen_size[1] * 0.07)
    spacing = int(screen_size[1] * 0.02)
    
    start_x = button_center_1[0] - option_width // 2
    start_y = button_center_1[1] - button_radius_1 - (option_height * len(menu_options)) - (spacing * (len(menu_options)-1))
    
    if start_x < 10:
        start_x = 10
    
    mouse_pos = pygame.mouse.get_pos()
    hovered_option = None
    
    for i, option in enumerate(menu_options):
        rect = pygame.Rect(
            start_x, 
            start_y + i * (option_height + spacing), 
            option_width, 
            option_height
        )
        
        if rect.collidepoint(mouse_pos):
            hovered_option = option
            bg_color = (100, 149, 237)
            text_color = (50, 50, 50)
        else:
            bg_color = (50, 50, 50)
            text_color = (100, 149, 237)
        
        pygame.draw.rect(screen, bg_color, rect, border_radius=10)
        pygame.draw.rect(screen, (200, 200, 200), rect, 2, border_radius=10)
        
        text = font.render(option, True, text_color)
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)
        
        menu_rects.append((rect, option))

running = True
clock = pygame.time.Clock()
app_rects = []

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if is_point_inside_circle(x, y, button_center_2, button_radius_2):
                open_firefox_gmail()
            elif is_point_inside_circle(x, y, button_center_1, button_radius_1):
                menu_visible = not menu_visible
            elif is_point_inside_rect(x, y, rect_button_1):
                open_file_manager_linux()
            elif is_point_inside_rect(x, y, rect_button_2):
                print("Botón de Engranaje presionado")
                open_terminal()
            elif menu_visible:
                for rect, option in menu_rects:
                    if rect.collidepoint(x, y):
                        if option == "Apagar":
                            running = False
                        elif option == "Ir al inicio de sesión":
                            go_to_login()
            
            for i, rect in enumerate(app_rects):
                if rect.collidepoint(x, y) and i == 2:
                    open_medical_app()

    screen.blit(background, (0, 0))

    if logo_image:
        logo_width = int(screen_size[0] * 0.2)
        aspect_ratio = logo_image.get_height() / logo_image.get_width()
        logo_height = int(logo_width * aspect_ratio)
        logo_scaled = pygame.transform.scale(logo_image, (logo_width, logo_height))
        logo_x = (screen_size[0] - logo_width) // 2
        logo_y = int(screen_size[1] * 0.1) + 100
        screen.blit(logo_scaled, (logo_x, logo_y))

    if menu_visible:
        draw_menu()

    if power_image:
        power_scaled = pygame.transform.scale(power_image, (button_radius_1 * 2, button_radius_1 * 2))
        power_rect = power_scaled.get_rect(center=(button_center_1[0] + 10, button_center_1[1] - 5))
        screen.blit(power_scaled, power_rect)

    if red_image:
        original_w, original_h = red_image.get_size()
        red_scaled = pygame.transform.scale(red_image, (int(original_w * 0.75), int(original_h * 0.75)))
        red_rect = red_scaled.get_rect(center=(button_center_2[0] + 2, button_center_2[1]))
        screen.blit(red_scaled, red_rect)

    if folder_image:
        folder_scaled = pygame.transform.scale(folder_image, (rect_button_1.width, rect_button_1.height))
        screen.blit(folder_scaled, rect_button_1.topleft)

    if gear_image:
        gear_scaled = pygame.transform.scale(gear_image, (rect_button_2.width, rect_button_2.height))
        gear_position = (rect_button_2.left - 4, rect_button_2.top)
        screen.blit(gear_scaled, gear_position)

    # Dibujar los 5 cuadrados con la imagen en el centro
    rect_x, rect_y, rect_width, rect_height = 573, 906, 1348 - 573, 1020 - 906
    separation = 20
    available_width = rect_width - (separation * 4)
    square_width = available_width // 5

    app_rects = []

    for i in range(5):
        square_x = rect_x + i * (square_width + separation)
        square_y = rect_y
        rect = pygame.Rect(square_x, square_y, square_width, rect_height)
        app_rects.append(rect)
        
        if i == 2 and salud_image:
            salud_scaled = pygame.transform.scale(salud_image, (square_width, rect_height))
            screen.blit(salud_scaled, (square_x, square_y))
        else:
            pygame.draw.rect(screen, (0, 0, 255), (square_x, square_y, square_width, rect_height))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()