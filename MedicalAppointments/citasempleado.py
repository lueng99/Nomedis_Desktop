import pygame  # type: ignore
import sys
import subprocess
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
SCROLLBAR_COLOR = (80, 80, 80)
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

# Clase para la scrollbar
class ScrollBar:
    def __init__(self, x, y, height, content_height, visible_height):
        self.x = x
        self.y = y
        self.width = 20
        self.height = height
        self.content_height = content_height
        self.visible_height = visible_height
        self.scroll_y = 0
        self.dragging = False
        self.hovered = False
        
        self.thumb_height = max(30, int((visible_height / content_height) * height))
        self.thumb_rect = pygame.Rect(x, y, self.width, self.thumb_height)
        
    def update(self, mouse_pos, mouse_buttons, mouse_wheel):
        self.hovered = self.thumb_rect.collidepoint(mouse_pos) or \
                      (self.x <= mouse_pos[0] <= self.x + self.width and 
                       self.y <= mouse_pos[1] <= self.y + self.height)
        
        if mouse_wheel != 0 and self.hovered:
            self.scroll_y -= mouse_wheel * 20
            self.scroll_y = max(0, min(self.scroll_y, self.content_height - self.visible_height))
        
        if mouse_buttons[0]:
            if self.thumb_rect.collidepoint(mouse_pos) and not self.dragging:
                self.dragging = True
                self.drag_offset = mouse_pos[1] - self.thumb_rect.y
            elif self.dragging:
                new_y = mouse_pos[1] - self.drag_offset
                new_y = max(self.y, min(new_y, self.y + self.height - self.thumb_rect.height))
                thumb_range = self.height - self.thumb_rect.height
                if thumb_range > 0:
                    scroll_ratio = (new_y - self.y) / thumb_range
                    self.scroll_y = scroll_ratio * (self.content_height - self.visible_height)
        else:
            self.dragging = False
        
        if self.content_height > self.visible_height:
            scroll_ratio = self.scroll_y / (self.content_height - self.visible_height)
            thumb_range = self.height - self.thumb_rect.height
            self.thumb_rect.y = self.y + int(scroll_ratio * thumb_range)
        else:
            self.thumb_rect.y = self.y
        
    def draw(self, surface):
        pygame.draw.rect(surface, DARK_BLUE, (self.x, self.y, self.width, self.height), border_radius=10)
        thumb_color = SCROLLBAR_HOVER if self.hovered or self.dragging else SCROLLBAR_COLOR
        pygame.draw.rect(surface, thumb_color, self.thumb_rect, border_radius=10)

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
    
    appointments.sort(key=lambda x: x['datetime'])
    return appointments

# Función principal
def main():
    clock = pygame.time.Clock()
    appointments = load_appointments()
    
    current_width, current_height = SCREEN_WIDTH, SCREEN_HEIGHT
    screen = pygame.display.set_mode((current_width, current_height), pygame.FULLSCREEN)
    font_small, font_medium, font_large = get_scaled_fonts(current_height)
    
    header_height = current_height // 6
    footer_height = 100
    list_height = current_height - header_height - footer_height
    item_height = 40
    visible_items = list_height // item_height
    
    scrollbar_width = 20
    scrollbar = ScrollBar(
        current_width - scrollbar_width - 20, 
        header_height + 40, 
        list_height - 40, 
        len(appointments) * item_height, 
        visible_items * item_height
    )
    
    # Crear botón "Volver"
    exit_button = Button(
        current_width - 200, 
        current_height - 80, 
        170, 60, 
        "Volver", 
        BUTTON_COLOR, 
        BUTTON_HOVER
    )
    
    running = True
    mouse_wheel = 0

    while running:
        mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()
        
        mouse_wheel = 0  # Resetear cada frame
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEWHEEL:
                mouse_wheel = event.y
            elif event.type == pygame.FINGERMOTION:
                mouse_wheel = int(event.dy * 10)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Clic izquierdo
                    if exit_button.is_clicked(mouse_pos, event):
                        pygame.quit()
                        subprocess.run([sys.executable, "opcionesempleado.py"])
                        sys.exit()

        scrollbar.update(mouse_pos, mouse_buttons, mouse_wheel)
        exit_button.check_hover(mouse_pos)

        screen.fill(BACKGROUND_COLOR)
        
        title = font_large.render("Todas las Citas Médicas Registradas", True, LIGHT_BLUE)
        screen.blit(title, (current_width // 2 - title.get_width() // 2, current_height // 20))
        
        if not appointments:
            no_app_text = font_medium.render("No se encontraron citas en citas.txt", True, RED)
            screen.blit(no_app_text, (current_width // 2 - no_app_text.get_width() // 2, current_height // 2))
        else:
            headers = ["DNI", "Fecha", "Hora"]
            header_y = header_height
            col_positions = [current_width * 0.1, current_width * 0.4, current_width * 0.7]
            
            for i, header in enumerate(headers):
                header_text = font_medium.render(header, True, GREEN)
                screen.blit(header_text, (col_positions[i], header_y))
            
            pygame.draw.line(screen, GRAY, (current_width * 0.05, header_y + 40), (current_width * 0.95, header_y + 40), 2)
            
            start_index = int(scrollbar.scroll_y / item_height)
            end_index = min(len(appointments), start_index + visible_items + 1)
            
            for i in range(start_index, end_index):
                app = appointments[i]
                y_pos = header_y + 60 + (i - start_index) * item_height - (scrollbar.scroll_y % item_height)
                
                if header_y + 60 <= y_pos < header_y + list_height:
                    screen.blit(font_small.render(app['dni'], True, WHITE), (col_positions[0], y_pos))
                    screen.blit(font_small.render(app['date_str'], True, WHITE), (col_positions[1], y_pos))
                    screen.blit(font_small.render(app['time_str'], True, WHITE), (col_positions[2], y_pos))
            
            if len(appointments) > visible_items:
                scrollbar.draw(screen)

        exit_button.draw(screen, font_medium)
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
