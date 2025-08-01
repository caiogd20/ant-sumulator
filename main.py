import pygame, sys
import random
from pygame.locals import QUIT

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

pygame.init()
clock = pygame.time.Clock()
altura = 600
largura = 600
formigas = {}
formiguero_pos = (altura / 2, largura / 2)
DISPLAYSURF = pygame.display.set_mode((altura, largura))
pygame.display.set_caption('ant simulator')
green = (34, 139, 34)  # verde folha
brawn = (165, 42, 42)
black = (0, 0, 0)
pygame.mouse.set_visible(False)

# Criação das formigas
for i in range(5):
    formigas[i] = Formiga(formiguero_pos, black)

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    DISPLAYSURF.fill(green)

    # Mover e desenhar as formigas
    for i in formigas:
        formigas[i].move()   # Move a formiga
        formigas[i].draw(DISPLAYSURF)  # Desenha a formiga

    pygame.draw.circle(DISPLAYSURF, brawn, formiguero_pos, 20)
    clock.tick(30)
    pygame.display.update()