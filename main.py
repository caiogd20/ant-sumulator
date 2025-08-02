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
    def __init__(self, cx, cy , color, formigueiro_cx, formigueiro_cy):
        self.cx = cx
        self.cy = cy
        self.color = color
        self.carregando_comida = False
        self.frame_delay = 0
        self.formigueiro_cx = formigueiro_cx
        self.formigueiro_cy = formigueiro_cy
        self.ultima_comida_encontrada_cx = None
        self.ultima_comida_encontrada_cy = None 

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
            if (self.cx == self.ultima_comida_encontrada_cx and 
                self.cy == self.ultima_comida_encontrada_cy and 
                not self.carregando_comida):
                self.ultima_comida_encontrada_cx = None
                self.ultima_comida_encontrada_cy = None
            if self.carregando_comida:
                self.ir_para(self.formigueiro_cx, self.formigueiro_cy)
            elif self.ultima_comida_encontrada_cx is not None and self.ultima_comida_encontrada_cy is not None:
                self.ir_para(self.ultima_comida_encontrada_cx, self.ultima_comida_encontrada_cy)
            else:
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
                return self.cx, self.cy  # retorna a posição da comida coletada
    def tentar_entregar_comida(self, formigueiro_cx, formigueiro_cy):
        if self.carregando_comida and self.cx == formigueiro_cx and self.cy == formigueiro_cy:
            self.carregando_comida = False
            return True  # comida entregue
        return False
    def ir_para(self, destino_cx, destino_cy):
        dx = 0
        dy = 0
        if self.cx < destino_cx:
            dx = 1
        elif self.cx > destino_cx:
            dx = -1
        if self.cy < destino_cy:
            dy = 1
        elif self.cy > destino_cy:
            dy = -1

        novo_cx = max(0, min(self.cx + dx, cols - 1))
        novo_cy = max(0, min(self.cy + dy, rows - 1))

        self.cx = novo_cx
        self.cy = novo_cy
    def set_ultima_comida_encontrada(self, cx, cy):
        self.ultima_comida_encontrada_cx = cx
        self.ultima_comida_encontrada_cy = cy


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
CUSTO_NOVA_FORMIGA = 5
LIMITE_FORMIGAS = 50
FREQUENCIA_COMIDA = 120  # a cada 120 frames (~4 segundos com 30 FPS)
MAX_COMIDAS = 15
contador_frames = 0

pygame.mouse.set_visible(False)

formigas = []
for i in range(5):
    formigas.append(Formiga(formiguero_cx, formiguero_cy, black, formiguero_cx, formiguero_cy))
comidas = []
for i in range(5):
    comida_x = random.randint(0, cols - 1)
    comida_y = random.randint(0, rows - 1)
    comidas.append(Comida(comida_x, comida_y))
energia_colonia = 0


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
        pos_coleta = f.tentar_coletar_comida(comidas)
        if pos_coleta:
            cx, cy = pos_coleta
            for f1 in formigas:
                if f1 != f:
                    f1.set_ultima_comida_encontrada(cx, cy)
                    
        if f.tentar_entregar_comida(formiguero_cx, formiguero_cy):
            energia_colonia += 1
        if energia_colonia >= CUSTO_NOVA_FORMIGA and len(formigas) < LIMITE_FORMIGAS:
            nova_formiga = Formiga(formiguero_cx, formiguero_cy, black, formiguero_cx, formiguero_cy)
            formigas.append(nova_formiga)
            energia_colonia -= CUSTO_NOVA_FORMIGA
        f.draw(DISPLAYSURF)

    for c in comidas:
        c.draw(DISPLAYSURF)
    
    font = pygame.font.SysFont(None, 24)
    texto = font.render(f'Energia: {energia_colonia}', True, (0, 0, 0))
    proxima = max(0, CUSTO_NOVA_FORMIGA - energia_colonia)
    texto1 = font.render(f'Faltam {proxima} para nova formiga', True, (0, 0, 0))
    texto2 = font.render(f'Formigas: {len(formigas)}', True, (0, 0, 0))

    DISPLAYSURF.blit(texto, (10, 10))       # primeira linha de texto
    DISPLAYSURF.blit(texto1, (10, 30))
    DISPLAYSURF.blit(texto2, (10, 50))      # segunda linha, mais abaixo
    contador_frames += 1
    if contador_frames >= FREQUENCIA_COMIDA:
        contador_frames = 0

        if len(comidas) < MAX_COMIDAS:
            tentativas = 0
            while tentativas < 10:  # tenta no máximo 10 posições aleatórias
                comida_x = random.randint(0, cols - 1)
                comida_y = random.randint(0, rows - 1)

                # Garante que a célula não seja o formigueiro nem tenha outra comida
                if (comida_x != formiguero_cx or comida_y != formiguero_cy) and \
                all(c.cx != comida_x or c.cy != comida_y for c in comidas):
                    comidas.append(Comida(comida_x, comida_y))
                    break
                tentativas += 1


    pygame.display.update()
    clock.tick(30)
