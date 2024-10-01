import cv2
import mediapipe as mp

# Inicializa os módulos de detecção de mãos e utilitários de desenho do MediaPipe
mp_hand = mp.solutions.hands
mp_desenho = mp.solutions.drawing_utils

# Cria um objeto para detectar mãos com as configurações padrão
hand = mp_hand.Hands()

# Inicializa a captura de vídeo da webcam
webcam = cv2.VideoCapture(0)

# Define a resolução da captura de vídeo
resolution_x = 1280
resolution_y = 720
webcam.set(cv2.CAP_PROP_FRAME_WIDTH, resolution_x)
webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution_y)

def encontra_coord(imagem, reverse_side=False):
    # Converte a imagem de BGR (formato padrão do OpenCV) para RGB (formato necessário para MediaPipe)
    imagem_rgb = cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB)

    # Processa a imagem para detectar mãos e suas marcações
    resultado = hand.process(imagem_rgb)
    whole_hands=[]

    # Verifica se há mãos detectadas
    if resultado.multi_hand_landmarks:
        # Itera sobre todas as mãos detectadas
        for hand_side, hand_marking in zip(resultado.multi_handedness, resultado.multi_hand_landmarks):
            info_hand={}  # Dicionário para armazenar as coordenadas da mão atual
            coord=[]  # Lista para armazenar as coordenadas dos pontos da mão

            # Itera sobre os landmarks (pontos) da mão
            for marking in hand_marking.landmark:
                # Calcula as coordenadas X, Y, Z escaladas de acordo com a resolução
                coord_X, coord_y, coord_z = int(marking.x * resolution_x), int(marking.y * resolution_y), int(marking.z * resolution_x)
                coord.append((coord_X, coord_y, coord_z))  # Armazena as coordenadas

            info_hand["coord"] = coord  # Armazena as coordenadas no dicionário
            if reverse_side:
                if hand_side.classification[0].label=="Left":
                    info_hand["Lado"]="Right"
                else:
                    info_hand["Lado"]="Left"
            else:
                info_hand["Lado"]=hand_side.classification[0].label
            print(info_hand["Lado"])
            whole_hands.append(info_hand)  # Adiciona a mão à lista de mãos

            # Desenha os pontos e as conexões das mãos detectadas
            mp_desenho.draw_landmarks(imagem, hand_marking, mp_hand.HAND_CONNECTIONS)

    # Retorna a imagem com os desenhos e as coordenadas das mãos
    return imagem, whole_hands

# Loop principal para capturar e processar o vídeo em tempo real
while True:
    # Captura um frame da webcam
    sucesso, imagem = webcam.read()
    
    imagem=cv2.flip(imagem, 1)
    
    # Se a captura falhar, pula para a próxima iteração
    if not sucesso:
        break
    
    # Chama a função para encontrar as coordenadas das mãos e processa a imagem
    imagem, whole_hands = encontra_coord(imagem)

    # Exibe o frame processado com as marcações de mãos na janela
    cv2.imshow("Câmera", imagem)

    # Aguarda 1 ms por uma tecla pressionada, se a tecla 'Esc' (código 27) for pressionada, sai do loop
    key = cv2.waitKey(1)
    if key == 27:
        break

# Libera a webcam e fecha todas as janelas abertas
webcam.release()
cv2.destroyAllWindows()