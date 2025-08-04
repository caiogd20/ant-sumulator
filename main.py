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
cor_caminho = (210, 180, 140)  # cor areia

class Celula:
    def __init__(self, tipo="grama", comida=0, pisada=0):
        # Variações leves de verde
        self.tipo = tipo
        self.estado = "normal" 
        if tipo == "formigueiro":
            self.cor = cor_formigueiro
        else:
            self.cor = cor_grama()
        self.comida = comida
        self.pisada = pisada

    def desenhar(self, superficie, x, y):
        pygame.draw.rect(
            superficie,
            self.cor,
            (x * tamanho_celula, y * tamanho_celula, tamanho_celula, tamanho_celula)
        )
        if self.comida > 0:
            tamanho = self.comida * 2  # tamanho do círculo proporcional à quantidade de comida
            pygame.draw.circle(
                superficie,
                (255, 0, 0),  # amarelo para comida
                (x * tamanho_celula + tamanho_celula // 2, y * tamanho_celula + tamanho_celula // 2),
                tamanho
            )
        if self.pisada > 0:
            pygame.draw.circle(
                superficie,
                cor_caminho,
                (x * tamanho_celula + tamanho_celula // 2, y * tamanho_celula + tamanho_celula // 2),
                int(tamanho_celula // 4 + self.pisada * 2)
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

    def draw(self, superficie):
        centro_x = self.cx * tamanho_celula + tamanho_celula // 2
        centro_y = self.cy * tamanho_celula + tamanho_celula // 2
        pygame.draw.circle(superficie, self.color, (centro_x, centro_y), 5)
        if self.carregando_comida:
            pygame.draw.circle(superficie, (255, 0, 0), (centro_x, centro_y), 2)

    def move(self):
        self.frame_delay += 1
        if self.frame_delay >= 5:
            self.frame_delay = 0
            if self.carregando_comida:
                self.ir_para(self.formigueiro_cx, self.formigueiro_cy)
            else:
                comida_adjacente = self.detectar_comida_adjacente()
                if comida_adjacente:
                    self.ir_para(*comida_adjacente)
                else:
                    dx = random.randint(-1, 1)
                    dy = random.randint(-1, 1)

                    novo_cx = max(0, min(self.cx + dx, cols - 1))
                    novo_cy = max(0, min(self.cy + dy, rows - 1))
                    celula = grade[novo_cy][novo_cx]
                    if celula.tipo == "grama":
                        celula.pisada += 1  # aumenta o pisada da célula
                    self.cx = novo_cx
                    self.cy = novo_cy
    def tentar_coletar_comida(self):
       if not self.carregando_comida:
            celula = grade[self.cy][self.cx]
            if celula.comida > 0:
                celula.comida -= 1
                self.carregando_comida = True
                return True
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
    def detectar_comida_adjacente(self):
        # Verifica se há comida na célula adijacentes
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                novo_cx = self.cx + dx
                novo_cy = self.cy + dy
                if 0 <= novo_cx < cols and 0 <= novo_cy < rows:
                    celula = grade[novo_cy][novo_cx]
                    cordenadas = (novo_cx, novo_cy)
                    if celula.comida > 0:
                        return cordenadas  # retorna a célula com comida
        return None  # se não encontrar comida, retorna None
                        





# ----- PYGAME SETUP -----
pygame.init()
DISPLAYSURF = pygame.display.set_mode((largura, altura))
pygame.display.set_caption('Simulador de Formigueiro')
clock = pygame.time.Clock()


black = (0, 0, 0)
CUSTO_NOVA_FORMIGA = 5
LIMITE_FORMIGAS = 50
FREQUENCIA_COMIDA = 120  # a cada 120 frames (~4 segundos com 30 FPS)
MAX_COMIDAS = 50
contador_frames = 0
contador_pisadas = 0

pygame.mouse.set_visible(False)

formigas = []
for i in range(1):
    formigas.append(Formiga(formiguero_cx, formiguero_cy, black, formiguero_cx, formiguero_cy))
for i in range(5):
    comida_x = random.randint(0, cols - 1)
    comida_y = random.randint(0, rows - 1)
    quanntidade_comida = random.randint(1, 3)  # quantidade de comida entre 1 e 3
    grade[comida_y][comida_x].comida += quanntidade_comida
energia_colonia = 0


# ----- LOOP PRINCIPAL -----
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    contador_pisadas += 1
    if contador_pisadas >= 5:  # controla a frequência de "crescimento"
        contador_pisadas = 0
        for linha in grade:
            for celula in linha:
                if celula.pisada > 0:
                    celula.pisada = max(0, celula.pisada - 0.1)
    # Desenha cada célula da grade
    for y in range(rows):
        for x in range(cols):
            grade[y][x].desenhar(DISPLAYSURF, x, y)



    # Mover e desenhar as formigas
    for f in formigas:
        f.move()
        f.tentar_coletar_comida()
        if f.tentar_entregar_comida(formiguero_cx, formiguero_cy):
            energia_colonia += 1
        if energia_colonia >= CUSTO_NOVA_FORMIGA and len(formigas) < LIMITE_FORMIGAS:
            nova_formiga = Formiga(formiguero_cx, formiguero_cy, black, formiguero_cx, formiguero_cy)
            formigas.append(nova_formiga)
            energia_colonia -= CUSTO_NOVA_FORMIGA
        f.draw(DISPLAYSURF)

    

    font = pygame.font.SysFont(None, 24)
    texto = font.render(f'Energia: {energia_colonia}', True, (0, 0, 0))
    proxima = max(0, CUSTO_NOVA_FORMIGA - energia_colonia)
    texto1 = font.render(f'Faltam {proxima} para nova formiga', True, (0, 0, 0))
    texto2 = font.render(f'Formigas: {len(formigas)}', True, (0, 0, 0))
    texto3 = font.render(f'Comida total: {sum(c.comida for row in grade for c in row)}', True, (0, 0, 0))
    texto4 = font.render(f'Comida máxima: {MAX_COMIDAS}', True, (0, 0, 0))

    DISPLAYSURF.blit(texto, (10, 10))       # primeira linha de texto
    DISPLAYSURF.blit(texto1, (10, 30))
    DISPLAYSURF.blit(texto2, (10, 50))      # segunda linha, mais abaixo
    DISPLAYSURF.blit(texto3, (10, 70))      # terceira linha, mais abaixo
    DISPLAYSURF.blit(texto4, (10, 90))
    contador_frames += 1
    if contador_frames >= FREQUENCIA_COMIDA:
        contador_frames = 0
        
        total_comida = sum(c.comida for row in grade for c in row)
        if total_comida < MAX_COMIDAS:
            tentativas = 0
            while tentativas < 10:  # tenta no máximo 10 posições aleatórias
                comida_x = random.randint(0, cols - 1)
                comida_y = random.randint(0, rows - 1)

                # Garante que a célula não seja o formigueiro e não tenha sido pisada
                if (comida_x != formiguero_cx or comida_y != formiguero_cy) and grade[comida_y][comida_x].tipo == "grama" and grade[comida_y][comida_x].comida == 0:
                    quanntidade_comida = random.randint(1, 3)  # quantidade de comida entre 1 e 3
                    grade[comida_y][comida_x].comida += quanntidade_comida
                    #comidas.append(Comida(comida_x, comida_y))
                    break
                tentativas += 1


    pygame.display.update()
    clock.tick(30)