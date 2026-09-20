# Cubos 3D controlados pela mao

Uma experiencia de realidade aumentada feita em Python. A webcam ocupa a janela do Pygame e tres cubos aparecem sobre a imagem. O indicador funciona como cursor; uma pinça entre o polegar e o indicador pega um cubo e permite move-lo pela cena.

O projeto nasceu como um estudo pratico de visao computacional: captura de video, rastreamento de mao, conversao de coordenadas e uma pequena projecao 3D desenhada sem motor grafico externo.

## O que da para fazer

- Ver a propria imagem em tempo real dentro da janela.
- Mover o cursor usando a ponta do indicador.
- Selecionar e soltar cubos com o gesto de pinça.
- Alterar a posicao horizontal e vertical do cubo.
- Aproximar ou afastar a mao para alterar a profundidade e o tamanho aparente.
- Ver a malha de landmarks da mao sobre o video.

## Tecnologias

- Python 3.12
- OpenCV para captura e espelhamento da webcam
- MediaPipe Hands `0.10.21` para os 21 landmarks da mao
- Pygame para a janela, HUD e desenho dos cubos

## Instalacao

No Windows, abra o terminal na pasta do projeto e crie um ambiente virtual:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

O arquivo `requirements.txt` fixa a versao do MediaPipe usada pelo codigo. Isso evita que uma atualizacao da biblioteca remova a API `mediapipe.solutions.hands`.

## Como executar

Com o ambiente virtual ativado:

```powershell
python controle_mao_pygame.py
```

Ou diretamente pelo executavel do ambiente:

```powershell
.\.venv\Scripts\python.exe .\controle_mao_pygame.py
```

## Controles

1. Permita o acesso do Python a webcam.
2. Aponte o indicador para um cubo.
3. Encoste o polegar no indicador para seleciona-lo.
4. Mantendo a pinça, mova a mao para controlar X e Y.
5. Aproxime ou afaste a mao para alterar o eixo Z visual do cubo.
6. Separe os dedos para soltar.
7. Pressione `ESC` ou feche a janela para sair.

## Estrutura

```text
.
|-- controle_mao_pygame.py  # Aplicacao completa
|-- requirements.txt        # Dependencias do projeto
|-- README.md               # Documentacao
|-- .gitignore              # Arquivos locais ignorados pelo Git
`-- .vscode/settings.json   # Interpretador recomendado no VS Code
```

## Como o rastreamento funciona

O frame da webcam e espelhado antes de ser enviado ao MediaPipe. Assim, mover a mao para a direita tambem move o cursor para a direita. As coordenadas `x` e `y` dos landmarks sao normalizadas entre `0` e `1` e convertidas para os `800x600` pixels da janela.

O eixo `z` do indicador fornece uma estimativa relativa de distancia em relacao a camera. Os cubos sao desenhados em uma projecao 2.5D: frente, topo e lateral recebem cores e deslocamentos diferentes para sugerir volume, enquanto a profundidade altera sua escala.

## Solucao de problemas

**A webcam nao aparece**

- Feche Teams, Zoom, navegador ou outro programa que possa estar usando a camera.
- Confirme a permissao em `Configuracoes > Privacidade e seguranca > Camera`.
- Execute novamente pelo `.venv` depois de liberar o dispositivo.

**O comando `python` nao existe**

Instale o Python pelo site oficial ou use o launcher do Windows:

```powershell
py -3.12 controle_mao_pygame.py
```

## Licenca

Este projeto esta disponivel para estudo e modificacao. Escolha uma licenca antes de publicar uma versao distribuida no GitHub.