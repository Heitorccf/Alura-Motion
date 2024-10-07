# Importação das bibliotecas necessárias
import cv2  # OpenCV para processamento de imagem
import mediapipe as mp  # MediaPipe para detecção de mãos
import os  # Para executar comandos do sistema operacional
import pyautogui  # Para simular pressionamento de teclas do teclado físico
import time  # Para controle de tempo entre pressionamentos de tecla

# Definição de cores em formato BGR (Blue, Green, Red)
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
AZUL = (255, 0, 0)
AZUL_CLARO = (173, 216, 230)
CINZA = (200, 200, 200)
CINZA_ESCURO = (169, 169, 169)
VERDE = (0, 255, 0)

# Inicialização do MediaPipe para detecção de mãos
mp_hand = mp.solutions.hands
mp_desenho = mp.solutions.drawing_utils
hand = mp_hand.Hands()

# Configuração da webcam
webcam = cv2.VideoCapture(0)  # Inicializa a webcam (0 é geralmente a webcam padrão)
resolution_x = 1280
resolution_y = 720
webcam.set(cv2.CAP_PROP_FRAME_WIDTH, resolution_x)
webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution_y)

# Variáveis para controle de aplicativos abertos
notepad = False
chrome = False
calculator = False

# Variáveis para controle do teclado virtual
contador = 0  # Contador para controle de digitação
texto = ">"  # Texto inicial que será exibido na tela
ultima_tecla = None  # Armazena a última tecla pressionada
ultimo_tempo = time.time()  # Tempo do último pressionamento de tecla
tempo_cooldown = 0.5  # Tempo mínimo entre pressionamentos de tecla

# Layout do teclado virtual
teclas = [
    ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
    ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
    ["Z", "X", "C", "V", "B", "N", "M", ",", ".", ";"],
    ["SPACE", "BACKSPACE"]
]

# Configurações de layout para o teclado virtual
offset = 50  # Espaçamento inicial
button_width = 80  # Largura dos botões normais
button_height = 80  # Altura dos botões
espaco_width = 200  # Largura das teclas especiais

def encontra_coord(imagem):
    """
    Detecta e processa as mãos na imagem
    Retorna a imagem com as marcações e as coordenadas das mãos detectadas
    """
    imagem_rgb = cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB)
    resultado = hand.process(imagem_rgb)
    whole_hands = []

    if resultado.multi_hand_landmarks:
        for hand_side, hand_marking in zip(resultado.multi_handedness, resultado.multi_hand_landmarks):
            info_hand = {}
            coord = []

            for marking in hand_marking.landmark:
                coord_X = int(marking.x * resolution_x)
                coord_y = int(marking.y * resolution_y)
                coord_z = int(marking.z * resolution_x)
                coord.append((coord_X, coord_y, coord_z))

            info_hand["coord"] = coord
            info_hand["Lado"] = hand_side.classification[0].label
            whole_hands.append(info_hand)
            mp_desenho.draw_landmarks(imagem, hand_marking, mp_hand.HAND_CONNECTIONS)

    return imagem, whole_hands

def raised_fingers(hand):
    """
    Determina quais dedos estão levantados
    Retorna uma lista de booleanos indicando o estado de cada dedo
    """
    fingers = []
    # Verifica cada dedo (exceto o polegar)
    for ponta_finger in [8, 12, 16, 20]:
        if hand["coord"][ponta_finger][1] < hand["coord"][ponta_finger-2][1]:
            fingers.append(True)
        else:
            fingers.append(False)
    return fingers

def print_btn(imagem, position, texto, width=button_width, height=button_height, color=AZUL_CLARO):
    """
    Desenha um botão na imagem
    Retorna a imagem com o botão desenhado
    """
    # Adapta a largura para teclas especiais
    if texto in ["SPACE", "BACKSPACE"]:
        width = espaco_width
    
    # Desenha o retângulo do botão
    cv2.rectangle(imagem, position, (position[0]+width, position[1]+height), color, cv2.FILLED)
    cv2.rectangle(imagem, position, (position[0]+width, position[1]+height), CINZA_ESCURO, 2)
    
    # Ajusta o posicionamento do texto baseado no tamanho do botão
    if texto in ["SPACE", "BACKSPACE"]:
        text_x = position[0] + 10
    else:
        text_x = position[0] + width//4
    
    cv2.putText(imagem, texto, (text_x, position[1]+height//2+10), 
                cv2.FONT_HERSHEY_COMPLEX, 0.7, PRETO, 2)
    return imagem

def process_key_press(tecla, texto_atual):
    """
    Processa o pressionamento de teclas virtuais
    Retorna o texto atualizado após o pressionamento
    """
    if tecla == "SPACE":
        pyautogui.press("space")
        return texto_atual + " "
    elif tecla == "BACKSPACE":
        if len(texto_atual) > 1:  # Mantém pelo menos o ">" inicial
            pyautogui.press("backspace")
            return texto_atual[:-1]
        return texto_atual
    else:
        pyautogui.press(tecla.lower())
        return texto_atual + tecla

# Loop principal do programa
while True:
    sucesso, imagem = webcam.read()
    
    if not sucesso:
        break

    imagem = cv2.flip(imagem, 1)
    imagem, whole_hands = encontra_coord(imagem)
    
    # Desenha o texto digitado na parte superior da tela
    cv2.putText(imagem, texto, (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, BRANCO, 2)
    
    # Processa as mãos detectadas
    for hand_info in whole_hands:
        info_fingers = raised_fingers(hand_info)
        
        if hand_info["Lado"] == "Right":
            # Processamento da mão direita para controle de aplicativos
            pointer_x, pointer_y, pointer_z = hand_info["coord"][8]
            cv2.putText(imagem, f"Distância: {pointer_z}", (850, 50), cv2.FONT_HERSHEY_COMPLEX, 1, BRANCO, 2)
            
            # Diferentes gestos para abrir/fechar aplicativos
            if info_fingers == [True, False, False, False] and not notepad:
                notepad = True
                os.startfile(r"C:\Windows\System32\notepad.exe")
            if info_fingers == [True, True, False, False] and not chrome:
                chrome = True
                os.startfile(r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Google Chrome.lnk")
            if info_fingers == [True, True, True, False] and not calculator:
                calculator = True
                os.startfile(r"C:\Windows\System32\calc.exe")
            if info_fingers == [False, False, False, False]:
                if notepad:
                    notepad = False
                    os.system("TASKKILL /IM notepad.exe")
            if info_fingers == [True, False, False, True]:
                break  # Encerra o programa
        
        elif hand_info["Lado"] == "Left":
            # Processamento da mão esquerda para o teclado virtual
            indicador_x, indicador_y, indicador_z = hand_info["coord"][8]
            
            # Desenha o teclado virtual
            for indice_linha, linha_teclado in enumerate(teclas):
                for indice, tecla in enumerate(linha_teclado):
                    # Determina a posição do botão
                    if tecla in ["SPACE", "BACKSPACE"]:
                        pos_x = offset + indice * espaco_width
                    else:
                        pos_x = offset + indice * button_width
                    pos_y = offset + indice_linha * button_height
                    
                    # Verifica se o indicador está sobre a tecla
                    largura_tecla = espaco_width if tecla in ["SPACE", "BACKSPACE"] else button_width
                    if (pos_x < indicador_x < pos_x + largura_tecla and 
                        pos_y < indicador_y < pos_y + button_height):
                        # Tecla selecionada
                        cor_tecla = VERDE
                        
                        # Verifica se o dedo está próximo o suficiente para "pressionar" a tecla
                        if indicador_z < -85 and time.time() - ultimo_tempo > tempo_cooldown:
                            texto = process_key_press(tecla, texto)
                            ultimo_tempo = time.time()
                            cor_tecla = AZUL  # Muda a cor para indicar pressionamento
                    else:
                        cor_tecla = AZUL_CLARO
                    
                    # Desenha o botão
                    imagem = print_btn(imagem, (pos_x, pos_y), tecla, color=cor_tecla)
    
    # Mostra a imagem processada
    cv2.imshow("Teclado Virtual", imagem)
    
    # Verifica se a tecla ESC foi pressionada para encerrar o programa
    key = cv2.waitKey(1)
    if key == 27:  # 27 é o código ASCII da tecla ESC
        break

# Libera os recursos
webcam.release()
cv2.destroyAllWindows()