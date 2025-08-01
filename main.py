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
        self.pos = (self.pos[0] + random.randint(-1, 1), 
                    self.pos[1] + random.randint(-1, 1))

pygame.init()
altura = 500
largura = 500
formigas = {}
formiguero_pos = (altura / 2, largura / 2)
DISPLAYSURF = pygame.display.set_mode((altura, largura))
pygame.display.set_caption('ant simulator')
green = (0, 255, 0)
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
    pygame.display.update()