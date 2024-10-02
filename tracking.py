import cv2
import mediapipe as mp
import os

BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
AZUL = (255, 0, 0)
VERDE = (0, 255, 0)
VERMELHO = (0, 0, 255)
AZUL_CLARO = (255, 255, 0)

mp_hand = mp.solutions.hands
mp_desenho = mp.solutions.drawing_utils

hand = mp_hand.Hands()

webcam = cv2.VideoCapture(0)

resolution_x = 1280
resolution_y = 720
webcam.set(cv2.CAP_PROP_FRAME_WIDTH, resolution_x)
webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution_y)

notepad = False
chrome = False
calculator = False

def encontra_coord(imagem, reverse_side=False):
    imagem_rgb = cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB)
    resultado = hand.process(imagem_rgb)
    whole_hands = []

    if resultado.multi_hand_landmarks:
        for hand_side, hand_marking in zip(resultado.multi_handedness, resultado.multi_hand_landmarks):
            info_hand = {}
            coord = []

            for marking in hand_marking.landmark:
                coord_X, coord_y, coord_z = int(marking.x * resolution_x), int(marking.y * resolution_y), int(marking.z * resolution_x)
                coord.append((coord_X, coord_y, coord_z))

            info_hand["coord"] = coord
            
            if reverse_side:
                if hand_side.classification[0].label == "Left":
                    info_hand["Lado"] = "Right"
                else:
                    info_hand["Lado"] = "Left"
            else:
                info_hand["Lado"] = hand_side.classification[0].label

            whole_hands.append(info_hand)
            mp_desenho.draw_landmarks(imagem, hand_marking, mp_hand.HAND_CONNECTIONS)

    return imagem, whole_hands

def raised_fingers(hand):
    fingers = []
    for ponta_finger in [8, 12, 16, 20]:
        if hand["coord"][ponta_finger][1] < hand["coord"][ponta_finger-2][1]:
            fingers.append(True)
        else:
            fingers.append(False)
    return fingers

while True:
    sucesso, imagem = webcam.read()
    
    if not sucesso:
        break

    imagem = cv2.flip(imagem, 1)
    imagem, whole_hands = encontra_coord(imagem)
    
    cv2.rectangle(imagem, (50, 50), (100, 100), BRANCO, cv2.FILLED)
    cv2.putText(imagem, "Q", (65, 85), cv2.FONT_HERSHEY_COMPLEX, 1, PRETO, 2)

    if len(whole_hands) == 1:
        info_fingers1 = raised_fingers(whole_hands[0])
        if whole_hands[0]["Lado"] == "Right":
            if info_fingers1 == [True, False, False, False] and not notepad:
                notepad = True
                os.startfile(r"C:\Windows\System32\notepad.exe")
            if info_fingers1 == [True, True, False, False] and not chrome:
                chrome = True
                os.startfile(r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Google Chrome.lnk")
            if info_fingers1 == [True, True, True, False] and not calculator:
                calculator = True
                os.startfile(r"C:\Windows\System32\calc.exe")
            if info_fingers1 == [False, False, False, False] and notepad:
                notepad = False
                os.system("TASKKILL /IM notepad.exe")
            if info_fingers1 == [True, False, False, True]:
                break
    
    cv2.imshow("Câmera", imagem)

    key = cv2.waitKey(1)
    if key == 27:
        break

webcam.release()
cv2.destroyAllWindows()