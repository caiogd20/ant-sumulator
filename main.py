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
        elif tipo == "fonte_comida":
            self.cor = (180, 120, 0)  # uma cor diferente, como marrom-amarelada
        else:
            self.cor = cor_grama()
        self.comida = comida
        self.pisada = pisada
        self.timer_gerar_comida = 0
        self.feromonio = 0.0  # inicializa o feromônio

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
            raio = min(tamanho_celula // 2 - 2, int(self.pisada * 2))
            pygame.draw.circle(
                superficie,
                cor_caminho,
                (x * tamanho_celula + tamanho_celula // 2, y * tamanho_celula + tamanho_celula // 2),
                raio
            )
        if self.feromonio > 0:
            intensidade = min(255, int(self.feromonio * 10))
            cor = (0, 0, intensidade)
            s = pygame.Surface((tamanho_celula, tamanho_celula))
            s.set_alpha(80)
            s.fill(cor)
            superficie.blit(s, (x * tamanho_celula, y * tamanho_celula))



# Inicializa a grade com células do tipo "grama"
grade = [[Celula() for _ in range(cols)] for _ in range(rows)]
# Define posição central para o formigueiro
formiguero_cx = cols // 2
formiguero_cy = rows // 2
# Define a célula do formigueiro
grade[formiguero_cy][formiguero_cx] = Celula(tipo="formigueiro")

# ----- FORMIGA -----
def tem_formiga_em(cx, cy, formigas):
    return any(f.cx == cx and f.cy == cy for f in formigas)
class Formiga:
    def __init__(self, cx, cy , color, formigueiro_cx, formigueiro_cy):
        self.cx = cx
        self.cy = cy
        self.color = color
        self.carregando_comida = False
        self.frame_delay = 0
        self.formigueiro_cx = formigueiro_cx
        self.formigueiro_cy = formigueiro_cy
        self.estado = "normal"  # estado inicial da formiga
        # o etado não é usado no momento, mas pode ser útil para futuras implementações
        self.idade = 0  # idade da formiga, pode ser usado para simular envelhecimento ou morte
        self.viva = True  # estado de vida da formiga, pode ser usado para simular morte 

    def draw(self, superficie):
        centro_x = self.cx * tamanho_celula + tamanho_celula // 2
        centro_y = self.cy * tamanho_celula + tamanho_celula // 2
        envelhecimento = min(255, int((self.idade / MAX_IDADE) * 200))
        cor_desbotada = (envelhecimento, envelhecimento, envelhecimento)
        pygame.draw.circle(superficie, cor_desbotada, (centro_x, centro_y), 5)
        if self.carregando_comida:
            pygame.draw.circle(superficie, (255, 0, 0), (centro_x, centro_y), 2)

    def move(self):
        self.frame_delay += 1
        if self.frame_delay >= 5:
            self.frame_delay = 0
            self.idade += 1  # aumenta a idade da formiga a cada movimento
            if self.carregando_comida:
                self.ir_para(self.formigueiro_cx, self.formigueiro_cy)
                if (self.cx != self.formigueiro_cx or
                        self.cy != self.formigueiro_cy):
                    celula = grade[self.cy][self.cx]
                    celula.feromonio += 5.0
            else:
                comida_adjacente = self.detectar_comida_adjacente()
                if comida_adjacente:
                    self.ir_para(*comida_adjacente)
                else:
                    melhor_opcao = (self.cx, self.cy)
                    melhor_opcao = None
                    maior_distancia = -1

                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            if dx == 0 and dy == 0:
                                continue
                            nx = self.cx + dx
                            ny = self.cy + dy
                            if 0 <= nx < cols and 0 <= ny < rows:
                                cel = grade[ny][nx]
                                if cel.feromonio > 0 and not tem_formiga_em(nx, ny, formigas):
                                    distancia = abs(nx - self.formigueiro_cx) + abs(ny - self.formigueiro_cy)
                                    if distancia > maior_distancia:
                                        maior_distancia = distancia
                                        melhor_opcao = (nx, ny)
                    # Aplica movimento
                    if melhor_opcao:
                        self.cx, self.cy = melhor_opcao
                    else:
                        # Movimento aleatório se não encontrar feromônio
                        tentativas = 0
                        while tentativas < 10:
                            dx = random.randint(-1, 1)
                            dy = random.randint(-1, 1)
                            novo_cx = max(0, min(self.cx + dx, cols - 1))
                            novo_cy = max(0, min(self.cy + dy, rows - 1))
                            if not tem_formiga_em(novo_cx, novo_cy, formigas):
                                self.cx = novo_cx
                                self.cy = novo_cy
                                break
                            

    # Tenta coletar comida se não estiver carregando
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
        celula = grade[novo_cy][novo_cx]
        if celula.tipo == "grama":
            celula.pisada += 5  # aumenta o pisada da célula

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
    def morrer(self):
        self.viva = False
        if self.carregando_comida:
            celula = grade[self.cy][self.cx]
            celula.comida += 1
    def verificar_idade(self, max_idade):
        if self.idade >= max_idade:
            self.morrer() 
                        





# ----- PYGAME SETUP -----
pygame.init()
DISPLAYSURF = pygame.display.set_mode((largura, altura))
pygame.display.set_caption('Simulador de Formigueiro')
clock = pygame.time.Clock()


black = (0, 0, 0)
CUSTO_NOVA_FORMIGA = 5
LIMITE_FORMIGAS = 10
MAX_IDADE = 3000  # por exemplo, 3000 frames = 100 segundos a 30 FPS
FREQUENCIA_COMIDA = 120  # a cada 120 frames (~4 segundos com 30 FPS)
contador_frames = 0
contador_pisadas = 0
energia_colonia = 0  # energia inicial da colônia

pygame.mouse.set_visible(False)

formigas = []
for i in range(5):  # cria 5 formigas iniciais
    formigas.append(Formiga(formiguero_cx, formiguero_cy, black, formiguero_cx, formiguero_cy))
fonte_comida = random.randint(0, 3)
if fonte_comida == 0:
    grade[0][0] = Celula(tipo="fonte_comida")  # canto superior esquerdo
elif fonte_comida == 1:
    grade[0][cols - 1] = Celula(tipo="fonte_comida")  # canto superior direito
elif fonte_comida == 2:
    grade[rows - 1][0] = Celula(tipo="fonte_comida")  # canto inferior esquerdo
else:
    grade[rows - 1][cols - 1] = Celula(tipo="fonte_comida")  # canto inferior direito  # substitui uma célula aleatória por uma fonte de comida



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
                if celula.feromonio > 0:
                    celula.feromonio = max(0, celula.feromonio - 0.1)
    # Desenha cada célula da grade
    for y in range(rows):
        for x in range(cols):
            grade[y][x].desenhar(DISPLAYSURF, x, y)
            celula = grade[y][x]

            # Se for uma fonte de comida
            if celula.tipo == "fonte_comida":
                celula.timer_gerar_comida += 1
                if celula.timer_gerar_comida >= 60:  # a cada 2 segundos (30 FPS)
                    celula.timer_gerar_comida = 0

                    # Tenta gerar comida em volta
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            if dx == 0 and dy == 0:
                                continue
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < cols and 0 <= ny < rows:
                                vizinha = grade[ny][nx]
                                if vizinha.tipo == "grama" and vizinha.comida == 0:
                                    vizinha.comida = 3  # valor inicial da comida
                                    break  # só gera uma por ciclo



    # Mover e desenhar as formigas
    formigas_vivas = []
    for f in formigas:
        f.move()
        f.tentar_coletar_comida()
        if f.tentar_entregar_comida(formiguero_cx, formiguero_cy):
            energia_colonia += 1
        if energia_colonia >= CUSTO_NOVA_FORMIGA and len(formigas) < LIMITE_FORMIGAS:
            nova_formiga = Formiga(formiguero_cx, formiguero_cy, black, formiguero_cx, formiguero_cy)
            formigas.append(nova_formiga)
            energia_colonia -= CUSTO_NOVA_FORMIGA

        f.verificar_idade(MAX_IDADE)
        if f.viva:
            f.draw(DISPLAYSURF)
            formigas_vivas.append(f)
    formigas = formigas_vivas  # atualiza a lista de formigas para manter apenas as vivas


    

    font = pygame.font.SysFont(None, 24)
    texto = font.render(f'Energia: {energia_colonia}', True, (0, 0, 0))
    proxima = max(0, CUSTO_NOVA_FORMIGA - energia_colonia)
    texto1 = font.render(f'Faltam {proxima} para nova formiga', True, (0, 0, 0))
    texto2 = font.render(f'Formigas: {len(formigas)}', True, (0, 0, 0))



    DISPLAYSURF.blit(texto, (10, 10))       # primeira linha de texto
    DISPLAYSURF.blit(texto1, (10, 30))
    DISPLAYSURF.blit(texto2, (10, 50))      # segunda linha, mais abaixo
     # terceira linha, mais abaixo
   
    

    pygame.display.update()
    clock.tick(30)