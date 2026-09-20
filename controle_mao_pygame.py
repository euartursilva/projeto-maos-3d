"""Realidade aumentada simples: controle cubos 3D com a mao."""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from typing import Optional

import cv2
import mediapipe as mp
import pygame


LARGURA_JANELA = 800
ALTURA_JANELA = 600
CAMERA_INDEX = 0


def limitar(valor: float, minimo: float, maximo: float) -> float:
    return max(minimo, min(maximo, valor))


def ponto_para_tela(x_normalizado: float, y_normalizado: float) -> tuple[int, int]:
    """Mapeia coordenadas normalizadas do MediaPipe para pixels da janela."""

    return (
        round(limitar(x_normalizado, 0.0, 1.0) * (LARGURA_JANELA - 1)),
        round(limitar(y_normalizado, 0.0, 1.0) * (ALTURA_JANELA - 1)),
    )


def mao_e_pinco(landmarks: object) -> bool:
    """Detecta o gesto de pegar aproximando polegar e indicador."""

    polegar = landmarks.landmark[4]
    indicador = landmarks.landmark[8]
    distancia = math.hypot(polegar.x - indicador.x, polegar.y - indicador.y)
    return distancia < 0.065


def profundidade_da_mao(landmarks: object) -> float:
    """Converte o eixo Z do indicador em profundidade visual entre 0 e 1."""

    z_indicador = landmarks.landmark[8].z
    return limitar(0.5 - z_indicador * 2.0, 0.05, 0.95)


@dataclass
class Cubo3D:
    """Cubo 3D projetado em perspectiva simples sobre a webcam."""

    x: float
    y: float
    profundidade: float
    tamanho: int
    cor: tuple[int, int, int]
    nome: str
    selecionado: bool = False

    def area_projetada(self) -> pygame.Rect:
        escala = 0.72 + self.profundidade * 0.72
        lado = round(self.tamanho * escala)
        return pygame.Rect(round(self.x - lado / 2), round(self.y - lado / 2), lado, lado)

    def desenhar(self, tela: pygame.Surface, fonte: pygame.font.Font) -> None:
        escala = 0.72 + self.profundidade * 0.72
        lado = round(self.tamanho * escala)
        metade = lado // 2
        deslocamento_3d = max(10, round(26 * escala))
        centro = (round(self.x), round(self.y))
        frente = pygame.Rect(centro[0] - metade, centro[1] - metade, lado, lado)
        topo = [(frente.left, frente.top), (frente.left + deslocamento_3d, frente.top - deslocamento_3d), (frente.right + deslocamento_3d, frente.top - deslocamento_3d), (frente.right, frente.top)]
        lateral = [(frente.right, frente.top), (frente.right + deslocamento_3d, frente.top - deslocamento_3d), (frente.right + deslocamento_3d, frente.bottom - deslocamento_3d), (frente.right, frente.bottom)]
        cor_frente = self.cor if not self.selecionado else (80, 230, 145)
        cor_topo = tuple(min(255, valor + 45) for valor in cor_frente)
        cor_lateral = tuple(max(0, valor - 45) for valor in cor_frente)
        pygame.draw.polygon(tela, cor_topo, topo)
        pygame.draw.polygon(tela, cor_lateral, lateral)
        pygame.draw.rect(tela, cor_frente, frente)
        pygame.draw.polygon(tela, (245, 248, 250), topo, width=2)
        pygame.draw.polygon(tela, (245, 248, 250), lateral, width=2)
        pygame.draw.rect(tela, (245, 248, 250), frente, width=2)
        etiqueta = fonte.render(self.nome, True, (255, 255, 255))
        tela.blit(etiqueta, etiqueta.get_rect(center=frente.center))


def criar_objetos() -> list[Cubo3D]:
    return [
        Cubo3D(155, 210, 0.30, 115, (35, 125, 220), "AZUL"),
        Cubo3D(555, 245, 0.52, 105, (220, 75, 65), "VERMELHO"),
        Cubo3D(350, 445, 0.18, 125, (135, 70, 175), "ROXO"),
    ]


def camera_para_surface(frame: object) -> pygame.Surface:
    frame_redimensionado = cv2.resize(frame, (LARGURA_JANELA, ALTURA_JANELA))
    return pygame.image.frombuffer(frame_redimensionado.tobytes(), (LARGURA_JANELA, ALTURA_JANELA), "RGB")


def desenhar_hud(
    tela: pygame.Surface,
    fonte: pygame.font.Font,
    cursor: Optional[tuple[int, int]],
    pinco_ativo: bool,
    camera_ok: bool,
    objeto: Optional[Cubo3D],
) -> None:
    painel = pygame.Surface((LARGURA_JANELA, 72), pygame.SRCALPHA)
    painel.fill((8, 15, 25, 205))
    tela.blit(painel, (0, 0))
    tela.blit(fonte.render("MAO 3D  |  REALIDADE AUMENTADA", True, (240, 245, 250)), (18, 12))
    if not camera_ok:
        estado, cor_estado = "Webcam indisponivel - verifique a permissao", (255, 190, 100)
    elif objeto is not None and pinco_ativo:
        estado = f"SEGURANDO {objeto.nome}  |  mova X/Y e aproxime para aumentar"
        cor_estado = (100, 240, 155)
    elif cursor is not None:
        estado, cor_estado = "Faca uma pinça sobre um cubo para pegar", (230, 235, 245)
    else:
        estado, cor_estado = "Mostre uma mao para iniciar", (230, 190, 100)
    tela.blit(fonte.render(estado, True, cor_estado), (18, 43))


def desenhar_cursor(tela: pygame.Surface, cursor: tuple[int, int], pinco_ativo: bool) -> None:
    cor = (80, 240, 150) if pinco_ativo else (255, 230, 100)
    pygame.draw.circle(tela, (255, 255, 255), cursor, 14, width=2)
    pygame.draw.circle(tela, cor, cursor, 5)


def abrir_camera() -> cv2.VideoCapture:
    """Abre a webcam com backend mais estavel no Windows."""

    camera = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
    if not camera.isOpened():
        camera.release()
        camera = cv2.VideoCapture(CAMERA_INDEX)
    return camera


def executar() -> None:
    pygame.init()
    tela = pygame.display.set_mode((LARGURA_JANELA, ALTURA_JANELA))
    pygame.display.set_caption("Mao 3D - Webcam + MediaPipe + Pygame")
    relogio = pygame.time.Clock()
    fonte = pygame.font.Font(None, 24)
    camera = abrir_camera()
    camera_ok = camera.isOpened()
    cubos = criar_objetos()
    cubo_selecionado: Optional[Cubo3D] = None
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils

    try:
        with mp_hands.Hands(static_image_mode=False, max_num_hands=1, model_complexity=0, min_detection_confidence=0.7, min_tracking_confidence=0.6) as detector:
            executando = True
            while executando:
                for evento in pygame.event.get():
                    if evento.type == pygame.QUIT or (evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE):
                        executando = False

                cursor: Optional[tuple[int, int]] = None
                pinco_ativo = False
                frame_surface: Optional[pygame.Surface] = None

                if camera_ok:
                    sucesso, frame = camera.read()
                    if not sucesso:
                        camera_ok = False
                    else:
                        frame = cv2.flip(frame, 1)
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        resultado = detector.process(frame_rgb)
                        if resultado.multi_hand_landmarks:
                            landmarks = resultado.multi_hand_landmarks[0]
                            mp_drawing.draw_landmarks(frame_rgb, landmarks, mp_hands.HAND_CONNECTIONS)
                            cursor = ponto_para_tela(landmarks.landmark[8].x, landmarks.landmark[8].y)
                            pinco_ativo = mao_e_pinco(landmarks)
                            if pinco_ativo and cubo_selecionado is None:
                                for cubo in sorted(cubos, key=lambda item: item.profundidade, reverse=True):
                                    if cubo.area_projetada().inflate(24, 24).collidepoint(cursor):
                                        cubo_selecionado = cubo
                                        cubo.selecionado = True
                                        break
                            elif not pinco_ativo and cubo_selecionado is not None:
                                cubo_selecionado.selecionado = False
                                cubo_selecionado = None
                            if cubo_selecionado is not None:
                                cubo_selecionado.x = cursor[0]
                                cubo_selecionado.y = cursor[1]
                                alvo_z = profundidade_da_mao(landmarks)
                                cubo_selecionado.profundidade += (alvo_z - cubo_selecionado.profundidade) * 0.18
                                area = cubo_selecionado.area_projetada()
                                cubo_selecionado.x = limitar(cubo_selecionado.x, area.width / 2, LARGURA_JANELA - area.width / 2 - 25)
                                cubo_selecionado.y = limitar(cubo_selecionado.y, 95 + area.height / 2, ALTURA_JANELA - area.height / 2 - 15)
                        frame_surface = camera_para_surface(frame_rgb)

                if not camera_ok:
                    tela.fill((18, 25, 35))
                elif frame_surface is not None:
                    tela.blit(frame_surface, (0, 0))
                for cubo in sorted(cubos, key=lambda item: item.profundidade):
                    cubo.desenhar(tela, fonte)
                desenhar_hud(tela, fonte, cursor, pinco_ativo, camera_ok, cubo_selecionado)
                if cursor is not None:
                    desenhar_cursor(tela, cursor, pinco_ativo)
                pygame.display.flip()
                relogio.tick(60)
    finally:
        if cubo_selecionado is not None:
            cubo_selecionado.selecionado = False
        camera.release()
        cv2.destroyAllWindows()
        pygame.quit()


if __name__ == "__main__":
    try:
        executar()
    except KeyboardInterrupt:
        pygame.quit()
        sys.exit(0)