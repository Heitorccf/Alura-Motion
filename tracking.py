# Importação das bibliotecas necessárias
import cv2  # OpenCV para processamento de imagem
import mediapipe as mp  # MediaPipe para detecção de mãos
import os  # Para executar comandos do sistema operacional

# Definição de cores em formato BGR (Blue, Green, Red)
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
AZUL = (255, 0, 0)
AZUL_CLARO = (173, 216, 230)
CINZA = (200, 200, 200)
CINZA_ESCURO = (169, 169, 169)

# Inicialização do MediaPipe para detecção de mãos
mp_hand = mp.solutions.hands
mp_desenho = mp.solutions.drawing_utils
hand = mp_hand.Hands()

# Configuração da webcam
webcam = cv2.VideoCapture(0)  # Inicializa a webcam (0 é geralmente a webcam padrão)
resolution_x = 1280
resolution_y = 720
# Define a resolução da webcam
webcam.set(cv2.CAP_PROP_FRAME_WIDTH, resolution_x)
webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution_y)

# Variáveis para controle de aplicativos abertos
notepad = False
chrome = False
calculator = False

# Layout do teclado virtual
teclas = [
    ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
    ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
    ["Z", "X", "C", "V", "B", "N", "M", ",", ".", ";"],
    [" "]  # Tecla de espaço
]

# Configurações de layout para o teclado virtual
offset = 50  # Espaçamento inicial
button_width = 80  # Largura dos botões
button_height = 80  # Altura dos botões
espaco_width = 500  # Largura da tecla de espaço

def encontra_coord(imagem, reverse_side=False):
    """
    Função que detecta e processa as mãos na imagem
    Retorna a imagem com as marcações e as coordenadas das mãos detectadas
    """
    imagem_rgb = cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB)  # Converte imagem para RGB
    resultado = hand.process(imagem_rgb)  # Processa a imagem para detectar mãos
    whole_hands = []  # Lista para armazenar informações das mãos detectadas

    if resultado.multi_hand_landmarks:
        for hand_side, hand_marking in zip(resultado.multi_handedness, resultado.multi_hand_landmarks):
            info_hand = {}
            coord = []

            # Extrai as coordenadas de cada ponto da mão
            for marking in hand_marking.landmark:
                coord_X, coord_y, coord_z = int(marking.x * resolution_x), int(marking.y * resolution_y), int(marking.z * resolution_x)
                coord.append((coord_X, coord_y, coord_z))

            info_hand["coord"] = coord
            
            # Determina se é mão direita ou esquerda
            if reverse_side:
                if hand_side.classification[0].label == "Left":
                    info_hand["Lado"] = "Right"
                else:
                    info_hand["Lado"] = "Left"
            else:
                info_hand["Lado"] = hand_side.classification[0].label

            whole_hands.append(info_hand)
            # Desenha as marcações da mão na imagem
            mp_desenho.draw_landmarks(imagem, hand_marking, mp_hand.HAND_CONNECTIONS)

    return imagem, whole_hands

def raised_fingers(hand):
    """
    Função que determina quais dedos estão levantados
    Retorna uma lista de booleanos indicando o estado de cada dedo
    """
    fingers = []
    # Verifica cada dedo (exceto o polegar)
    for ponta_finger in [8, 12, 16, 20]:  # Índices das pontas dos dedos
        if hand["coord"][ponta_finger][1] < hand["coord"][ponta_finger-2][1]:
            fingers.append(True)  # Dedo levantado
        else:
            fingers.append(False)  # Dedo abaixado
    return fingers

def print_btn(imagem, position, texto, width=button_width, height=button_height, color=BRANCO):
    """
    Função que desenha um botão na imagem
    Retorna a imagem com o botão desenhado
    """
    # Desenha o retângulo do botão
    cv2.rectangle(imagem, position, (position[0]+width, position[1]+height), color, cv2.FILLED, cv2.LINE_AA)
    # Desenha a borda do botão
    cv2.rectangle(imagem, position, (position[0]+width, position[1]+height), CINZA_ESCURO, 2, cv2.LINE_AA)
    # Adiciona o texto ao botão
    cv2.putText(imagem, texto, (position[0]+width//4, position[1]+height//2+10), cv2.FONT_HERSHEY_COMPLEX, 1, PRETO, 2)
    return imagem

# Loop principal do programa
while True:
    sucesso, imagem = webcam.read()  # Lê um frame da webcam
    
    if not sucesso:
        break  # Se não conseguir ler o frame, encerra o programa

    imagem = cv2.flip(imagem, 1)  # Espelha a imagem horizontalmente
    imagem, whole_hands = encontra_coord(imagem)  # Detecta as mãos na imagem
    
    # Verifica se deve mostrar o teclado virtual
    mostrar_teclado = False
    for hand_info in whole_hands:
        if hand_info["Lado"] == "Left":
            mostrar_teclado = True
            break

    # Desenha o teclado virtual se necessário
    if mostrar_teclado:
        for index_line, keyboard_line in enumerate(teclas):
            for index, texto in enumerate(keyboard_line):
                if texto == " ":
                    # Desenha a tecla de espaço
                    imagem = print_btn(imagem, (offset + index * button_width, offset + index_line * button_height), texto, width=espaco_width, height=button_height, color=AZUL_CLARO)
                else:
                    # Desenha as outras teclas
                    imagem = print_btn(imagem, (offset + index * button_width, offset + index_line * button_height), texto, color=AZUL_CLARO)
    
    # Verifica gestos para controle de aplicativos
    if len(whole_hands) == 1:
        info_fingers1 = raised_fingers(whole_hands[0])
        if whole_hands[0]["Lado"] == "Right":
            # Diferentes gestos para abrir/fechar aplicativos
            if info_fingers1 == [True, False, False, False] and not notepad:
                notepad = True
                os.startfile(r"C:\Windows\System32\notepad.exe")  # Abre o Notepad
            if info_fingers1 == [True, True, False, False] and not chrome:
                chrome = True
                os.startfile(r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Google Chrome.lnk")  # Abre o Chrome
            if info_fingers1 == [True, True, True, False] and not calculator:
                calculator = True
                os.startfile(r"C:\Windows\System32\calc.exe")  # Abre a Calculadora
            if info_fingers1 == [False, False, False, False] and notepad:
                notepad = False
                os.system("TASKKILL /IM notepad.exe")  # Fecha o Notepad
            if info_fingers1 == [True, False, False, True]:
                break  # Encerra o programa
    
    # Mostra a imagem processada
    cv2.imshow("Câmera", imagem)

    # Verifica se a tecla ESC foi pressionada para encerrar o programa
    key = cv2.waitKey(1)
    if key == 27:  # 27 é o código ASCII da tecla ESC
        break

# Libera os recursos
webcam.release()
cv2.destroyAllWindows()