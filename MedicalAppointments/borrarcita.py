import pygame # type: ignore
import sys
import subprocess
import os
from datetime import datetime

# Inicializar pygame
pygame.init()

# Obtener información de la pantalla
info = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h

# Configuración inicial de pantalla
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Visualizador de Citas Médicas")

# Colores
BACKGROUND_COLOR = (30, 30, 30)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 100, 200)
LIGHT_BLUE = (100, 150, 200)
DARK_BLUE = (30, 60, 90)
BUTTON_COLOR = (70, 70, 70)
BUTTON_HOVER = (100, 100, 100)

# Función para obtener fuentes escalables
def get_scaled_fonts(height):
    try:
        base_size = height // 30
        return (
            pygame.font.Font(None, int(base_size * 0.8)),  # small
            pygame.font.Font(None, int(base_size * 1.2)),  # medium
            pygame.font.Font(None, int(base_size * 1.8))   # large
        )
    except:
        base_size = max(16, height // 40)
        return (
            pygame.font.SysFont('Arial', int(base_size * 0.8)),
            pygame.font.SysFont('Arial', int(base_size * 1.2)),
            pygame.font.SysFont('Arial', int(base_size * 1.8))
        )

# Clase para botones
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        
    def draw(self, surface, font):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=5)
        
        text_surf = font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
        
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

# Función para cargar DNIs
def load_dnis():
    try:
        with open('dni.txt', 'r') as file:
            return [line.strip() for line in file.readlines() if line.strip()]
    except FileNotFoundError:
        return []

# Función para cargar citas
def load_appointments():
    appointments = []
    try:
        with open('citas.txt', 'r') as file:
            for line in file:
                if line.strip():
                    parts = line.strip().split(',')
                    if len(parts) >= 3:
                        dni = parts[0].strip()
                        date_str = parts[1].strip()
                        time_str = parts[2].strip()
                        try:
                            date = datetime.strptime(date_str, "%Y-%m-%d").date()
                            time = datetime.strptime(time_str, "%H:%M").time()
                            datetime_obj = datetime.combine(date, time)
                            appointments.append({
                                'dni': dni,
                                'datetime': datetime_obj,
                                'date_str': date_str,
                                'time_str': time_str
                            })
                        except ValueError:
                            continue
    except FileNotFoundError:
        pass
    return appointments

# Función para borrar cita del archivo
def delete_appointment(dni, date_str, time_str):
    try:
        with open('citas.txt', 'r') as file:
            lines = file.readlines()
        with open('citas.txt', 'w') as file:
            for line in lines:
                parts = line.strip().split(',')
                if len(parts) >= 3:
                    line_dni = parts[0].strip()
                    line_date = parts[1].strip()
                    line_time = parts[2].strip()
                    if not (line_dni == dni and line_date == date_str and line_time == time_str):
                        file.write(line + "\n")
    except FileNotFoundError:
        pass

# Función principal
def main():
    clock = pygame.time.Clock()
    dnis = load_dnis()
    appointments = load_appointments()
    filtered_appointments = [app for dni in dnis for app in appointments if app['dni'] == dni]
    filtered_appointments.sort(key=lambda x: x['datetime'])

    confirm_delete = None
    countdown_start = None
    current_width, current_height = SCREEN_WIDTH, SCREEN_HEIGHT
    screen = pygame.display.set_mode((current_width, current_height), pygame.FULLSCREEN)
    font_small, font_medium, font_large = get_scaled_fonts(current_height)

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if confirm_delete:
                    if ok_button.is_clicked(mouse_pos, event):
                        delete_appointment(confirm_delete['dni'], confirm_delete['date_str'], confirm_delete['time_str'])
                        appointments = load_appointments()
                        filtered_appointments = [app for dni in dnis for app in appointments if app['dni'] == dni]
                        filtered_appointments.sort(key=lambda x: x['datetime'])
                        confirm_delete = None
                        countdown_start = None
                    if cancel_button.is_clicked(mouse_pos, event):
                        confirm_delete = None
                        countdown_start = None
                else:
                    for idx, cancel_button in enumerate(cancel_buttons):
                        if cancel_button.is_clicked(mouse_pos, event):
                            confirm_delete = filtered_appointments[idx]
                            countdown_start = pygame.time.get_ticks()

        screen.fill(BACKGROUND_COLOR)

        # Botón salir
        exit_button = Button(current_width - 200, current_height - 80, 170, 60, "Volver", BUTTON_COLOR, BUTTON_HOVER)
        exit_button.check_hover(mouse_pos)
        if exit_button.is_clicked(mouse_pos, event):
            pygame.quit()
            subprocess.run([sys.executable, "opcionesuser.py"])
            sys.exit()
        exit_button.draw(screen, font_medium)

        title = font_large.render("Citas Médicas Registradas", True, LIGHT_BLUE)
        screen.blit(title, (current_width // 2 - title.get_width() // 2, current_height // 20))

        if not dnis:
            no_dni_text = font_medium.render("No se encontraron DNIs en dni.txt", True, RED)
            screen.blit(no_dni_text, (current_width // 2 - no_dni_text.get_width() // 2, current_height // 2))
        elif not filtered_appointments:
            no_app_text = font_medium.render("No se encontraron citas para los DNIs especificados", True, RED)
            screen.blit(no_app_text, (current_width // 2 - no_app_text.get_width() // 2, current_height // 2))
        else:
            headers = ["DNI", "Fecha", "Hora"]
            header_y = current_height // 6
            col_positions = [current_width * 0.1, current_width * 0.4, current_width * 0.7]

            for i, header in enumerate(headers):
                header_text = font_medium.render(header, True, GREEN)
                screen.blit(header_text, (col_positions[i], header_y))

            pygame.draw.line(screen, GRAY, (current_width * 0.05, header_y + 40), (current_width * 0.95, header_y + 40), 2)

            cancel_buttons = []
            max_appointments = min(20, (current_height - header_y - 120) // 50)

            for i, app in enumerate(filtered_appointments[:max_appointments]):
                y_pos = header_y + 60 + i * 50
                screen.blit(font_small.render(app['dni'], True, WHITE), (col_positions[0], y_pos))
                screen.blit(font_small.render(app['date_str'], True, WHITE), (col_positions[1], y_pos))
                screen.blit(font_small.render(app['time_str'], True, WHITE), (col_positions[2], y_pos))

                cancel_btn = Button(col_positions[2] + 120, y_pos - 10, 100, 40, "Cancelar", RED, (255, 100, 100))
                cancel_btn.check_hover(mouse_pos)
                cancel_btn.draw(screen, font_small)
                cancel_buttons.append(cancel_btn)

        if confirm_delete:
            elapsed = (pygame.time.get_ticks() - countdown_start) // 1000
            remaining = max(0, 5 - elapsed)
            confirm_rect = pygame.Rect(current_width//4, current_height//3, current_width//2, current_height//3)
            pygame.draw.rect(screen, DARK_BLUE, confirm_rect, border_radius=10)
            pygame.draw.rect(screen, WHITE, confirm_rect, 3, border_radius=10)

            text1 = font_medium.render(f"¿Cancelar cita del día {confirm_delete['date_str']}?", True, WHITE)
            screen.blit(text1, (confirm_rect.centerx - text1.get_width()//2, confirm_rect.y + 30))

            if remaining > 0:
                countdown_text = font_large.render(f"{remaining}", True, RED)
                screen.blit(countdown_text, (confirm_rect.centerx - countdown_text.get_width()//2, confirm_rect.centery))
            else:
                ok_button = Button(confirm_rect.x + 50, confirm_rect.bottom - 80, 120, 50, "OK", GREEN, (100, 255, 100))
                cancel_button = Button(confirm_rect.right - 170, confirm_rect.bottom - 80, 120, 50, "Cancelar", RED, (255, 100, 100))
                ok_button.check_hover(mouse_pos)
                cancel_button.check_hover(mouse_pos)
                ok_button.draw(screen, font_small)
                cancel_button.draw(screen, font_small)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
