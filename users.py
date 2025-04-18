import pygame # type: ignore
import sys
import os
import time
import subprocess

# Inicializar pygame
pygame.init()

# Obtener resolución actual de la pantalla
display_info = pygame.display.Info()
screen_width = display_info.current_w
screen_height = display_info.current_h

# Configuración de colores
COLOR_FONDO = (240, 240, 240)  # Gris claro
COLOR_TEXTO = (80, 80, 80)      # Gris oscuro
COLOR_BOTON = (120, 170, 220)   # Azul claro
COLOR_ERROR = (210, 70, 70)     # Rojo suave
COLOR_EXITO = (70, 180, 70)     # Verde suave
COLOR_BORDE = (200, 200, 200)   # Gris para bordes

# Configurar ventana sin marco
screen = pygame.display.set_mode((screen_width, screen_height), pygame.NOFRAME)
pygame.display.set_caption("Inicio de sesión")

# Fuentes
font_large = pygame.font.Font(None, 48)
font_medium = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 28)

# Diccionario de usuarios
usuarios = {
    "Admin": "Nomedis1",
    "Alvaro": "Alvaro!",
    "Guillermo": "GRS",
    "Eva": "ERJ"
}

# Función para efecto de transición
def fade_transition(surface, color, duration=1.0):
    overlay = pygame.Surface((screen_width, screen_height))
    overlay.fill(color)
    for alpha in range(0, 255, 5):
        overlay.set_alpha(alpha)
        surface.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.time.delay(30)

def draw_input_box(surface, x, y, text, color, active, show_cursor):
    # Fondo del input
    box = pygame.Surface((300, 45), pygame.SRCALPHA)
    pygame.draw.rect(box, COLOR_FONDO, (0, 0, 300, 45), border_radius=5)
    pygame.draw.rect(box, COLOR_BORDE if not active else color, (0, 0, 300, 45), 2, border_radius=5)
    
    # Texto con cursor
    display_text = text + ("|" if active and show_cursor else "")
    text_surface = font_medium.render(display_text, True, COLOR_TEXTO)
    box.blit(text_surface, (10, 8))  # Ajuste vertical interno
    
    surface.blit(box, (x, y))

def login():
    usuario_input = ""
    contrasena_input = ""
    active_usuario = False
    active_contrasena = False
    
    mensaje_error = ""
    error_alpha = 0
    show_cursor = True
    cursor_time = 0
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        dt = clock.tick(60) / 1000.0
        screen.fill(COLOR_FONDO)
        
        # Mostrar coordenadas del cursor
        mouse_x, mouse_y = pygame.mouse.get_pos()
        coord_text = font_small.render(f"X: {mouse_x} Y: {mouse_y}", True, (100, 100, 100))
        screen.blit(coord_text, (10, 10))
        
        # Título (posición más alta)
        title = font_large.render("Iniciar Sesión", True, COLOR_TEXTO)
        screen.blit(title, (screen_width//2 - title.get_width()//2, screen_height//3))
        
        # Control de cursor parpadeante
        cursor_time += dt
        if cursor_time >= 0.5:
            show_cursor = not show_cursor
            cursor_time = 0
        
        # Etiquetas (con mayor separación)
        user_label = font_small.render("Usuario:", True, COLOR_TEXTO)
        pass_label = font_small.render("Contraseña:", True, COLOR_TEXTO)
        
        # Posiciones ajustadas con más espacio
        label_user_y = screen_height//2 - 100
        input_user_y = screen_height//2 - 70
        label_pass_y = screen_height//2 - 20
        input_pass_y = screen_height//2 + 10
        mensaje_y = screen_height//2 + 80
        
        screen.blit(user_label, (screen_width//2 - 150, label_user_y))
        screen.blit(pass_label, (screen_width//2 - 150, label_pass_y))
        
        # Campos de entrada (con más espacio respecto a las etiquetas)
        draw_input_box(screen, screen_width//2 - 150, input_user_y, 
                      usuario_input, COLOR_BOTON, active_usuario, show_cursor)
        draw_input_box(screen, screen_width//2 - 150, input_pass_y, 
                      "*" * len(contrasena_input), COLOR_BOTON, active_contrasena, show_cursor)
        
        # Manejo de mensajes de error (con más espacio)
        if mensaje_error:
            error_alpha = min(255, error_alpha + 500 * dt)
            
            if error_alpha >= 255 and pygame.time.get_ticks() > 1000:
                error_alpha = max(0, error_alpha - 200 * dt)
                if error_alpha <= 0:
                    mensaje_error = ""
            
            error_surface = font_small.render(mensaje_error, True, COLOR_ERROR)
            error_surface.set_alpha(int(error_alpha))
            error_rect = error_surface.get_rect(center=(screen_width//2, mensaje_y))
            screen.blit(error_surface, error_rect)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                active_usuario = screen_width//2 - 150 <= event.pos[0] <= screen_width//2 + 150 and \
                               input_user_y <= event.pos[1] <= input_user_y + 45
                active_contrasena = screen_width//2 - 150 <= event.pos[0] <= screen_width//2 + 150 and \
                                   input_pass_y <= event.pos[1] <= input_pass_y + 45
            
            if event.type == pygame.KEYDOWN:
                if active_usuario:
                    if event.key == pygame.K_BACKSPACE:
                        usuario_input = usuario_input[:-1]
                    elif event.key not in [pygame.K_RETURN, pygame.K_TAB]:
                        usuario_input += event.unicode
                
                if active_contrasena:
                    if event.key == pygame.K_BACKSPACE:
                        contrasena_input = contrasena_input[:-1]
                    elif event.key not in [pygame.K_RETURN, pygame.K_TAB]:
                        contrasena_input += event.unicode
                
                if event.key == pygame.K_RETURN:
                    usuario = usuario_input.strip()
                    contrasena = contrasena_input.strip()
                    
                    if usuario in usuarios and usuarios[usuario] == contrasena:
                        # Mensaje de éxito
                        success = font_medium.render(f"Bienvenido {usuario}!", True, COLOR_EXITO)
                        screen.blit(success, (screen_width//2 - success.get_width()//2, mensaje_y))
                        pygame.display.flip()
                        
                        fade_transition(screen, COLOR_FONDO)
                        
                        try:
                            subprocess.Popen(["python3", "interfaz.py"])
                            time.sleep(0.5)
                        except Exception as e:
                            print(f"Error al abrir interfaz.py: {e}")
                        
                        running = False
                    else:
                        mensaje_error = "Usuario o contraseña incorrectos"
                        error_alpha = 0
                
                if event.key == pygame.K_TAB:
                    active_usuario, active_contrasena = active_contrasena, active_usuario
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    login()
