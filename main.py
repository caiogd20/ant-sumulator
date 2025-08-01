import pygame, sys
import random
from pygame.locals import QUIT

# Tamanho da tela
largura, altura = 500, 500
tamanho_celula = 20
cols = largura // tamanho_celula
rows = altura // tamanho_celula

class Celula:
    def __init__(self):
        # Variações leves de verde
        self.cor = (0, random.randint(120, 180), 0)
        self.estado = "normal"  # depois podemos usar: "pisada", "comida", "feromonio", etc.

    def desenhar(self, superficie, x, y):
        pygame.draw.rect(
            superficie,
            self.cor,
            (x * tamanho_celula, y * tamanho_celula, tamanho_celula, tamanho_celula)
        )

# Inicializa a grade
grade = [[Celula() for _ in range(cols)] for _ in range(rows)]

# ----- FORMIGA (igual antes) -----
class Formiga:
    def __init__(self, pos, color):
        self.pos = pos
        self.color = color

    def draw(self, superficie):
        pygame.draw.circle(superficie, self.color, self.pos, 5)

    def move(self):
        dx = random.randint(-2, 2)
        dy = random.randint(-2, 2)
        new_x = max(0, min(self.pos[0] + dx, largura))
        new_y = max(0, min(self.pos[1] + dy, altura))
        self.pos = (new_x, new_y)

# ----- PYGAME SETUP -----
pygame.init()
formiguero_pos = (largura // 2, altura // 2)
DISPLAYSURF = pygame.display.set_mode((largura, altura))
pygame.display.set_caption('Simulador de Formigueiro')
clock = pygame.time.Clock()

green = (34, 139, 34)
brawn = (165, 42, 42)
black = (0, 0, 0)

pygame.mouse.set_visible(False)

formigas = {}
for i in range(5):
    formigas[i] = Formiga(formiguero_pos, black)

# ----- LOOP PRINCIPAL -----
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    # Desenha cada célula da grade
    for y in range(rows):
        for x in range(cols):
            grade[y][x].desenhar(DISPLAYSURF, x, y)

    # Desenha formigueiro
    pygame.draw.circle(DISPLAYSURF, brawn, formiguero_pos, 20)

    # Mover e desenhar as formigas
    for i in formigas:
        formigas[i].move()
        formigas[i].draw(DISPLAYSURF)

    pygame.display.update()
    clock.tick(30)
