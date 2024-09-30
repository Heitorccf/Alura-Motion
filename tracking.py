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

# Loop principal para capturar e processar o vídeo em tempo real
while True:
    # Captura um frame da webcam
    sucesso, imagem = webcam.read()

    # Converte a imagem de BGR (formato padrão do OpenCV) para RGB (formato necessário para MediaPipe)
    imagem_rgb = cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB)

    # Processa a imagem para detectar mãos e suas marcações
    resultado = hand.process(imagem_rgb)

    # Se houver mãos detectadas, desenha as marcações e conexões na imagem
    if resultado.multi_hand_landmarks:
        for hand_marking in resultado.multi_hand_landmarks:
            for marking in hand_marking.landmark:
                coord_X, coord_y, coord_z=int(marking.x*resolution_x), int(marking.y*resolution_y), int(marking.z*resolution_x)
                print(coord_X, coord_y, coord_z)
            # Desenha os pontos e as conexões das mãos detectadas
            mp_desenho.draw_landmarks(imagem, hand_marking, mp_hand.HAND_CONNECTIONS)

    # Exibe o frame processado com as marcações de mãos na janela "Câmera"
    cv2.imshow("Câmera", imagem)

    # Aguarda 1 ms por uma tecla pressionada, se a tecla 'Esc' (código 27) for pressionada, sai do loop
    key = cv2.waitKey(1)
    if key == 27:
        break

# Libera a webcam e fecha todas as janelas abertas
webcam.release()
cv2.destroyAllWindows()