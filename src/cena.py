from manim import *

class Introducao(Scene):
    def construct(self):
        nomes = Text("Vinícius Yudi Oya e Leonardo Ryoichi Yakushijin Taniguti", font_size=24)
        self.play(Write(nomes))
        self.wait()