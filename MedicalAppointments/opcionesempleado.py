import pygame # type: ignore
import sys
import subprocess

# Inicializar pygame
pygame.init()

# Pantalla completa
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Gestión de Citas Médicas")

# Colores
BACKGROUND_COLOR = (30, 30, 30)
BUTTON_COLOR = (70, 130, 180)
BUTTON_HOVER_COLOR = (100, 149, 237)
TEXT_COLOR = (255, 255, 255)

# Fuente
font = pygame.font.SysFont('Arial', 40)

# Clase Botón
class Button:
    def __init__(self, x, y, width, height, text, callback):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.hovered = False

    def draw(self, surface):
        color = BUTTON_HOVER_COLOR if self.hovered else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=15)
        text_surf = font.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.hovered:
            self.callback()

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

# Funciones para abrir scripts
def abrir_miscitas():
    pygame.quit()
    subprocess.run(["python", "citasempleado.py"])
    sys.exit()

def abrir_cancelarcita():
    pygame.quit()
    subprocess.run(["python", "eliminarempleado.py"])
    sys.exit()

def volver_al_inicio():
    pygame.quit()
    subprocess.run(["python", "Inicio.py"])
    sys.exit()

# Crear botones centrados
button_width = 300
button_height = 80
button_spacing = 40
start_y = (HEIGHT - (3 * button_height + 2 * button_spacing)) // 2

buttons = [
    Button((WIDTH - button_width) // 2, start_y, button_width, button_height, "Ver Citas", abrir_miscitas),
    Button((WIDTH - button_width) // 2, start_y + (button_height + button_spacing), button_width, button_height, "Cancelar Citas", abrir_cancelarcita),
    Button((WIDTH - button_width) // 2, start_y + 2 * (button_height + button_spacing), button_width, button_height, "Salir a Inicio", volver_al_inicio)
]

# Bucle principal
clock = pygame.time.Clock()
running = True
while running:
    screen.fill(BACKGROUND_COLOR)

    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
        for button in buttons:
            button.check_event(event)

    for button in buttons:
        button.update(mouse_pos)
        button.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()