import pygame # type: ignore
import sys
import subprocess

# Configuración inicial
pygame.init()
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Login de Usuario")

# Colores
BACKGROUND_COLOR = (240, 240, 240)
PRIMARY_COLOR = (50, 100, 200)
HOVER_COLOR = (70, 130, 250)
TEXT_COLOR = (30, 30, 30)
PLACEHOLDER_COLOR = (150, 150, 150)
BUTTON_TEXT_COLOR = (255, 255, 255)
LINE_COLOR = (100, 100, 100)
CLOSE_COLOR = (200, 50, 50)
CLOSE_HOVER_COLOR = (250, 70, 70)

# Fuentes (más moderna y ligera)
pygame.font.init()
font_big = pygame.font.SysFont("segoeui", 48)
font_medium = pygame.font.SysFont("segoeui", 36)
font_small = pygame.font.SysFont("segoeui", 24)

# Input box
input_box = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 60, 400, 60)
input_color_active = PRIMARY_COLOR
input_color_inactive = LINE_COLOR
input_color = input_color_inactive
active = False
text = ''

# Botón
button_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 20, 200, 60)

# Botón de cerrar
close_button_rect = pygame.Rect(WIDTH - 120, HEIGHT - 70, 80, 50)

clock = pygame.time.Clock()

# Animación variables
fade_alpha = 255
fade_in = True

def draw_fade(surface):
    global fade_alpha, fade_in
    fade = pygame.Surface((WIDTH, HEIGHT))
    fade.fill(BACKGROUND_COLOR)
    if fade_in:
        fade_alpha -= 8
        if fade_alpha <= 0:
            fade_alpha = 0
            fade_in = False
    fade.set_alpha(fade_alpha)
    surface.blit(fade, (0, 0))

def launch_program(file_name):
    pygame.quit()
    subprocess.Popen(["python", file_name])
    sys.exit()

def draw_text_center(surface, text, font, color, rect):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)

def save_dni(dni):
    # Guardar el DNI en el archivo dni.txt, sobrescribiendo la línea
    with open("dni.txt", "w") as file:
        file.write(dni)

# Main Loop
running = True
while running:
    screen.fill(BACKGROUND_COLOR)

    mouse_pos = pygame.mouse.get_pos()
    mouse_click = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_click = True

            # Activar input box
            if input_box.collidepoint(event.pos):
                active = True
                input_color = input_color_active
            else:
                active = False
                input_color = input_color_inactive

            # Clic en "Inicio de empleados"
            employee_text_surface = font_small.render('Inicio de empleados', True, PRIMARY_COLOR)
            employee_rect = employee_text_surface.get_rect()
            employee_rect.topleft = (40, HEIGHT - 60)
            if employee_rect.collidepoint(event.pos):
                launch_program("inicioempleado.py")

            # Clic en botón "Continuar"
            if button_rect.collidepoint(event.pos):
                if len(text) in [7, 8] and text.isdigit():
                    save_dni(text)  # Guardar el DNI en el archivo
                    launch_program("opcionesuser.py")
                else:
                    text = ''
            
            # Clic en botón "Cerrar"
            if close_button_rect.collidepoint(event.pos):
                running = False

        if event.type == pygame.KEYDOWN:
            if active:
                if event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    if len(text) < 8 and event.unicode.isdigit():
                        text += event.unicode

    # Dibuja input box
    pygame.draw.rect(screen, input_color, input_box, border_radius=10, width=3)

    if text == '':
        placeholder_surface = font_medium.render("Escriba aquí su DNI", True, PLACEHOLDER_COLOR)
        placeholder_rect = placeholder_surface.get_rect(center=input_box.center)
        screen.blit(placeholder_surface, placeholder_rect)
    else:
        txt_surface = font_medium.render(text, True, TEXT_COLOR)
        txt_rect = txt_surface.get_rect(center=input_box.center)
        screen.blit(txt_surface, txt_rect)

    # Dibuja botón "Continuar"
    if button_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, HOVER_COLOR, button_rect, border_radius=12)
    else:
        pygame.draw.rect(screen, PRIMARY_COLOR, button_rect, border_radius=12)

    draw_text_center(screen, "Continuar", font_medium, BUTTON_TEXT_COLOR, button_rect)

    # Dibuja texto "Inicio de empleados"
    employee_text = font_small.render('Inicio de empleados', True, PRIMARY_COLOR)
    employee_rect = employee_text.get_rect()
    employee_rect.topleft = (40, HEIGHT - 60)
    screen.blit(employee_text, employee_rect)

    # Subrayado dinámico
    pygame.draw.line(screen, PRIMARY_COLOR, 
                     (employee_rect.left, employee_rect.bottom + 2), 
                     (employee_rect.right, employee_rect.bottom + 2), 2)

    # Dibuja botón de cerrar
    if close_button_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, CLOSE_HOVER_COLOR, close_button_rect, border_radius=8)
    else:
        pygame.draw.rect(screen, CLOSE_COLOR, close_button_rect, border_radius=8)
    
    draw_text_center(screen, "Cerrar", font_small, BUTTON_TEXT_COLOR, close_button_rect)

    # Animación de entrada
    if fade_in:
        draw_fade(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()