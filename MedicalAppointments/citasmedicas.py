import pygame # type: ignore
import sys
import calendar
from datetime import datetime
import os
import subprocess 

# Inicializar Pygame
pygame.init()

def launch_program(file_name):
    pygame.quit()
    subprocess.Popen(["python", file_name])
    sys.exit()

# Configuración de pantalla completa según resolución
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Sistema de Citas Médicas")

# Colores
BACKGROUND_COLOR = (30, 30, 30)  # Color de fondo oscuro
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

# Fuentes
try:
    font_small = pygame.font.Font(None, int(HEIGHT/40))
    font_medium = pygame.font.Font(None, int(HEIGHT/30))
    font_large = pygame.font.Font(None, int(HEIGHT/20))
except:
    font_small = pygame.font.SysFont('Arial', 16)
    font_medium = pygame.font.SysFont('Arial', 20)
    font_large = pygame.font.SysFont('Arial', 24)

# Festivos españoles
festivos = {
    2025: [(1, 1), (1, 6), (4, 17), (4, 18), (5, 1), (8, 15), (10, 12), (11, 1), (12, 6), (12, 8), (12, 25)],
    2026: [(1, 1), (1, 6), (4, 2), (4, 3), (5, 1), (8, 15), (10, 12), (11, 1), (12, 6), (12, 8), (12, 25)],
    2027: [(1, 1), (1, 6), (3, 25), (3, 26), (5, 1), (8, 15), (10, 12), (11, 1), (12, 6), (12, 8), (12, 25)]
}

class Button:
    def __init__(self, x, y, width, height, text, color=BUTTON_COLOR, hover_color=BUTTON_HOVER):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=10)
        
        text_surf = font_medium.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
        
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

class CitaMedica:
    def __init__(self):
        self.current_year = datetime.now().year
        self.current_month = datetime.now().month
        self.selected_year = self.current_year
        self.selected_month = self.current_month
        self.selected_day = None
        self.selected_hour = None
        self.dnis = self.leer_dnis()
        self.citas = self.leer_citas()
        self.state = "year_selection"  # Estados: year_selection, month_selection, day_selection, hour_selection
        
        # Botones generales
        btn_width = WIDTH // 6
        self.back_button = Button(20, HEIGHT - 70, btn_width, 50, "Volver")
        self.cancel_button = Button(WIDTH - btn_width - 20, HEIGHT - 70, btn_width, 50, "Cancelar")
        
    def leer_dnis(self):
        try:
            with open("dni.txt", "r") as f:
                return [line.strip() for line in f.readlines() if line.strip()]
        except FileNotFoundError:
            print("Error: No se encontró el archivo dni.txt")
            return []
    
    def leer_citas(self):
        citas = {}
        try:
            if os.path.exists("citas.txt"):
                with open("citas.txt", "r") as f:
                    for line in f:
                        parts = line.strip().split(", ")
                        if len(parts) >= 3:
                            fecha = parts[1]
                            hora = parts[2]
                            if fecha not in citas:
                                citas[fecha] = []
                            citas[fecha].append(hora)
        except Exception as e:
            print(f"Error al leer citas: {e}")
        return citas
    
    def guardar_cita(self):
        if not self.dnis:
            print("No hay DNIs disponibles")
            return False
        
        dni = self.dnis[0]  # Tomamos el primer DNI
        fecha = f"{self.selected_year}-{self.selected_month:02d}-{self.selected_day:02d}"
        
        try:
            with open("citas.txt", "a") as f:
                f.write(f"{dni}, {fecha}, {self.selected_hour}\n")
            
            # Actualizar citas en memoria
            if fecha not in self.citas:
                self.citas[fecha] = []
            self.citas[fecha].append(self.selected_hour)
            
            return True
        except Exception as e:
            print(f"Error al guardar cita: {e}")
            return False
    
    def draw_year_selection(self):
        screen.fill(BACKGROUND_COLOR)
        
        # Título
        title = font_large.render("Seleccione el año", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//8))
        
        # Años disponibles
        years = [self.current_year, self.current_year + 1, self.current_year + 2]
        year_buttons = []
        
        for i, year in enumerate(years):
            btn_width = WIDTH // 3
            btn_height = HEIGHT // 6
            x = WIDTH//2 - btn_width//2
            y = HEIGHT//3 + i * (btn_height + 20)
            
            button = Button(x, y, btn_width, btn_height, str(year), DARK_BLUE, BLUE)
            button.draw(screen)
            year_buttons.append((year, button))
        
        # Botones generales
        self.back_button.draw(screen)
        self.cancel_button.draw(screen)
        
        pygame.display.flip()
        return year_buttons
    
    def draw_month_calendar(self):
        screen.fill(BACKGROUND_COLOR)
        
        # Título
        month_name = calendar.month_name[self.selected_month]
        title = font_large.render(f"{month_name} {self.selected_year}", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//10))
        
        # Flechas para cambiar mes
        arrow_size = HEIGHT // 20
        left_arrow = [
            (50, HEIGHT//10),
            (50 + arrow_size, HEIGHT//10 - arrow_size//2),
            (50 + arrow_size, HEIGHT//10 + arrow_size//2)
        ]
        right_arrow = [
            (WIDTH-50, HEIGHT//10),
            (WIDTH-50 - arrow_size, HEIGHT//10 - arrow_size//2),
            (WIDTH-50 - arrow_size, HEIGHT//10 + arrow_size//2)
        ]
        pygame.draw.polygon(screen, BLUE, left_arrow)
        pygame.draw.polygon(screen, BLUE, right_arrow)
        
        # Días de la semana
        days = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        day_width = WIDTH // 8
        for i, day in enumerate(days):
            text = font_medium.render(day, True, WHITE)
            screen.blit(text, (day_width//2 + i*day_width - text.get_width()//2, HEIGHT//6))
        
        # Calendario
        cal = calendar.monthcalendar(self.selected_year, self.selected_month)
        day_buttons = []
        day_height = (HEIGHT - HEIGHT//3) // 6
        
        for week_num, week in enumerate(cal):
            for day_num, day in enumerate(week):
                if day != 0:
                    x = day_width//2 + day_num * day_width - day_width//3
                    y = HEIGHT//4 + week_num * day_height
                    
                    # Verificar si es seleccionable
                    es_domingo = day_num == 6
                    es_festivo = (self.selected_month, day) in festivos.get(self.selected_year, [])
                    fecha_str = f"{self.selected_year}-{self.selected_month:02d}-{day:02d}"
                    horas_ocupadas = self.citas.get(fecha_str, [])
                    dia_completo = len(horas_ocupadas) >= 12
                    
                    if es_domingo or es_festivo:
                        color = RED
                        selectable = False
                    elif dia_completo:
                        color = GRAY
                        selectable = False
                    else:
                        color = LIGHT_BLUE
                        selectable = True
                    
                    rect = pygame.Rect(x, y, day_width//1.5, day_height//1.5)
                    pygame.draw.rect(screen, color, rect, border_radius=5)
                    pygame.draw.rect(screen, BLACK, rect, 2, border_radius=5)
                    
                    # Número del día
                    day_text = font_medium.render(str(day), True, BLACK if color != BLACK else WHITE)
                    screen.blit(day_text, (rect.centerx - day_text.get_width()//2, rect.centery - day_text.get_height()//2))
                    
                    if selectable:
                        day_buttons.append((day, rect))
        
        # Botones generales
        self.back_button.draw(screen)
        self.cancel_button.draw(screen)
        
        pygame.display.flip()
        return day_buttons
    
    def draw_hour_selection(self):
        screen.fill(BACKGROUND_COLOR)
        
        # Título
        fecha_str = f"{self.selected_year}-{self.selected_month:02d}-{self.selected_day:02d}"
        title = font_large.render(f"Seleccione hora para el {self.selected_day}/{self.selected_month}/{self.selected_year}", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//10))
        
        # Horas disponibles (8:00 - 20:00)
        horas_ocupadas = self.citas.get(fecha_str, [])
        horas = [f"{h:02d}:00" for h in range(8, 20)]
        hour_buttons = []
        
        for i, hora in enumerate(horas):
            if hora not in horas_ocupadas:
                x = WIDTH//4 + (i % 3) * (WIDTH//4)
                y = HEIGHT//4 + (i // 3) * (HEIGHT//10)
                
                button = Button(x, y, WIDTH//5, HEIGHT//12, hora, DARK_BLUE, BLUE)
                button.draw(screen)
                hour_buttons.append((hora, button))
        
        # Botón de confirmar (solo si hay hora seleccionada)
        if self.selected_hour:
            confirm_button = Button(WIDTH//2 - WIDTH//6, HEIGHT - HEIGHT//4, WIDTH//3, HEIGHT//10, 
                                  "Confirmar Cita", GREEN, (50, 150, 50))
            confirm_button.draw(screen)
            hour_buttons.append(("confirm", confirm_button))
        
        # Botones generales
        self.back_button.draw(screen)
        self.cancel_button.draw(screen)
        
        pygame.display.flip()
        return hour_buttons
    
    def draw_confirmation(self):
        screen.fill(BACKGROUND_COLOR)
        
        fecha_str = f"{self.selected_year}-{self.selected_month:02d}-{self.selected_day:02d}"
        msg = f"Cita confirmada para el {fecha_str} a las {self.selected_hour}"
        
        text = font_large.render(msg, True, GREEN)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - text.get_height()//2))
        
        # Botón para volver a opcionesuser.py
        ok_button = Button(WIDTH//2 - WIDTH//6, HEIGHT//2 + HEIGHT//10, WIDTH//3, HEIGHT//10, 
                         "Aceptar", GREEN, (50, 150, 50))
        ok_button.draw(screen)
        
        pygame.display.flip()
        
        # Esperar click en el botón
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    if ok_button.rect.collidepoint(mouse_pos):
                        waiting = False
                        self.go_to_opcionesuser()
            
            pygame.time.delay(50)
    
    def go_to_opcionesuser(self):
        """Función para volver a opcionesuser.py"""
        print("Redirigiendo a opcionesuser.py...")
        launch_program("opcionesuser.py")
        # En una aplicación real, aquí iría el código para cambiar a la pantalla de opciones
        # Por ahora simulamos cerrando la aplicación
        pygame.quit()
        sys.exit()
    
    def reset_selection(self):
        self.selected_day = None
        self.selected_hour = None
        self.state = "year_selection"
    
    def handle_back(self):
        """Maneja la acción del botón Volver"""
        if self.state == "month_selection":
            self.state = "year_selection"
            self.selected_month = datetime.now().month if self.selected_year == datetime.now().year else 1
        elif self.state == "hour_selection":
            self.state = "month_selection"
            self.selected_day = None
        elif self.state == "day_selection":
            self.state = "month_selection"
    
    def run(self):
        if not self.dnis:
            print("No hay DNIs disponibles. El programa no puede continuar.")
            return
        
        clock = pygame.time.Clock()
        running = True
        
        while running:
            mouse_pos = pygame.mouse.get_pos()
            
            # Dibujar el estado actual
            if self.state == "year_selection":
                year_buttons = self.draw_year_selection()
                self.state = "year_selection"  # Forzar estado correcto
            elif self.state == "month_selection":
                day_buttons = self.draw_month_calendar()
                self.state = "month_selection"  # Forzar estado correcto
            elif self.state == "hour_selection":
                hour_buttons = self.draw_hour_selection()
                self.state = "hour_selection"  # Forzar estado correcto
            
            # Comprobar hover en botones generales
            self.back_button.check_hover(mouse_pos)
            self.cancel_button.check_hover(mouse_pos)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                # Tecla ESC para salir de pantalla completa
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Botón Volver - Retrocede un paso
                    if self.back_button.is_clicked(mouse_pos, event):
                        self.handle_back()
                    
                    # Botón Cancelar - Va directamente a opcionesuser.py
                    if self.cancel_button.is_clicked(mouse_pos, event):
                        self.go_to_opcionesuser()
                    
                    # Lógica de selección según estado actual
                    if self.state == "year_selection":
                        for year, button in year_buttons:
                            if button.rect.collidepoint(mouse_pos):
                                self.selected_year = year
                                self.state = "month_selection"
                    
                    elif self.state == "month_selection":
                        # Flecha izquierda (mes anterior)
                        arrow_size = HEIGHT // 20
                        left_arrow_rect = pygame.Rect(50, HEIGHT//10 - arrow_size//2, arrow_size, arrow_size)
                        if left_arrow_rect.collidepoint(mouse_pos):
                            self.selected_month -= 1
                            if self.selected_month < 1:
                                self.selected_month = 12
                                self.selected_year -= 1
                        
                        # Flecha derecha (mes siguiente)
                        right_arrow_rect = pygame.Rect(WIDTH-50 - arrow_size, HEIGHT//10 - arrow_size//2, arrow_size, arrow_size)
                        if right_arrow_rect.collidepoint(mouse_pos):
                            self.selected_month += 1
                            if self.selected_month > 12:
                                self.selected_month = 1
                                self.selected_year += 1
                        
                        # Selección de día
                        for day, rect in day_buttons:
                            if rect.collidepoint(mouse_pos):
                                self.selected_day = day
                                self.state = "hour_selection"
                    
                    elif self.state == "hour_selection":
                        for hora, button in hour_buttons:
                            if button.rect.collidepoint(mouse_pos):
                                if hora == "confirm":
                                    if self.guardar_cita():
                                        self.draw_confirmation()
                                else:
                                    self.selected_hour = hora
            
            clock.tick(30)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = CitaMedica()
    app.run()