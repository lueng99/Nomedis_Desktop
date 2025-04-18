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
SCROLLBAR_COLOR = (100, 100, 100)
SCROLLBAR_HOVER = (120, 120, 120)

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

# Clase para campo de entrada de texto
class InputBox:
    def __init__(self, x, y, width, height, text=''):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = GRAY
        self.text = text
        self.active = False
        self.font = pygame.font.Font(None, height - 10)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                return self.text
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
        return None
        
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, 0, 5)
        pygame.draw.rect(screen, WHITE if self.active else BLACK, self.rect, 2, 5)
        text_surface = self.font.render(self.text, True, WHITE)
        screen.blit(text_surface, (self.rect.x + 10, self.rect.y + (self.rect.height - text_surface.get_height()) // 2))

# Clase para la barra de desplazamiento
class ScrollBar:
    def __init__(self, x, y, height, total_items, visible_items):
        self.rect = pygame.Rect(x, y, 20, height)
        self.scroll_rect = pygame.Rect(x, y, 20, height // visible_items * total_items)
        self.total_items = total_items
        self.visible_items = visible_items
        self.scroll_pos = 0
        self.dragging = False
        self.hovered = False
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.scroll_rect.collidepoint(event.pos):
                self.dragging = True
            elif self.rect.collidepoint(event.pos):
                rel_y = event.pos[1] - self.rect.y
                self.scroll_pos = min(max(0, rel_y / self.rect.height * self.total_items - self.visible_items // 2), 
                                    self.total_items - self.visible_items)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            rel_y = event.pos[1] - self.rect.y
            self.scroll_pos = min(max(0, rel_y / self.rect.height * self.total_items - self.visible_items // 2), 
                             self.total_items - self.visible_items)
            
    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos) or self.scroll_rect.collidepoint(pos)
        
    def draw(self, screen):
        pygame.draw.rect(screen, SCROLLBAR_COLOR, self.rect, border_radius=10)
        
        scroll_height = max(30, self.rect.height * self.visible_items / self.total_items)
        scroll_y = self.rect.y + (self.scroll_pos / self.total_items) * self.rect.height
        
        self.scroll_rect = pygame.Rect(self.rect.x, scroll_y, self.rect.width, scroll_height)
        color = SCROLLBAR_HOVER if self.hovered or self.dragging else SCROLLBAR_COLOR
        pygame.draw.rect(screen, color, self.scroll_rect, border_radius=10)

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
                        file.write(line)
    except FileNotFoundError:
        pass

# Función principal
def main():
    clock = pygame.time.Clock()
    appointments = load_appointments()
    appointments.sort(key=lambda x: x['datetime'])
    
    # Variables para búsqueda y scroll
    search_dni = ""
    filtered_appointments = appointments.copy()
    scroll_offset = 0
    items_per_page = 15
    
    # Variables para confirmación de eliminación
    confirm_delete = None
    countdown_start = None
    
    # Fuentes
    font_small, font_medium, font_large = get_scaled_fonts(SCREEN_HEIGHT)
    
    # Elementos de UI
    search_box = InputBox(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 10, SCREEN_WIDTH // 2, 40)
    scroll_bar = ScrollBar(SCREEN_WIDTH - 50, SCREEN_HEIGHT // 5 + 50, 
                          SCREEN_HEIGHT * 3 // 5, len(filtered_appointments), items_per_page)
    
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_F5:
                    # Actualizar lista al presionar F5
                    appointments = load_appointments()
                    appointments.sort(key=lambda x: x['datetime'])
                    filtered_appointments = [app for app in appointments if search_dni.lower() in app['dni'].lower()]
                    scroll_bar.total_items = len(filtered_appointments)
                    scroll_offset = min(scroll_offset, max(0, len(filtered_appointments) - items_per_page))
            
            # Manejar eventos de entrada de búsqueda
            search_result = search_box.handle_event(event)
            if search_result is not None:
                search_dni = search_result
                filtered_appointments = [app for app in appointments if search_dni.lower() in app['dni'].lower()]
                scroll_bar.total_items = len(filtered_appointments)
                scroll_offset = 0
            
            # Manejar eventos de scroll
            scroll_bar.handle_event(event)
            scroll_offset = int(scroll_bar.scroll_pos)
            
            # Manejar clics en botones de cancelar
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if confirm_delete:
                    if ok_button.is_clicked(mouse_pos, event):
                        delete_appointment(confirm_delete['dni'], confirm_delete['date_str'], confirm_delete['time_str'])
                        appointments = load_appointments()
                        appointments.sort(key=lambda x: x['datetime'])
                        filtered_appointments = [app for app in appointments if search_dni.lower() in app['dni'].lower()]
                        scroll_bar.total_items = len(filtered_appointments)
                        scroll_offset = min(scroll_offset, max(0, len(filtered_appointments) - items_per_page))
                        confirm_delete = None
                        countdown_start = None
                    if cancel_button.is_clicked(mouse_pos, event):
                        confirm_delete = None
                        countdown_start = None
                else:
                    for idx, cancel_button in enumerate(cancel_buttons):
                        if cancel_button.is_clicked(mouse_pos, event):
                            confirm_delete = filtered_appointments[scroll_offset + idx]
                            countdown_start = pygame.time.get_ticks()

        screen.fill(BACKGROUND_COLOR)
        
        # Dibujar título
        title = font_large.render("Todas las Citas Médicas", True, LIGHT_BLUE)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 20))
        
        # Dibujar campo de búsqueda
        search_label = font_medium.render("Buscar por DNI:", True, WHITE)
        screen.blit(search_label, (SCREEN_WIDTH // 4 - search_label.get_width() - 20, SCREEN_HEIGHT // 10 + 10))
        search_box.draw(screen)
        
        # Botón de actualizar (F5)
        refresh_text = font_small.render("Presiona F5 para actualizar", True, GRAY)
        screen.blit(refresh_text, (SCREEN_WIDTH // 2 - refresh_text.get_width() // 2, SCREEN_HEIGHT // 10 + 50))
        
        # Botón salir
        exit_button = Button(SCREEN_WIDTH - 200, SCREEN_HEIGHT - 80, 170, 60, "Volver", BUTTON_COLOR, BUTTON_HOVER)
        exit_button.check_hover(mouse_pos)
        exit_button.draw(screen, font_medium)
        
        # Encabezados de la tabla
        headers = ["DNI", "Fecha", "Hora", "Acción"]
        header_y = SCREEN_HEIGHT // 5
        col_positions = [SCREEN_WIDTH * 0.1, SCREEN_WIDTH * 0.35, SCREEN_WIDTH * 0.55, SCREEN_WIDTH * 0.75]

        for i, header in enumerate(headers):
            header_text = font_medium.render(header, True, GREEN)
            screen.blit(header_text, (col_positions[i], header_y))

        pygame.draw.line(screen, GRAY, (SCREEN_WIDTH * 0.05, header_y + 40), (SCREEN_WIDTH * 0.95, header_y + 40), 2)
        
        # Mostrar citas
        visible_appointments = filtered_appointments[scroll_offset:scroll_offset + items_per_page]
        cancel_buttons = []
        
        for i, app in enumerate(visible_appointments):
            y_pos = header_y + 60 + i * 50
            screen.blit(font_small.render(app['dni'], True, WHITE), (col_positions[0], y_pos))
            screen.blit(font_small.render(app['date_str'], True, WHITE), (col_positions[1], y_pos))
            screen.blit(font_small.render(app['time_str'], True, WHITE), (col_positions[2], y_pos))

            cancel_btn = Button(col_positions[3], y_pos - 10, 100, 40, "Cancelar", RED, (255, 100, 100))
            cancel_btn.check_hover(mouse_pos)
            cancel_btn.draw(screen, font_small)
            cancel_buttons.append(cancel_btn)
        
        # Mostrar barra de desplazamiento si hay más elementos de los que caben
        if len(filtered_appointments) > items_per_page:
            scroll_bar.check_hover(mouse_pos)
            scroll_bar.draw(screen)
        
        # Mostrar mensaje si no hay citas
        if not filtered_appointments:
            no_app_text = font_medium.render("No se encontraron citas", True, RED)
            screen.blit(no_app_text, (SCREEN_WIDTH // 2 - no_app_text.get_width() // 2, SCREEN_HEIGHT // 2))
        
        # Mostrar confirmación de eliminación
        if confirm_delete:
            elapsed = (pygame.time.get_ticks() - countdown_start) // 1000
            remaining = max(0, 5 - elapsed)
            confirm_rect = pygame.Rect(SCREEN_WIDTH//4, SCREEN_HEIGHT//3, SCREEN_WIDTH//2, SCREEN_HEIGHT//3)
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