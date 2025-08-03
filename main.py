import pygame, sys
import random
from pygame.locals import QUIT

# Tamanho da tela
largura, altura = 500, 500
tamanho_celula = 20
cols = largura // tamanho_celula
rows = altura // tamanho_celula

# cor das células
cor_grama = lambda: (0, random.randint(120, 180), 0)
cor_formigueiro = (139, 69, 19)  # marrom

class Celula:
    def __init__(self, tipo="grama"):
        self.tipo = tipo
        self.estado = "normal"
        self.feromonio = 0.0
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
        if self.feromonio > 0:
            intensidade = min(255, int(self.feromonio * 10))
            cor = (0, 0, intensidade)
            s = pygame.Surface((tamanho_celula, tamanho_celula))
            s.set_alpha(80)
            s.fill(cor)
            superficie.blit(s, (x * tamanho_celula, y * tamanho_celula))

# Inicializa a grade
grade = [[Celula() for _ in range(cols)] for _ in range(rows)]
formiguero_cx = cols // 2
formiguero_cy = rows // 2
grade[formiguero_cy][formiguero_cx] = Celula(tipo="formigueiro")

class Formiga:
    def __init__(self, cx, cy, color, formigueiro_cx, formigueiro_cy):
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
            pygame.draw.circle(superficie, (255, 0, 0), (centro_x, centro_y), 3)

    
    def move(self):
        self.frame_delay += 1
        if self.frame_delay >= 5:
            self.frame_delay = 0

            if self.carregando_comida:
                self.ir_para(self.formigueiro_cx, self.formigueiro_cy)
                if self.cx != self.formigueiro_cx or self.cy != self.formigueiro_cy:
                    grade[self.cy][self.cx].feromonio += 1.0
            else:
                melhor_opcao = None
                melhor_valor = -1
                distancia_atual = abs(self.cx - self.formigueiro_cx) + abs(self.cy - self.formigueiro_cy)
                feromonio_local = grade[self.cy][self.cx].feromonio

                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = self.cx + dx, self.cy + dy
                        if 0 <= nx < cols and 0 <= ny < rows:
                            valor = grade[ny][nx].feromonio
                            distancia_nova = abs(nx - self.formigueiro_cx) + abs(ny - self.formigueiro_cy)

                            if feromonio_local > 0:
                                # Evita voltar para o formigueiro se estiver em trilha
                                if valor > melhor_valor and distancia_nova > distancia_atual:
                                    melhor_valor = valor
                                    melhor_opcao = (nx, ny)
                            else:
                                if valor > melhor_valor:
                                    melhor_valor = valor
                                    melhor_opcao = (nx, ny)

                if melhor_opcao:
                    self.cx, self.cy = melhor_opcao
                else:
                    # Movimento aleatório
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

    def tentar_entregar_comida(self, formigueiro_cx, formigueiro_cy):
        if self.carregando_comida and self.cx == formigueiro_cx and self.cy == formigueiro_cy:
            self.carregando_comida = False
            return True
        return False

    def ir_para(self, destino_cx, destino_cy):
        dx = dy = 0
        if self.cx < destino_cx:
            dx = 1
        elif self.cx > destino_cx:
            dx = -1
        if self.cy < destino_cy:
            dy = 1
        elif self.cy > destino_cy:
            dy = -1
        self.cx = max(0, min(self.cx + dx, cols - 1))
        self.cy = max(0, min(self.cy + dy, rows - 1))

class Comida:
    def __init__(self, cx, cy):
        self.cx = cx
        self.cy = cy

    def draw(self, superficie):
        centro_x = self.cx * tamanho_celula + tamanho_celula // 2
        centro_y = self.cy * tamanho_celula + tamanho_celula // 2
        pygame.draw.circle(superficie, (255, 0, 0), (centro_x, centro_y), 3)

pygame.init()
DISPLAYSURF = pygame.display.set_mode((largura, altura))
pygame.display.set_caption('Simulador de Formigueiro')
clock = pygame.time.Clock()

black = (0, 0, 0)
CUSTO_NOVA_FORMIGA = 5
LIMITE_FORMIGAS = 50
FREQUENCIA_COMIDA = 120
MAX_COMIDAS = 15
contador_frames = 0

pygame.mouse.set_visible(False)
formigas = [Formiga(formiguero_cx, formiguero_cy, black, formiguero_cx, formiguero_cy) for _ in range(5)]
comidas = [Comida(random.randint(0, cols - 1), random.randint(0, rows - 1)) for _ in range(5)]
energia_colonia = 0

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    for linha in grade:
        for celula in linha:
            celula.feromonio = max(0, celula.feromonio - 0.01)

    for y in range(rows):
        for x in range(cols):
            grade[y][x].desenhar(DISPLAYSURF, x, y)

    for f in formigas:
        f.move()
        f.tentar_coletar_comida(comidas)
        if f.tentar_entregar_comida(formiguero_cx, formiguero_cy):
            energia_colonia += 1
        if energia_colonia >= CUSTO_NOVA_FORMIGA and len(formigas) < LIMITE_FORMIGAS:
            formigas.append(Formiga(formiguero_cx, formiguero_cy, black, formiguero_cx, formiguero_cy))
            energia_colonia -= CUSTO_NOVA_FORMIGA
        f.draw(DISPLAYSURF)

    for c in comidas:
        c.draw(DISPLAYSURF)

    font = pygame.font.SysFont(None, 24)
    DISPLAYSURF.blit(font.render(f'Energia: {energia_colonia}', True, (0, 0, 0)), (10, 10))
    DISPLAYSURF.blit(font.render(f'Faltam {max(0, CUSTO_NOVA_FORMIGA - energia_colonia)} para nova formiga', True, (0, 0, 0)), (10, 30))
    DISPLAYSURF.blit(font.render(f'Formigas: {len(formigas)}', True, (0, 0, 0)), (10, 50))

    contador_frames += 1
    if contador_frames >= FREQUENCIA_COMIDA:
        contador_frames = 0
        if len(comidas) < MAX_COMIDAS:
            tentativas = 0
            while tentativas < 10:
                comida_x = random.randint(0, cols - 1)
                comida_y = random.randint(0, rows - 1)
                if (comida_x != formiguero_cx or comida_y != formiguero_cy) and \
                   all(c.cx != comida_x or c.cy != comida_y for c in comidas):
                    comidas.append(Comida(comida_x, comida_y))
                    break
                tentativas += 1

    pygame.display.update()
    clock.tick(30)
