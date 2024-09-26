import cv2
import mediapipe

webcam = cv2.VideoCapture(0)
resolution_x=1280
resolution_y=720
webcam.set(cv2.CAP_PROP_FRAME_WIDTH, resolution_x)
webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution_y)

while True:
   sucesso, imagem = webcam.read()
   cv2.imshow("Câmera", imagem)
   key = cv2.waitKey(1)
   if key==27:
      break