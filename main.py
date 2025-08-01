import pygame, sys
import random
from pygame.locals import QUIT

# Tamanho da tela
largura, altura = 500, 500
tamanho_celula = 20
cols = largura // tamanho_celula
rows = altura // tamanho_celula

# cor das células
cor_grama =lambda: (0, random.randint(120, 180), 0)
cor_formigueiro = (139, 69, 19)  # marrom

class Celula:
    def __init__(self, tipo="grama"):
        # Variações leves de verde
        self.tipo = tipo
        self.estado = "normal"  # depois podemos usar: "pisada", "comida", "feromonio", etc.
        if tipo == "formigueiro":
            self.cor = cor_formigueiro
        else:
            self.cor = cor_grama()

    def desenhar(self, superficie, x, y):
        pygame.draw.rect(
            superficie,
            self.cor,
            (x * tamanho_celula, y * tamanho_celula, tamanho_celula, tamanho_celula)
        )

# Inicializa a grade com células do tipo "grama"
grade = [[Celula() for _ in range(cols)] for _ in range(rows)]
# Define posição central para o formigueiro
formiguero_cx = cols // 2
formiguero_cy = rows // 2
# Define a célula do formigueiro
grade[formiguero_cy][formiguero_cx] = Celula(tipo="formigueiro")

# ----- FORMIGA -----
class Formiga:
    def __init__(self, cx, cy , color):
        self.cx = cx
        self.cy = cy
        self.color = color
        self.carregando_comida = False
        self.frame_delay = 0 

    def draw(self, superficie):
        centro_x = self.cx * tamanho_celula + tamanho_celula // 2
        centro_y = self.cy * tamanho_celula + tamanho_celula // 2
        pygame.draw.circle(superficie, self.color, (centro_x, centro_y), 5)
        if self.carregando_comida:
            pygame.draw.circle(superficie, (255, 0, 0), (centro_x, centro_y), 3)

    def move(self):
        self.frame_delay += 1
        if self.frame_delay >= 5:
            self.frame_delay = 0
            dx = random.randint(-1, 1)
            dy = random.randint(-1, 1)

            novo_cx = max(0, min(self.cx + dx, cols - 1))
            novo_cy = max(0, min(self.cy + dy, rows - 1))

            self.cx = novo_cx
            self.cy = novo_cy
    def tentar_coletar_comida(self, lista_de_comidas):
        for comida in lista_de_comidas:
            if comida.cx == self.cx and comida.cy == self.cy:
                self.carregando_comida = True
                lista_de_comidas.remove(comida)
                break

class Comida:
    def __init__(self, cx, cy):
        self.cx = cx
        self.cy = cy

    def draw(self, superficie):
        centro_x = self.cx * tamanho_celula + tamanho_celula // 2
        centro_y = self.cy * tamanho_celula + tamanho_celula // 2
        pygame.draw.circle(superficie, (255, 0, 0), (centro_x, centro_y), 3)

# ----- PYGAME SETUP -----
pygame.init()
DISPLAYSURF = pygame.display.set_mode((largura, altura))
pygame.display.set_caption('Simulador de Formigueiro')
clock = pygame.time.Clock()


black = (0, 0, 0)

pygame.mouse.set_visible(False)

formigas = []
for i in range(5):
    formigas.append(Formiga(formiguero_cx, formiguero_cy, black))
comidas = []
for i in range(5):
    comida_x = random.randint(0, cols - 1)
    comida_y = random.randint(0, rows - 1)
    comidas.append(Comida(comida_x, comida_y))

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

    

    # Mover e desenhar as formigas
    for f in formigas:
        f.move()
        f.tentar_coletar_comida(comidas)
        f.draw(DISPLAYSURF)
    for c in comidas:
        c.draw(DISPLAYSURF)
    

    pygame.display.update()
    clock.tick(30)
