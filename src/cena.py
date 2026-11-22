from manim import *
from manim_slides import Slide
from pathlib import Path
import json
import numpy as np

# Cada classe é um bloco da apresentação.
# Cada self.next_slide() é uma pausa, a apresentação só continua
# quando você aperta a seta ou a barra de espaço.


# ---------------------------------------------------------------------
# Cores (fundo preto e fonte padrão do Manim)
# ---------------------------------------------------------------------
COR_TEXTO = WHITE
COR_SUAVE = GRAY_B           # cinza pra eixos, setas e textos de apoio
COR_CERTO = GREEN            # "deu certo"
COR_DESTAQUE = YELLOW        # retas, padrões e respostas
COR_NORMAL = BLUE            # pedidos normais
COR_ESTRANHO = ORANGE        # pedidos estranhos ou atrasados
COR_PLATEIA = RED            # vermelho, SÓ pra etiqueta PLATEIA
COR_LILAS = PURPLE_A         # cor extra pro modelo A da pergunta 6

LADO_DIREITO = RIGHT * 3.8   # coluna de textos do lado direito da tela

# A logo tem que estar na mesma pasta deste arquivo
PASTA = Path(__file__).parent
LOGO_UEL = str(PASTA / "uel_negativo.png")

# Resultados reais da Olist, gerados pelo analise_olist.py (mesma pasta)
with open(PASTA / "resultados_olist.json", encoding="utf-8") as arquivo:
    RES = json.load(arquivo)

Text.set_default(color=COR_TEXTO)
Paragraph.set_default(color=COR_TEXTO)
Arrow.set_default(color=COR_SUAVE)
Dot.set_default(radius=0.1)
Axes.set_default(axis_config={"color": COR_SUAVE, "tip_width": 0.18, "tip_height": 0.18})

# Velocidade das animações, em segundos (quanto menor, mais rápido)
FadeIn.set_default(run_time=0.5)
FadeOut.set_default(run_time=0.4)
Write.set_default(run_time=0.9)
Create.set_default(run_time=0.8)
GrowArrow.set_default(run_time=0.6)
DrawBorderThenFill.set_default(run_time=0.8)
GrowFromEdge.set_default(run_time=0.7)
ReplacementTransform.set_default(run_time=0.6)
TransformFromCopy.set_default(run_time=1.0)


def titulo_slide(texto):
    # Título simples, centralizado no topo
    titulo = Text(texto, font_size=28)
    titulo.to_edge(UP)
    return titulo


def caixa_plateia(texto):
    # Etiqueta vermelha PLATEIA com a pergunta embaixo
    etiqueta = Text("PLATEIA", font_size=22, weight=BOLD, color=WHITE)
    fundo = RoundedRectangle(
        corner_radius=0.12,
        width=etiqueta.width + 0.5,
        height=etiqueta.height + 0.3,
        fill_color=COR_PLATEIA,
        fill_opacity=1,
        stroke_width=0,
    )
    etiqueta.move_to(fundo.get_center())
    selo = VGroup(fundo, etiqueta)

    pergunta = Text(texto, font_size=22)
    pergunta.next_to(selo, DOWN, buff=0.25)
    return VGroup(selo, pergunta)


def perguntar_plateia(cena, texto, posicao):
    # Mostra a pergunta e deixa a etiqueta balançando em loop
    # até você apertar a seta pra revelar a resposta
    caixa = caixa_plateia(texto)
    caixa.move_to(posicao)
    cena.play(FadeIn(caixa, shift=DOWN * 0.3))
    cena.next_slide(loop=True)
    cena.play(Wiggle(caixa[0], scale_value=1.2))
    cena.next_slide()
    return caixa


def com_virgula(numero, casas=2):
    # 0.26 vira "0,26" e 95343 vira "95.343", do jeito que a gente escreve
    texto = f"{numero:,.{casas}f}"
    texto = texto.replace(",", "#").replace(".", ",").replace("#", ".")
    return texto


NOMES_MES = {"01": "jan", "02": "fev", "03": "mar", "04": "abr", "05": "mai", "06": "jun",
             "07": "jul", "08": "ago", "09": "set", "10": "out", "11": "nov", "12": "dez"}


def mes_curto(ano_mes):
    # "2017-11" vira "nov/17"
    return NOMES_MES[ano_mes[5:7]] + "/" + ano_mes[2:4]


# =====================================================================
# ABERTURA
# =====================================================================
class Introducao(Slide):
    def construct(self):
        # Capa: logo da UEL, disciplina e nomes, tudo centralizado
        logo = ImageMobject(LOGO_UEL)
        logo.height = 2.2
        logo.move_to(UP * 1.5)

        disciplina = Text("Redes Neurais I", font_size=26, color=COR_SUAVE)
        autores = Text("Vinícius Yudi Oya e Leonardo Ryoichi Yakushijin Taniguti", font_size=24)
        professor = Text("Prof. Davi Pereira dos Santos", font_size=20, color=COR_SUAVE)
        disciplina.next_to(logo, DOWN, buff=0.6)
        autores.next_to(disciplina, DOWN, buff=0.5)
        professor.next_to(autores, DOWN, buff=0.3)
        bloco = VGroup(disciplina, autores, professor)

        self.play(FadeIn(logo, scale=0.9))
        self.play(FadeIn(bloco))
        self.next_slide()
        self.play(FadeOut(logo), FadeOut(bloco))

        # As três perguntas do trabalho
        titulo = titulo_slide("As três perguntas")
        q1 = Text("1.  Como um neurônio artificial aprende?", font_size=24, t2c={"1.": COR_CERTO})
        q6 = Text("6.  O que acontece quando uma rede aprende além do ideal?", font_size=24, t2c={"6.": COR_CERTO})
        q16 = Text("16. Como detectar anomalias com redes neurais?", font_size=24, t2c={"16.": COR_CERTO})
        q6.next_to(q1, DOWN, buff=0.6, aligned_edge=LEFT)
        q16.next_to(q6, DOWN, buff=0.6, aligned_edge=LEFT)
        perguntas = VGroup(q1, q6, q16)
        perguntas.move_to(DOWN * 0.2)

        self.play(Write(titulo))
        self.play(FadeIn(q1, shift=UP * 0.2))
        self.play(FadeIn(q6, shift=UP * 0.2))
        self.play(FadeIn(q16, shift=UP * 0.2))
        self.next_slide()
        self.play(FadeOut(titulo), FadeOut(perguntas))

        # As 3 perguntas estão ligadas, uma leva à outra
        caixa1 = Text("Como a rede\naprende", font_size=24)
        caixa6 = Text("Quando ela\naprende demais", font_size=24)
        caixa16 = Text("Usando isso pra\nachar anomalias", font_size=24)
        caixa1.move_to(LEFT * 4.5 + UP * 0.5)
        caixa6.move_to(UP * 0.5)
        caixa16.move_to(RIGHT * 4.5 + UP * 0.5)
        borda1 = SurroundingRectangle(caixa1, buff=0.3, corner_radius=0.2, color=COR_SUAVE)
        borda6 = SurroundingRectangle(caixa6, buff=0.3, corner_radius=0.2, color=COR_SUAVE)
        borda16 = SurroundingRectangle(caixa16, buff=0.3, corner_radius=0.2, color=COR_SUAVE)
        seta_a = Arrow(borda1.get_right(), borda6.get_left())
        seta_b = Arrow(borda6.get_right(), borda16.get_left())

        self.play(Write(caixa1), Create(borda1))
        self.play(GrowArrow(seta_a), Write(caixa6), Create(borda6))
        self.play(GrowArrow(seta_b), Write(caixa16), Create(borda16))

        fio = Text("A ideia é que aquilo que a rede não conseguiu\naprender acaba entregando a anomalia", font_size=26, color=COR_DESTAQUE)
        fio.shift(DOWN * 1.8)
        self.play(Write(fio))
        self.next_slide()

        self.play(FadeOut(caixa1), FadeOut(caixa6), FadeOut(caixa16), FadeOut(borda1), FadeOut(borda6), FadeOut(borda16), FadeOut(seta_a), FadeOut(seta_b), FadeOut(fio))

        # Explica a etiqueta PLATEIA pra turma
        regra = Text("Sempre que aparecer essa etiqueta, é a vez de vocês", font_size=28)
        regra.shift(UP * 1.5)
        exemplo = caixa_plateia("dá pra responder em voz alta\nou levantando a mão")
        self.play(Write(regra))
        self.play(FadeIn(exemplo, shift=DOWN * 0.3))
        self.next_slide()
        self.play(FadeOut(regra), FadeOut(exemplo))

        # Pergunta de aquecimento
        aquecimento = perguntar_plateia(self, "Quem aqui já fez uma compra\nonline que chegou atrasada?", ORIGIN)


# =====================================================================
# OS DADOS DA OLIST
# =====================================================================
class Dados(Slide):
    def construct(self):
        titulo = titulo_slide("Os dados da Olist")
        self.play(Write(titulo))

        # O que é a Olist
        linha1 = Text("A Olist é uma empresa brasileira que ajuda", font_size=22)
        linha2 = Text("lojas pequenas a vender nos grandes marketplaces", font_size=22)
        linha3 = Text("Ela liberou no Kaggle uma base com cerca de 100 mil", font_size=22)
        linha4 = Text("pedidos reais, feitos entre 2016 e 2018", font_size=22)
        linha5 = Text("São 8 tabelas, com pedidos, itens, pagamentos, avaliações,", font_size=22)
        linha6 = Text("clientes, vendedores, produtos e localização", font_size=22)
        linha2.next_to(linha1, DOWN, buff=0.15)
        linha3.next_to(linha2, DOWN, buff=0.5)
        linha4.next_to(linha3, DOWN, buff=0.15)
        linha5.next_to(linha4, DOWN, buff=0.5)
        linha6.next_to(linha5, DOWN, buff=0.15)
        sobre = VGroup(linha1, linha2, linha3, linha4, linha5, linha6)
        sobre.move_to(DOWN * 0.2)
        self.play(FadeIn(linha1), FadeIn(linha2))
        self.play(FadeIn(linha3), FadeIn(linha4))
        self.play(FadeIn(linha5), FadeIn(linha6))
        self.next_slide()
        self.play(FadeOut(sobre))

        # Antes de mostrar as variáveis, a turma dá palpite
        brainstorm = perguntar_plateia(self, "Se vocês fossem a loja, o que olhariam\npra desconfiar de um pedido?", ORIGIN)
        self.play(FadeOut(brainstorm))

        # Um pedido de verdade da base, bem avaliado e bem comum
        tipico = RES["pedido_tipico"]
        cartao_texto = Paragraph(
            "Um pedido da base",
            "prometido pra " + str(tipico["prazo_prometido"]) + " dias",
            "entregue em " + str(tipico["prazo_real"]) + " dias",
            "produto de R$ " + com_virgula(tipico["preco"]),
            "frete de R$ " + com_virgula(tipico["frete"]),
            "pesa " + com_virgula(tipico["peso"], 0) + " g",
            "volume de " + com_virgula(tipico["volume"], 0) + " cm³",
            "cliente a " + com_virgula(tipico["distancia"], 0) + " km",
            "pago em " + str(tipico["parcelas"]) + "x",
            alignment="left",
            font_size=20,
            line_spacing=0.8,
        )
        cartao_texto.move_to(LEFT * 4.3 + DOWN * 0.5)
        cartao = SurroundingRectangle(cartao_texto, buff=0.3, corner_radius=0.2, color=COR_SUAVE)
        self.play(Create(cartao), Write(cartao_texto))
        self.next_slide()

        # As 10 variáveis que entram na rede (as mesmas da tabela do Leonardo)
        tabela = Table(
            [
                [str(tipico["prazo_prometido"]), "prazo prometido (dias)"],
                [str(tipico["prazo_real"]), "prazo real (dias)"],
                [str(tipico["diferenca"]), "diferença entre os dois"],
                [com_virgula(tipico["preco"]), "preço (R$)"],
                [com_virgula(tipico["frete"]), "frete (R$)"],
                [com_virgula(tipico["frete_preco"]), "frete dividido pelo preço"],
                [str(tipico["peso"]), "peso (g)"],
                [str(tipico["volume"]), "volume (cm³)"],
                [str(tipico["distancia"]), "distância até o vendedor (km)"],
                [str(tipico["parcelas"]), "parcelas"],
            ],
            include_inner_lines=False,
            v_buff=0.22,
            h_buff=0.5,
            element_to_mobject_config={"font_size": 20},
        )
        tabela.move_to(RIGHT * 2.6 + DOWN * 0.5)
        numeros = tabela.get_columns()[0]
        numeros.set_color(COR_DESTAQUE)
        vetor = SurroundingRectangle(numeros, buff=0.15, color=COR_DESTAQUE)
        seta = Arrow(cartao.get_right(), vetor.get_left())

        self.play(GrowArrow(seta))
        self.play(TransformFromCopy(cartao_texto, tabela), Create(vetor))
        frase = Text("Pra rede, cada pedido vira uma lista de 10 números", font_size=22, color=COR_DESTAQUE)
        frase.move_to(UP * 2.6)
        self.play(Write(frase))
        self.next_slide()

        escala = Text("Antes de entrar na rede, tudo é colocado na mesma escala (média 0 e desvio 1)", font_size=18, color=COR_SUAVE)
        escala.to_edge(DOWN, buff=0.4)
        self.play(FadeIn(escala))
        self.next_slide()
        self.play(FadeOut(cartao), FadeOut(cartao_texto), FadeOut(tabela), FadeOut(vetor), FadeOut(seta), FadeOut(frase), FadeOut(escala))

        # O plano em 3 passos
        passo1 = Text("1. Treinamos só com\npedidos bem avaliados\n(nota 4 ou 5)", font_size=22)
        passo2 = Text("2. Calculamos o erro\nde reconstrução de\ntodos os pedidos", font_size=22)
        passo3 = Text("3. Vemos se o erro alto\nbate com nota 1\nou cancelamento", font_size=22)
        passo1.move_to(LEFT * 4.6)
        passo3.move_to(RIGHT * 4.6)
        borda_p1 = SurroundingRectangle(passo1, buff=0.25, corner_radius=0.2, color=COR_NORMAL)
        borda_p2 = SurroundingRectangle(passo2, buff=0.25, corner_radius=0.2, color=COR_DESTAQUE)
        borda_p3 = SurroundingRectangle(passo3, buff=0.25, corner_radius=0.2, color=COR_ESTRANHO)
        seta_p1 = Arrow(borda_p1.get_right(), borda_p2.get_left())
        seta_p2 = Arrow(borda_p2.get_right(), borda_p3.get_left())

        self.play(Write(passo1), Create(borda_p1))
        self.next_slide()
        self.play(GrowArrow(seta_p1), Write(passo2), Create(borda_p2))
        self.next_slide()
        self.play(GrowArrow(seta_p2), Write(passo3), Create(borda_p3))

        gabarito = Text("Em nenhum momento a rede sabe o que é um pedido problemático,\nela tem que perceber isso sozinha", font_size=20, color=COR_DESTAQUE)
        gabarito.shift(DOWN * 2.2)
        contagem = Text("Foram " + com_virgula(RES["n_pedidos"], 0) + " pedidos entregues, e " + com_virgula(RES["n_treino"], 0) + " deles serviram de treino", font_size=18, color=COR_SUAVE)
        contagem.shift(UP * 2.2)
        self.play(Write(gabarito), FadeIn(contagem))
        self.next_slide()
        self.play(FadeOut(passo1), FadeOut(passo2), FadeOut(passo3), FadeOut(borda_p1), FadeOut(borda_p2), FadeOut(borda_p3), FadeOut(seta_p1), FadeOut(seta_p2), FadeOut(gabarito), FadeOut(contagem))

        # O que vamos medir
        subtitulo = Text("O que vamos medir", font_size=26, color=COR_DESTAQUE)
        metrica1 = Text("• o erro de reconstrução (MSE) de cada pedido", font_size=22)
        metrica2 = Text("• se o erro passa de um limite τ, o pedido gera um alerta\n   (τ é o erro que só 1% dos pedidos de treino ultrapassa)", font_size=22)
        metrica3 = Text("• depois vemos se os alertas têm mais nota 1 do que a média", font_size=22)
        metrica4 = Text("• e se eles aumentam na Black Friday de 2017 e na greve de 2018", font_size=22)
        metrica1.next_to(subtitulo, DOWN, buff=0.6, aligned_edge=LEFT)
        metrica2.next_to(metrica1, DOWN, buff=0.4, aligned_edge=LEFT)
        metrica3.next_to(metrica2, DOWN, buff=0.4, aligned_edge=LEFT)
        metrica4.next_to(metrica3, DOWN, buff=0.4, aligned_edge=LEFT)
        metricas = VGroup(subtitulo, metrica1, metrica2, metrica3, metrica4)
        metricas.move_to(DOWN * 0.3)

        self.play(Write(subtitulo))
        self.play(FadeIn(metrica1))
        self.next_slide()
        self.play(FadeIn(metrica2))
        self.next_slide()
        self.play(FadeIn(metrica3))
        self.next_slide()
        self.play(FadeIn(metrica4))


# =====================================================================
# PERGUNTA 1 - Como um neurônio artificial aprende?
# =====================================================================
class Pergunta1(Slide):
    def construct(self):
        titulo = titulo_slide("1. Como um neurônio artificial aprende?")
        self.play(Write(titulo))

        # Desenho do neurônio
        entrada1 = Text("distância", font_size=20)
        entrada2 = Text("volume do produto", font_size=20)
        entrada1.move_to(LEFT * 4.5 + UP * 1)
        entrada2.move_to(LEFT * 4.5 + DOWN * 1)

        neuronio = Circle(radius=0.6, color=COR_NORMAL)
        simbolo = Text("Σ", font_size=36)
        simbolo.move_to(neuronio.get_center())

        saida = Text("vai atrasar?", font_size=20)
        saida.move_to(RIGHT * 3.7)

        seta1 = Arrow(entrada1.get_right(), neuronio.get_left())
        seta2 = Arrow(entrada2.get_right(), neuronio.get_left())
        seta3 = Arrow(neuronio.get_right(), saida.get_left())
        peso1 = Text("w1", font_size=20, color=COR_DESTAQUE).next_to(seta1.get_center(), UP, buff=0.15)
        peso2 = Text("w2", font_size=20, color=COR_DESTAQUE).next_to(seta2.get_center(), DOWN, buff=0.15)

        self.play(FadeIn(entrada1), FadeIn(entrada2), GrowArrow(seta1), GrowArrow(seta2), FadeIn(peso1), FadeIn(peso2))
        self.play(Create(neuronio), FadeIn(simbolo), GrowArrow(seta3), FadeIn(saida))

        conta = Text("Ele multiplica cada entrada pelo seu peso, soma tudo e,\nse passar de um limite, diz que o pedido vai atrasar", font_size=20, color=COR_SUAVE)
        conta.to_edge(DOWN, buff=0.6)
        self.play(Write(conta))
        self.next_slide()

        self.play(
            FadeOut(entrada1), FadeOut(entrada2), FadeOut(neuronio), FadeOut(simbolo),
            FadeOut(saida), FadeOut(seta1), FadeOut(seta2), FadeOut(seta3),
            FadeOut(peso1), FadeOut(peso2), FadeOut(conta)
        )

        # Pedidos no plano (pontos de exemplo)
        eixos = Axes(x_range=[0, 10, 1], y_range=[0, 10, 1], x_length=5.2, y_length=5.2)
        eixos.shift(DOWN * 0.5 + LEFT * 2)
        rotulo_x = Text("distância", font_size=20, color=COR_SUAVE).next_to(eixos.x_axis, DOWN)
        rotulo_y = Text("volume", font_size=20, color=COR_SUAVE).rotate(PI / 2).next_to(eixos.y_axis, LEFT)
        self.play(Create(eixos), Write(rotulo_x), Write(rotulo_y))

        # verde chegou no prazo, laranja atrasou
        verde1 = Dot(eixos.c2p(1, 1), color=COR_CERTO)
        verde2 = Dot(eixos.c2p(2, 1), color=COR_CERTO)
        verde3 = Dot(eixos.c2p(1, 2), color=COR_CERTO)
        verde4 = Dot(eixos.c2p(3, 2), color=COR_CERTO)
        verde5 = Dot(eixos.c2p(2, 3), color=COR_CERTO)
        laranja1 = Dot(eixos.c2p(6, 6), color=COR_ESTRANHO)
        laranja2 = Dot(eixos.c2p(7, 5), color=COR_ESTRANHO)
        laranja3 = Dot(eixos.c2p(8, 7), color=COR_ESTRANHO)
        laranja4 = Dot(eixos.c2p(5, 8), color=COR_ESTRANHO)
        laranja5 = Dot(eixos.c2p(7, 8), color=COR_ESTRANHO)
        verdes = VGroup(verde1, verde2, verde3, verde4, verde5)
        laranjas = VGroup(laranja1, laranja2, laranja3, laranja4, laranja5)
        legenda = Text("● no prazo   ● atrasou", font_size=18, t2c={"● no prazo": COR_CERTO, "● atrasou": COR_ESTRANHO})
        legenda.next_to(eixos, UP, buff=0.1)
        self.play(FadeIn(verdes), FadeIn(laranjas), FadeIn(legenda))

        # A reta é o que o neurônio "acha", abaixo dela chega no prazo e acima atrasa.
        # O ValueTracker guarda a altura da reta, que é o que o neurônio vai ajustando.
        altura = ValueTracker(3)

        def desenhar_reta():
            b = altura.get_value()
            return Line(eixos.c2p(0, b), eixos.c2p(b, 0), color=COR_DESTAQUE, stroke_width=5)

        reta = always_redraw(desenhar_reta)
        self.play(Create(reta))

        # Marca os 2 pontos verdes que estão do lado errado
        erro_a = Circle(radius=0.22, color=COR_TEXTO).move_to(verde4.get_center())
        erro_b = Circle(radius=0.22, color=COR_TEXTO).move_to(verde5.get_center())
        self.play(Create(erro_a), Create(erro_b))

        pergunta = perguntar_plateia(self, "Pra acertar esses dois pontos,\na reta deveria subir ou descer?", LADO_DIREITO + UP * 1)
        self.play(altura.animate.set_value(4.5), run_time=1.5)
        self.play(FadeOut(pergunta))

        pergunta2 = perguntar_plateia(self, "E agora, ainda falta subir?", LADO_DIREITO + UP * 1)
        self.play(altura.animate.set_value(7), FadeOut(erro_a), FadeOut(erro_b), run_time=1.5)
        acertou = Text("Agora sim, separou\nos dois grupos", font_size=24, color=COR_CERTO)
        acertou.move_to(LADO_DIREITO + UP * 1)
        self.play(ReplacementTransform(pergunta2, acertou))
        self.next_slide()

        # A regra que o neurônio usa
        explicacao = Text("Quando erra, ele ajusta um pouco\nos pesos, e quando acerta,\ndeixa tudo como está", font_size=20)
        explicacao.move_to(LADO_DIREITO + DOWN * 0.6)
        regra = Text("peso novo = peso + taxa × erro × entrada", font_size=18, color=COR_DESTAQUE)
        regra.next_to(explicacao, DOWN, buff=0.5)
        self.play(Write(explicacao))
        self.play(Write(regra))
        self.next_slide()

        # O neurônio fazendo sozinho, época por época
        sozinho = Text("Agora o neurônio\nfazendo sozinho", font_size=24)
        sozinho.move_to(acertou.get_center())
        self.play(ReplacementTransform(acertou, sozinho), altura.animate.set_value(3))
        self.play(altura.animate.set_value(4), run_time=0.5)
        self.play(altura.animate.set_value(5), run_time=0.5)
        self.play(altura.animate.set_value(6), run_time=0.5)
        self.play(altura.animate.set_value(7), run_time=0.5)
        self.next_slide()

        self.play(FadeOut(*self.mobjects))

        # Na nossa rede, o erro foi caindo a cada época (curva real do treino)
        titulo2 = titulo_slide("Na nossa rede, o erro foi caindo a cada época")
        self.play(Write(titulo2))

        eixos2 = Axes(x_range=[0, 40, 10], y_range=[0, 0.8, 0.2], x_length=6, y_length=4.3)
        eixos2.shift(DOWN * 0.5 + LEFT * 2)
        rotulo_x2 = Text("época", font_size=20, color=COR_SUAVE).next_to(eixos2.x_axis, DOWN)
        rotulo_y2 = Text("erro", font_size=20, color=COR_SUAVE).rotate(PI / 2).next_to(eixos2.y_axis, LEFT)
        self.play(Create(eixos2), Write(rotulo_x2), Write(rotulo_y2))

        pergunta3 = perguntar_plateia(self, "O que vocês acham que acontece\ncom o erro a cada época?", LADO_DIREITO + UP * 1)

        erros_treino = RES["curva_treino"]
        epocas = list(range(1, len(erros_treino) + 1))
        curva = eixos2.plot_line_graph(x_values=epocas, y_values=erros_treino, line_color=COR_DESTAQUE, add_vertex_dots=False, stroke_width=5)
        self.play(Create(curva), run_time=2)
        resposta = Text("Com " + com_virgula(RES["n_treino"], 0) + " pedidos de treino,\no erro cai rápido no começo\ne depois vai caindo devagar", font_size=22, color=COR_DESTAQUE)
        resposta.move_to(LADO_DIREITO + DOWN * 1)
        self.play(Write(resposta))


# =====================================================================
# PERGUNTA 6 - O que acontece quando a rede aprende além do ideal?
# =====================================================================
class Pergunta6(Slide):
    def construct(self):
        titulo = titulo_slide("6. E se a rede aprender além do ideal?")
        self.play(Write(titulo))

        # Três modelos, em qual a turma confia?
        eixos = Axes(x_range=[0, 9, 1], y_range=[0, 10, 1], x_length=6, y_length=4.8)
        eixos.shift(DOWN * 0.5 + LEFT * 2.4)
        rotulo_x = Text("distância", font_size=20, color=COR_SUAVE).next_to(eixos.x_axis, DOWN)
        rotulo_y = Text("frete", font_size=20, color=COR_SUAVE).rotate(PI / 2).next_to(eixos.y_axis, LEFT)
        self.play(Create(eixos), Write(rotulo_x), Write(rotulo_y))

        # Pontos de treino (azul)
        x_treino = np.array([1, 2, 3, 4, 5, 6, 7, 8])
        y_treino = np.array([3.7, 3.6, 5.3, 4.9, 6.5, 5.9, 7.1, 6.0])

        treino1 = Dot(eixos.c2p(1, 3.7), color=COR_NORMAL)
        treino2 = Dot(eixos.c2p(2, 3.6), color=COR_NORMAL)
        treino3 = Dot(eixos.c2p(3, 5.3), color=COR_NORMAL)
        treino4 = Dot(eixos.c2p(4, 4.9), color=COR_NORMAL)
        treino5 = Dot(eixos.c2p(5, 6.5), color=COR_NORMAL)
        treino6 = Dot(eixos.c2p(6, 5.9), color=COR_NORMAL)
        treino7 = Dot(eixos.c2p(7, 7.1), color=COR_NORMAL)
        treino8 = Dot(eixos.c2p(8, 6.0), color=COR_NORMAL)
        pontos_treino = VGroup(treino1, treino2, treino3, treino4, treino5, treino6, treino7, treino8)
        self.play(FadeIn(pontos_treino))

        # A é uma reta, B uma curva suave e C uma curva de grau 7 que passa por todos os pontos
        coef_a = np.polyfit(x_treino, y_treino, 1)
        coef_b = np.polyfit(x_treino, y_treino, 2)
        coef_c = np.polyfit(x_treino, y_treino, 7)

        def modelo_a(x):
            return np.polyval(coef_a, x)

        def modelo_b(x):
            return np.polyval(coef_b, x)

        def modelo_c(x):
            return np.polyval(coef_c, x)

        curva_a = eixos.plot(modelo_a, x_range=[1, 8], color=COR_LILAS, stroke_width=4)
        curva_b = eixos.plot(modelo_b, x_range=[1, 8], color=COR_CERTO, stroke_width=4)
        curva_c = eixos.plot(modelo_c, x_range=[1, 8], color=COR_ESTRANHO, stroke_width=4)
        rotulo_a = Text("A", font_size=24, weight=BOLD, color=COR_LILAS).next_to(curva_a.get_end(), RIGHT)
        rotulo_b = Text("B", font_size=24, weight=BOLD, color=COR_CERTO).next_to(curva_b.get_end(), RIGHT)
        rotulo_c = Text("C", font_size=24, weight=BOLD, color=COR_ESTRANHO).next_to(curva_c.get_end(), RIGHT)

        self.play(Create(curva_a), Write(rotulo_a))
        self.play(Create(curva_b), Write(rotulo_b))
        self.play(Create(curva_c), Write(rotulo_c))

        pergunta = perguntar_plateia(self, "Em qual desses modelos\nvocês confiariam mais?", LADO_DIREITO + UP * 1.2)

        # Pontos de teste (amarelo), que o modelo nunca viu
        x_teste = np.array([1.5, 3.5, 5.5, 7.5])
        y_teste = np.array([3.8, 5.0, 6.4, 6.3])

        teste1 = Dot(eixos.c2p(1.5, 3.8), color=COR_DESTAQUE)
        teste2 = Dot(eixos.c2p(3.5, 5.0), color=COR_DESTAQUE)
        teste3 = Dot(eixos.c2p(5.5, 6.4), color=COR_DESTAQUE)
        teste4 = Dot(eixos.c2p(7.5, 6.3), color=COR_DESTAQUE)
        pontos_teste = VGroup(teste1, teste2, teste3, teste4)

        chegaram = Text("Agora chegaram pedidos\nque o modelo nunca viu", font_size=22, color=COR_DESTAQUE)
        chegaram.move_to(LADO_DIREITO + UP * 1.2)
        self.play(ReplacementTransform(pergunta, chegaram))
        self.play(FadeIn(pontos_teste, scale=2))
        self.next_slide()

        # Erro médio quadrático de cada modelo no treino e no teste
        erro_treino_b = np.mean((modelo_b(x_treino) - y_treino) ** 2)
        erro_teste_b = np.mean((modelo_b(x_teste) - y_teste) ** 2)
        erro_treino_c = np.mean((modelo_c(x_treino) - y_treino) ** 2)
        erro_teste_c = np.mean((modelo_c(x_teste) - y_teste) ** 2)

        linha_b = Text("O B erra " + com_virgula(erro_treino_b) + " no treino e " + com_virgula(erro_teste_b) + " no teste", font_size=18, color=COR_CERTO)
        linha_c = Text("O C erra " + com_virgula(erro_treino_c) + " no treino e " + com_virgula(erro_teste_c) + " no teste", font_size=18, color=COR_ESTRANHO)
        linha_b.move_to(LADO_DIREITO + RIGHT * 0.3 + DOWN * 0.2)
        linha_c.next_to(linha_b, DOWN, aligned_edge=LEFT)
        self.play(FadeOut(chegaram), Write(linha_b), Write(linha_c))
        self.next_slide()

        conclusao = Text("O C decorou os pontos de treino,\ne é isso que chamamos de overfitting", font_size=20, color=COR_ESTRANHO)
        conclusao.move_to(LADO_DIREITO + RIGHT * 0.3 + DOWN * 2)
        self.play(Write(conclusao))
        self.next_slide()
        self.play(FadeOut(*self.mobjects))

        # Treino e validação, quando parar?
        titulo2 = titulo_slide("Dá pra perceber isso durante o treino?")
        self.play(Write(titulo2))

        # Experimento real: uma rede grande tentando prever o frete
        # com só 80 pedidos de treino (parte 8 do analise_olist.py)
        eixos2 = Axes(x_range=[0, 300, 50], y_range=[0, 0.5, 0.1], x_length=6, y_length=4.3)
        eixos2.shift(DOWN * 0.5 + LEFT * 2.4)
        rotulo_x2 = Text("época", font_size=20, color=COR_SUAVE).next_to(eixos2.x_axis, DOWN)
        rotulo_y2 = Text("erro", font_size=20, color=COR_SUAVE).rotate(PI / 2).next_to(eixos2.y_axis, LEFT)
        contexto = Text("Uma rede grande tentando prever\no frete com só 80 pedidos", font_size=20, color=COR_SUAVE)
        contexto.move_to(LADO_DIREITO + UP * 2.1)
        self.play(Create(eixos2), Write(rotulo_x2), Write(rotulo_y2), FadeIn(contexto))

        # As primeiras 5 épocas ficam de fora porque o erro começa lá em cima
        epocas = list(range(6, len(RES["over_treino"]) + 1))
        valores_treino = RES["over_treino"][5:]
        valores_validacao = RES["over_validacao"][5:]
        curva_treino = eixos2.plot_line_graph(x_values=epocas, y_values=valores_treino, line_color=COR_NORMAL, add_vertex_dots=False, stroke_width=4)
        curva_validacao = eixos2.plot_line_graph(x_values=epocas, y_values=valores_validacao, line_color=COR_ESTRANHO, add_vertex_dots=False, stroke_width=4)
        legenda = Text("● treino   ● validação", font_size=18, t2c={"● treino": COR_NORMAL, "● validação": COR_ESTRANHO})
        legenda.next_to(eixos2, UP, buff=0.1)
        self.play(Create(curva_treino), Create(curva_validacao), FadeIn(legenda), run_time=2)

        pergunta2 = perguntar_plateia(self, "Em que época vocês\nparariam o treino?", LADO_DIREITO + UP * 0.5)

        melhor_epoca = RES["over_melhor_epoca"]
        linha_parada = DashedLine(
            eixos2.c2p(melhor_epoca, 0),
            eixos2.c2p(melhor_epoca, 0.5),
            color=COR_DESTAQUE,
        )
        resposta = Text("Na época " + str(melhor_epoca) + " a validação foi a melhor,\ndali pra frente a rede só decorou\nos 80 pedidos. Parar ali é o que\nchamam de parada antecipada", font_size=19, color=COR_DESTAQUE)
        resposta.move_to(LADO_DIREITO + DOWN * 1.7)
        self.play(Create(linha_parada))
        self.play(Write(resposta))
        self.next_slide()
        self.play(FadeOut(*self.mobjects))

        # O tamanho do gargalo no autoencoder
        titulo3 = titulo_slide("No autoencoder, o tamanho do gargalo faz diferença")
        self.play(Write(titulo3))

        # Cada desenho mostra entrada, gargalo e saída
        entrada_p = Rectangle(width=0.4, height=2, color=COR_SUAVE)
        gargalo_p = Rectangle(width=0.4, height=0.3, color=COR_DESTAQUE, fill_color=COR_DESTAQUE, fill_opacity=0.25)
        saida_p = Rectangle(width=0.4, height=2, color=COR_SUAVE)
        gargalo_p.next_to(entrada_p, RIGHT, buff=0.6)
        saida_p.next_to(gargalo_p, RIGHT, buff=0.6)
        rede_p = VGroup(entrada_p, gargalo_p, saida_p)

        entrada_m = Rectangle(width=0.4, height=2, color=COR_SUAVE)
        gargalo_m = Rectangle(width=0.4, height=0.9, color=COR_DESTAQUE, fill_color=COR_DESTAQUE, fill_opacity=0.25)
        saida_m = Rectangle(width=0.4, height=2, color=COR_SUAVE)
        gargalo_m.next_to(entrada_m, RIGHT, buff=0.6)
        saida_m.next_to(gargalo_m, RIGHT, buff=0.6)
        rede_m = VGroup(entrada_m, gargalo_m, saida_m)

        entrada_g = Rectangle(width=0.4, height=2, color=COR_SUAVE)
        gargalo_g = Rectangle(width=0.4, height=2.6, color=COR_DESTAQUE, fill_color=COR_DESTAQUE, fill_opacity=0.25)
        saida_g = Rectangle(width=0.4, height=2, color=COR_SUAVE)
        gargalo_g.next_to(entrada_g, RIGHT, buff=0.6)
        saida_g.next_to(gargalo_g, RIGHT, buff=0.6)
        rede_g = VGroup(entrada_g, gargalo_g, saida_g)

        rede_p.move_to(LEFT * 4.5 + UP * 0.2)
        rede_m.move_to(UP * 0.2)
        rede_g.move_to(RIGHT * 4.5 + UP * 0.2)

        nome_p = Text("pequeno", font_size=22).next_to(rede_p, UP, buff=0.4)
        nome_m = Text("médio", font_size=22).next_to(rede_m, UP, buff=0.4)
        nome_g = Text("grande", font_size=22).next_to(rede_g, UP, buff=0.4)

        self.play(Create(rede_p), Write(nome_p))
        self.play(Create(rede_m), Write(nome_m))
        self.play(Create(rede_g), Write(nome_g))

        pergunta3 = perguntar_plateia(self, "Qual desses gargalos vocês acham\nque encontra melhor um pedido estranho?", DOWN * 2.5)
        self.play(FadeOut(pergunta3))

        resp_p = Text("erra até os pedidos normais,\nentão tudo parece estranho", font_size=18, color=COR_ESTRANHO).next_to(rede_p, DOWN, buff=0.4)
        resp_m = Text("aprende bem o que é normal,\ne o estranho se destaca", font_size=18, color=COR_CERTO).next_to(rede_m, DOWN, buff=0.4)
        resp_g = Text("copia tudo, inclusive o\nestranho, e não acha nada", font_size=18, color=COR_ESTRANHO).next_to(rede_g, DOWN, buff=0.4)
        self.play(FadeIn(resp_p))
        self.play(FadeIn(resp_g))
        self.play(FadeIn(resp_m), Indicate(rede_m, color=COR_CERTO))
        self.next_slide()
        self.play(FadeOut(*self.mobjects))

        # O que aconteceu nos nossos dados (parte 7 do analise_olist.py)
        titulo4 = titulo_slide("E nos dados da Olist?")
        self.play(Write(titulo4))

        gargalos = RES["gargalos"]
        erros_normais = RES["erro_normais_por_gargalo"]
        erros_nota1 = RES["erro_nota1_por_gargalo"]
        maior = max(erros_nota1)

        base = Line(LEFT * 5.5, RIGHT * 5.5, color=COR_SUAVE)
        base.shift(DOWN * 2.3)
        barras = VGroup()
        nomes = VGroup()
        # Um par de barras pra cada tamanho de gargalo (azul = normais, laranja = nota 1)
        for i in range(len(gargalos)):
            x = -4.6 + i * 1.85
            barra_normal = Rectangle(width=0.5, height=max(erros_normais[i] / maior * 3.2, 0.01), fill_color=COR_NORMAL, fill_opacity=0.9, stroke_width=0)
            barra_nota1 = Rectangle(width=0.5, height=max(erros_nota1[i] / maior * 3.2, 0.01), fill_color=COR_ESTRANHO, fill_opacity=0.9, stroke_width=0)
            barra_normal.next_to(base, UP, buff=0).set_x(x - 0.27)
            barra_nota1.next_to(base, UP, buff=0).set_x(x + 0.27)
            barras.add(barra_normal, barra_nota1)
            nome = Text(str(gargalos[i]), font_size=22).next_to(base, DOWN, buff=0.2).set_x(x)
            nomes.add(nome)
        eixo_nome = Text("tamanho do gargalo", font_size=18, color=COR_SUAVE).next_to(nomes, DOWN, buff=0.25)
        legenda2 = Text("● erro nos pedidos normais   ● erro nos pedidos com nota 1", font_size=18, t2c={"● erro nos pedidos normais": COR_NORMAL, "● erro nos pedidos com nota 1": COR_ESTRANHO})
        legenda2.next_to(titulo4, DOWN, buff=0.35).set_x(0)

        self.play(Create(base), FadeIn(nomes), FadeIn(eixo_nome), FadeIn(legenda2))
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in barras], lag_ratio=0.15), run_time=2.5)
        self.next_slide()

        vezes = erros_nota1[1] / erros_normais[1]
        leitura = Text("Com gargalo 2, o erro dos pedidos nota 1 ficou " + com_virgula(vezes, 1) + " vezes maior.\nDe 8 pra cima a rede reconstrói quase tudo e a diferença some", font_size=20, color=COR_DESTAQUE)
        leitura.move_to(UP * 1.75)
        self.play(Write(leitura))


# =====================================================================
# PERGUNTA 16 - Como detectar anomalias com redes neurais?
# =====================================================================
class Pergunta16(Slide):
    def construct(self):
        titulo = titulo_slide("16. Como detectar anomalias?")
        self.play(Write(titulo))

        # A turma tenta achar o pedido estranho antes da rede
        eixos = Axes(x_range=[0, 10, 1], y_range=[0, 10, 1], x_length=5.2, y_length=5.2)
        eixos.shift(DOWN * 0.5 + LEFT * 2)
        rotulo_x = Text("distância", font_size=20, color=COR_SUAVE).next_to(eixos.x_axis, DOWN)
        rotulo_y = Text("frete", font_size=20, color=COR_SUAVE).rotate(PI / 2).next_to(eixos.y_axis, LEFT)
        self.play(Create(eixos), Write(rotulo_x), Write(rotulo_y))

        # Todos começam da mesma cor pra turma ter que procurar
        pedido1 = Dot(eixos.c2p(1, 2.0), color=COR_NORMAL)
        pedido2 = Dot(eixos.c2p(2, 2.4), color=COR_NORMAL)
        pedido3 = Dot(eixos.c2p(3, 3.6), color=COR_NORMAL)
        pedido4 = Dot(eixos.c2p(4, 4.0), color=COR_NORMAL)
        pedido5 = Dot(eixos.c2p(5, 5.2), color=COR_NORMAL)
        pedido6 = Dot(eixos.c2p(6, 5.6), color=COR_NORMAL)
        pedido7 = Dot(eixos.c2p(7, 6.8), color=COR_NORMAL)
        estranho = Dot(eixos.c2p(2.5, 8), color=COR_NORMAL)
        pedidos = VGroup(pedido1, pedido2, pedido3, pedido4, pedido5, pedido6, pedido7, estranho)
        self.play(FadeIn(pedidos))

        pergunta = perguntar_plateia(self, "Algum desses pedidos\nparece estranho pra vocês?", LADO_DIREITO + UP * 1)

        circulo = Circle(radius=0.3, color=COR_ESTRANHO).move_to(estranho.get_center())
        motivo = Text("esse tem frete alto\npra uma distância curta", font_size=22, color=COR_ESTRANHO)
        motivo.move_to(LADO_DIREITO + UP * 1)
        self.play(estranho.animate.set_color(COR_ESTRANHO), Create(circulo))
        self.play(ReplacementTransform(pergunta, motivo))
        self.next_slide()

        # Como a rede acha sozinha. Ela é treinada só com pedidos normais
        # e aprende o padrão deles (a reta amarela)
        x_normais = np.array([1, 2, 3, 4, 5, 6, 7])
        y_normais = np.array([2.0, 2.4, 3.6, 4.0, 5.2, 5.6, 6.8])
        coef = np.polyfit(x_normais, y_normais, 1)
        inclinacao = coef[0]
        intercepto = coef[1]

        def padrao(x):
            return inclinacao * x + intercepto

        reta_padrao = eixos.plot(padrao, x_range=[0, 9], color=COR_DESTAQUE, stroke_width=4)
        nome_padrao = Text("esse é o padrão que a rede\naprendeu com os pedidos normais", font_size=20, color=COR_DESTAQUE)
        nome_padrao.move_to(motivo.get_center())
        self.play(Create(reta_padrao), ReplacementTransform(motivo, nome_padrao))
        self.next_slide()

        # A reconstrução é o ponto mais perto do padrão,
        # e o erro de reconstrução é o tamanho da linha tracejada
        def linha_de_erro(x, y):
            x_rec = (x + inclinacao * (y - intercepto)) / (1 + inclinacao ** 2)
            y_rec = padrao(x_rec)
            return DashedLine(eixos.c2p(x, y), eixos.c2p(x_rec, y_rec), color=COR_TEXTO)

        erro1 = linha_de_erro(1, 2.0)
        erro2 = linha_de_erro(2, 2.4)
        erro3 = linha_de_erro(3, 3.6)
        erro4 = linha_de_erro(4, 4.0)
        erro5 = linha_de_erro(5, 5.2)
        erro6 = linha_de_erro(6, 5.6)
        erro7 = linha_de_erro(7, 6.8)
        erro_estranho = linha_de_erro(2.5, 8)
        erro_estranho.set_color(COR_ESTRANHO)
        erros = VGroup(erro1, erro2, erro3, erro4, erro5, erro6, erro7, erro_estranho)

        explicacao = Text("os pedidos normais ficam perto\ndo padrão, o estranho fica longe", font_size=20)
        explicacao.move_to(nome_padrao.get_center())
        self.play(Create(erros), ReplacementTransform(nome_padrao, explicacao))
        self.next_slide()

        regra = Text("quando o erro passa de um\nlimite τ, o pedido vira alerta", font_size=20, color=COR_ESTRANHO)
        regra.move_to(LADO_DIREITO + DOWN * 1)
        self.play(Write(regra))
        self.next_slide()
        self.play(FadeOut(*self.mobjects))

        # O autoencoder por trás disso
        titulo2 = titulo_slide("O que tem por trás disso é um autoencoder")
        self.play(Write(titulo2))

        entrada = Rectangle(width=0.6, height=3, color=COR_SUAVE)
        entrada.move_to(LEFT * 5 + UP * 0.2)
        codificador = Polygon(LEFT * 3.8 + UP * 1.7, LEFT * 1.2 + UP * 0.6, LEFT * 1.2 + DOWN * 0.2, LEFT * 3.8 + DOWN * 1.3, color=COR_NORMAL, fill_color=COR_NORMAL, fill_opacity=0.12)
        gargalo = Rectangle(width=0.6, height=0.8, color=COR_DESTAQUE, fill_color=COR_DESTAQUE, fill_opacity=0.25)
        gargalo.move_to(UP * 0.2)
        decodificador = Polygon(RIGHT * 1.2 + UP * 0.6, RIGHT * 3.8 + UP * 1.7, RIGHT * 3.8 + DOWN * 1.3, RIGHT * 1.2 + DOWN * 0.2, color=COR_NORMAL, fill_color=COR_NORMAL, fill_opacity=0.12)
        saida = Rectangle(width=0.6, height=3, color=COR_SUAVE)
        saida.move_to(RIGHT * 5 + UP * 0.2)

        nome_entrada = Text("pedido\noriginal", font_size=18, color=COR_SUAVE).next_to(entrada, DOWN)
        nome_gargalo = Text("gargalo", font_size=18, color=COR_SUAVE).next_to(gargalo, DOWN, buff=1.3)
        nome_saida = Text("pedido\nreconstruído", font_size=18, color=COR_SUAVE).next_to(saida, DOWN)
        nome_cod = Text("codificador", font_size=18).move_to(codificador.get_center())
        nome_dec = Text("decodificador", font_size=18).move_to(decodificador.get_center())

        self.play(FadeIn(entrada), FadeIn(nome_entrada), DrawBorderThenFill(codificador), FadeIn(nome_cod))
        self.play(DrawBorderThenFill(gargalo), FadeIn(nome_gargalo))
        self.play(DrawBorderThenFill(decodificador), FadeIn(nome_dec), FadeIn(saida), FadeIn(nome_saida))

        formula = Text("O erro é a diferença entre o pedido original e o reconstruído, MSE = média de (x − r)²", font_size=18, color=COR_DESTAQUE)
        formula.to_edge(DOWN, buff=0.5)
        arquitetura = Text("Na nossa rede são 10 → 8 → 2 → 8 → 10 neurônios, com ReLU, Adam e 40 épocas", font_size=18, color=COR_SUAVE)
        arquitetura.next_to(formula, UP, buff=0.25)
        self.play(FadeIn(formula), FadeIn(arquitetura))
        self.next_slide()
        self.play(FadeOut(*self.mobjects))

        # Os pedidos mais estranhos que a rede achou de verdade
        titulo5 = titulo_slide("Os pedidos mais estranhos que a rede achou")
        self.play(Write(titulo5))

        # O 1º e o 3º colocados (o 2º é igual ao 1º, mesmo produto)
        estranho1 = RES["mais_estranhos"][0]
        estranho2 = RES["mais_estranhos"][2]
        texto1 = Paragraph(
            "produto de R$ " + com_virgula(estranho1["preco"]),
            "frete de R$ " + com_virgula(estranho1["frete"]),
            "cliente a " + com_virgula(estranho1["distancia"], 0) + " km",
            "nota " + str(estranho1["nota"]),
            alignment="left", font_size=22, line_spacing=0.8,
        )
        texto2 = Paragraph(
            "prometido pra " + str(estranho2["prazo_prometido"]) + " dias",
            "entregue em " + str(estranho2["prazo_real"]) + " dias",
            "produto de R$ " + com_virgula(estranho2["preco"]),
            "nota " + str(estranho2["nota"]),
            alignment="left", font_size=22, line_spacing=0.8,
        )
        texto1.move_to(LEFT * 3.3 + UP * 0.6)
        texto2.move_to(RIGHT * 3.3 + UP * 0.6)
        cartao1 = SurroundingRectangle(texto1, buff=0.35, corner_radius=0.2, color=COR_ESTRANHO)
        cartao2 = SurroundingRectangle(texto2, buff=0.35, corner_radius=0.2, color=COR_ESTRANHO)
        self.play(Create(cartao1), Write(texto1))
        self.play(Create(cartao2), Write(texto2))

        pergunta_estranho = perguntar_plateia(self, "O que tem de estranho nesses dois?", DOWN * 2.2)
        self.play(FadeOut(pergunta_estranho))

        vezes = estranho1["frete"] / estranho1["preco"]
        meses_atraso = estranho2["diferenca"] // 30
        motivo1 = Text("o frete custou " + com_virgula(vezes, 0) + " vezes\no valor do produto", font_size=20, color=COR_ESTRANHO)
        motivo2 = Text("chegou com mais de " + str(meses_atraso) + "\nmeses de atraso", font_size=20, color=COR_ESTRANHO)
        motivo1.next_to(cartao1, DOWN, buff=0.4)
        motivo2.next_to(cartao2, DOWN, buff=0.4)
        self.play(FadeIn(motivo1, shift=UP * 0.2))
        self.play(FadeIn(motivo2, shift=UP * 0.2))
        self.next_slide()

        nota_cinco = Text("Repara que o primeiro levou nota " + str(estranho1["nota"]) + ", estranho nem sempre quer dizer problema", font_size=20, color=COR_DESTAQUE)
        nota_cinco.to_edge(DOWN, buff=0.6)
        self.play(Write(nota_cinco))
        self.next_slide()
        self.play(FadeOut(*self.mobjects))

        # Conferência com as avaliações dos clientes
        titulo3 = titulo_slide("Será que a rede achou os pedidos problemáticos?")
        self.play(Write(titulo3))

        pergunta2 = perguntar_plateia(self, "Vocês acham que os pedidos com alerta\ntêm mais ou menos nota 1 que a média?", ORIGIN)
        self.play(FadeOut(pergunta2))

        pct_nota1_geral = RES["pct_nota1_geral"]
        pct_nota1_alertas = RES["pct_nota1_alertas"]

        base = Line(LEFT * 3.8, RIGHT * 3.8, color=COR_SUAVE)
        base.shift(DOWN * 2.3)
        barra_geral = Rectangle(width=1.5, height=pct_nota1_geral * 0.065, fill_color=COR_NORMAL, fill_opacity=0.9, stroke_width=0)
        barra_alertas = Rectangle(width=1.5, height=pct_nota1_alertas * 0.065, fill_color=COR_ESTRANHO, fill_opacity=0.9, stroke_width=0)
        barra_geral.next_to(base, UP, buff=0).shift(LEFT * 2)
        barra_alertas.next_to(base, UP, buff=0).shift(RIGHT * 2)

        nome_geral = Text("todos os " + com_virgula(RES["n_pedidos"], 0) + "\npedidos", font_size=20, color=COR_SUAVE).next_to(barra_geral, DOWN, buff=0.25)
        nome_alertas = Text("os " + com_virgula(RES["n_alertas"], 0) + " pedidos\ncom alerta", font_size=20, color=COR_SUAVE).next_to(barra_alertas, DOWN, buff=0.25)
        valor_geral = Text(com_virgula(pct_nota1_geral, 1) + "% com nota 1", font_size=20).next_to(barra_geral, UP)
        valor_alertas = Text(com_virgula(pct_nota1_alertas, 1) + "% com nota 1", font_size=20).next_to(barra_alertas, UP)

        self.play(Create(base))
        self.play(GrowFromEdge(barra_geral, DOWN), Write(nome_geral), Write(valor_geral))
        self.play(GrowFromEdge(barra_alertas, DOWN), Write(nome_alertas), Write(valor_alertas))
        self.next_slide()

        lembrete = Text("e a rede nunca viu as notas durante o treino", font_size=20, color=COR_DESTAQUE)
        lembrete.next_to(titulo3, DOWN, buff=0.4).set_x(0)
        self.play(Write(lembrete))
        self.next_slide()
        self.play(FadeOut(*self.mobjects))

        # A própria história como teste
        titulo4 = titulo_slide("Usando a própria história como teste")
        self.play(Write(titulo4))

        meses = RES["meses"]
        pct_alerta_mes = RES["pct_alerta_mes"]
        pct_atraso_mes = RES["pct_atraso_mes"]
        posicao_bf = meses.index("2017-11")
        posicao_greve = meses.index("2018-05")

        eixos3 = Axes(x_range=[0, len(meses) - 1, 1], y_range=[0, 6, 1], x_length=10, y_length=3.6)
        eixos3.shift(DOWN * 0.9)
        rotulo_y3 = Text("% de pedidos com alerta", font_size=18, color=COR_SUAVE).rotate(PI / 2).next_to(eixos3.y_axis, LEFT)
        inicio = Text(mes_curto(meses[0]), font_size=18, color=COR_SUAVE).next_to(eixos3.c2p(0, 0), DOWN)
        fim = Text(mes_curto(meses[-1]), font_size=18, color=COR_SUAVE).next_to(eixos3.c2p(len(meses) - 1, 0), DOWN)
        self.play(Create(eixos3), Write(rotulo_y3), Write(inicio), Write(fim))

        # Marca a Black Friday e a greve antes de mostrar a curva
        linha_bf = DashedLine(eixos3.c2p(posicao_bf, 0), eixos3.c2p(posicao_bf, 6), color=COR_SUAVE)
        linha_greve = DashedLine(eixos3.c2p(posicao_greve, 0), eixos3.c2p(posicao_greve, 6), color=COR_SUAVE)
        nome_bf = Text("Black Friday\nnov/17", font_size=18, color=COR_SUAVE).next_to(linha_bf, UP, buff=0.1)
        nome_greve = Text("greve dos\ncaminhoneiros\nmai/18", font_size=18, color=COR_SUAVE).next_to(linha_greve, UP, buff=0.1)
        self.play(Create(linha_bf), Create(linha_greve), FadeIn(nome_bf), FadeIn(nome_greve))

        pergunta3 = perguntar_plateia(self, "Em quais meses vocês acham\nque o detector acendeu?", LEFT * 3.2 + UP * 2.0)
        self.play(FadeOut(pergunta3))

        curva_meses = eixos3.plot_line_graph(
            x_values=list(range(len(meses))),
            y_values=pct_alerta_mes,
            line_color=COR_ESTRANHO,
            vertex_dot_style={"fill_color": COR_ESTRANHO},
            stroke_width=4,
        )
        self.play(Create(curva_meses), run_time=3)
        self.next_slide()

        # Os dois meses com mais alerta em 2018
        posicao_fev = meses.index("2018-02")
        posicao_mar = meses.index("2018-03")
        leitura = Text(
            "A Black Friday acendeu e a greve também ficou acima do normal,\n"
            "mas o pico maior foi em fevereiro e março de 2018. Fomos ver e esses\n"
            "foram os meses com mais atraso, " + com_virgula(pct_atraso_mes[posicao_fev], 0) + "% e "
            + com_virgula(pct_atraso_mes[posicao_mar], 0) + "% dos pedidos chegaram depois do prazo",
            font_size=18,
            color=COR_DESTAQUE,
        )
        leitura.to_edge(UP, buff=1.2)
        self.play(FadeOut(nome_bf), FadeOut(nome_greve))
        self.play(Write(leitura), run_time=2)
        self.next_slide()

        self.play(FadeOut(*self.mobjects))

        # Demo ao vivo
        desafio = caixa_plateia("Agora é com vocês, inventem um\npedido e tentem enganar a rede")
        desafio.scale(1.4)
        dica = Text("pode ser qualquer coisa, preço, frete, distância, prazo...", font_size=22, color=COR_SUAVE)
        dica.next_to(desafio, DOWN, buff=0.6)
        self.play(FadeIn(desafio, shift=DOWN * 0.3))
        self.play(FadeIn(dica))
        # Aqui você sai do HTML e abre o notebook com o autoencoder treinado


# =====================================================================
# ENCERRAMENTO
# =====================================================================
class Encerramento(Slide):
    def construct(self):
        # Resumo das 3 respostas
        titulo_resumo = titulo_slide("Resumindo")
        resumo1 = Text("1.  O neurônio aprende errando e ajustando os pesos aos poucos", font_size=22, t2c={"1.": COR_CERTO})
        resumo2 = Text("6.  Quando aprende demais, a rede decora o treino e erra em dados novos", font_size=22, t2c={"6.": COR_CERTO})
        resumo3 = Text("16. Anomalia é aquilo que a rede não consegue reconstruir bem", font_size=22, t2c={"16.": COR_CERTO})
        resumo2.next_to(resumo1, DOWN, buff=0.5, aligned_edge=LEFT)
        resumo3.next_to(resumo2, DOWN, buff=0.5, aligned_edge=LEFT)
        resumos = VGroup(resumo1, resumo2, resumo3)
        resumos.move_to(DOWN * 0.2)

        self.play(Write(titulo_resumo))
        self.play(FadeIn(resumo1, shift=UP * 0.2))
        self.play(FadeIn(resumo2, shift=UP * 0.2))
        self.play(FadeIn(resumo3, shift=UP * 0.2))
        self.next_slide()
        self.play(FadeOut(titulo_resumo), FadeOut(resumos))

        # Onde isso é usado hoje
        titulo_app = titulo_slide("Onde isso é usado hoje")
        app1 = Text("• em bancos, pra pegar compras fora do padrão do cliente", font_size=20)
        app2 = Text("• na logística, pra achar entregas com prazo ou frete estranho", font_size=20)
        app3 = Text("• em marketplaces, pra achar anúncios com preço muito fora da média", font_size=20)
        app4 = Text("• na indústria, pra perceber quando uma máquina começa a falhar", font_size=20)
        app2.next_to(app1, DOWN, buff=0.4, aligned_edge=LEFT)
        app3.next_to(app2, DOWN, buff=0.4, aligned_edge=LEFT)
        app4.next_to(app3, DOWN, buff=0.4, aligned_edge=LEFT)
        aplicacoes = VGroup(app1, app2, app3, app4)
        aplicacoes.move_to(DOWN * 0.2)
        self.play(Write(titulo_app))
        self.play(FadeIn(app1))
        self.play(FadeIn(app2))
        self.play(FadeIn(app3))
        self.play(FadeIn(app4))
        self.next_slide()
        self.play(FadeOut(titulo_app), FadeOut(aplicacoes))

        # Limitações
        titulo_lim = titulo_slide("Limitações")
        lim1 = Text("• nem toda nota 1 é culpa do pedido, então nosso gabarito não é perfeito", font_size=20)
        lim2 = Text("• erro alto não quer dizer problema, um dos pedidos mais estranhos teve nota 5", font_size=20)
        lim3 = Text("• dependendo do limite τ que a gente escolhe, aparecem mais ou menos alertas", font_size=20)
        lim4 = Text("• " + com_virgula(RES["pct_atraso_alertas"], 0) + "% dos alertas são pedidos que atrasaram, e tirando eles,\n   a nota 1 nos alertas cai pra " + com_virgula(RES["pct_nota1_alertas_sem_atraso"], 0) + "%, quase igual à média", font_size=20)
        lim2.next_to(lim1, DOWN, buff=0.4, aligned_edge=LEFT)
        lim3.next_to(lim2, DOWN, buff=0.4, aligned_edge=LEFT)
        lim4.next_to(lim3, DOWN, buff=0.4, aligned_edge=LEFT)
        limitacoes = VGroup(lim1, lim2, lim3, lim4)
        limitacoes.move_to(DOWN * 0.2)
        self.play(Write(titulo_lim))
        self.play(FadeIn(lim1))
        self.play(FadeIn(lim2))
        self.play(FadeIn(lim3))
        self.play(FadeIn(lim4))
        self.next_slide()
        self.play(FadeOut(titulo_lim), FadeOut(limitacoes))

        # Código e uso de IA (o enunciado pede pra declarar)
        codigo = Text("O código está no GitHub, em github.com/arcseno/neuralNetworksFinalProject", font_size=22)
        ia = Text("O Claude foi utilizado para o aprimoramento das animações, visando a fluidez na apresentação.", font_size=20, color=COR_SUAVE)
        ia.next_to(codigo, DOWN, buff=0.5)
        self.play(Write(codigo))
        self.play(FadeIn(ia))
        self.next_slide()
        self.play(FadeOut(codigo), FadeOut(ia))

        # Fecha com a logo de novo
        logo = ImageMobject(LOGO_UEL)
        logo.height = 1.6
        logo.move_to(UP * 1.4)
        final = Text("Obrigado! Alguma pergunta?", font_size=40)
        final.next_to(logo, DOWN, buff=0.7)
        # TODO: QR code do quiz (Kahoot ou Mentimeter), se forem fazer
        self.play(FadeIn(logo, scale=0.9))
        self.play(Write(final))