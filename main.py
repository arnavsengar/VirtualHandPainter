import cv2
import numpy as np
import os
import HandTrackingModule as htm
from cvzone.HandTrackingModule import HandDetector
import cvzone
from pynput.keyboard import Controller
from time import sleep
import math
###############
brushThickness=10
eraserThickness=20
############
folderPath = "Heads"
myList = os.listdir(folderPath)
#print(myList)
overlayList=[]
for imPath in myList:
    image=cv2.imread(f'{folderPath}/{imPath}')
    overlayList.append(image)

header=overlayList[0]
drawColor=(255,0,255)


cap=cv2.VideoCapture(0)

cap.set(3,1280)
cap.set(4,720)

detector=htm.handDetector(detectionCon=0.85)
detector1=HandDetector(detectionCon=0.8)
xp,yp=0,0
keys = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
        ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"]]
finalText = ""
keyboard = Controller()
imgCanvas=np.zeros((720,1280,3),np.uint8)

def drawAll (img , buttonList) :
    for button in buttonList:
        x, y = button.pos
        w, h = button.size
        cvzone.cornerRect(img, (button.pos[0], button.pos[1], button.size[0], button.size[1]),
                          20, rt=0)
        cv2.rectangle(img, button.pos, (x + w, y + h), (0, 0,0), cv2.FILLED)
        cv2.putText(img, button.text, (x + 20, y + 65),
                    cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 4)
    return img

keyboards=False
class Button():
    def __init__(self, pos, text, size=[85, 85]):
        self.pos = pos
        self.size = size
        self.text = text


buttonList = []
for i in range(len(keys)):
    for j, key in enumerate(keys[i]):
        buttonList.append(Button([100 * j + 120, 100 * i + 100], key))


while True:
    # Import Images
    success, img=cap.read()
    img=cv2.flip(img,1)

    # find hand landmarks
    img=detector.findHands(img,draw=False)
    lmList=detector.findPosition(img,draw=False)

    if len(lmList)!=0:

        #print(lmList)

        #tip of index & middle finger
        x1,y1=lmList[8][1:]
        x2, y2 = lmList[12][1:]


    # check which finger are up

        fingers = detector.fingersUp()
        #print(fingers)

    # if selection mode 2 fingers

        if fingers[1] and fingers[2]:
            xp, yp = 0, 0
            #print("Selection mode")
            #checking Selection
            if y1<80:
                if 175<x1<275:
                    header=overlayList[0]
                    drawColor=(255,0,255)
                    keyboards = False
                elif 350<x1<450:
                    header=overlayList[1]
                    drawColor = (255, 0, 0)
                    keyboards = False
                elif 515<x1<615:
                    header=overlayList[2]
                    drawColor = (0, 255, 0)
                    keyboards = False
                elif 665<x1<770:
                    header=overlayList[3]
                    drawColor = (0, 0,0)
                    keyboards = False
                elif 810<x1<922:
                    cv2.rectangle(imgCanvas,(0,0),(1280,720),(0,0,0),cv2.FILLED)
                    keyboards = False
                elif 930<x1<1030:
                    keyboards=True
            if keyboards==True:
                img = drawAll(img, buttonList)


                if lmList:
                    #print(lmList)
                    for button in buttonList:
                        x, y = button.pos
                        w, h = button.size


                        if x < lmList[8][1] < x + w and y < lmList[8][2] < y + h:
                            #print("yes")
                            cv2.rectangle(img, button.pos, (x + w , y + h ), (255, 255, 255), cv2.FILLED)
                            cv2.putText(img, button.text, (x + 20, y + 65),
                                        cv2.FONT_HERSHEY_PLAIN, 4, (0, 0, 0), 4)
                            xs1, ys1 = lmList[8][1], lmList[8][2]
                            xs2, ys2 = lmList[12][1], lmList[12][2]
                            l = math.hypot(xs2 - xs1, ys2 - ys1)
                            #print(l)

                            ## when clicked
                            if l < 45:
                                keyboard.press(button.text)
                                cv2.rectangle(img, button.pos, (x + w, y + h), (255, 255, 255), cv2.FILLED)
                                cv2.putText(img, button.text, (x + 20, y + 65),
                                            cv2.FONT_HERSHEY_PLAIN, 4, (0, 0, 0), 4)
                                finalText += button.text
                                sleep(0.10)

                cv2.rectangle(img, (100, 500), (1000, 580), (0,0,0), cv2.FILLED)
                cv2.putText(img, finalText, (110, 550),
                            cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)



            cv2.rectangle(img, (x1, y1 - 25), (x2, y2 + 25), drawColor, cv2.FILLED)

        # if draw mode 1 finger
        if fingers[1] and fingers[2]==False and fingers[0]==1:

            cv2.circle(img,(x1,y1),15,drawColor,cv2.FILLED)
            #print("Drawing Mode")

            if xp==0 and yp==0:
                xp,yp=x1,y1

            if drawColor==(0,0,0):
                cv2.line(img, (xp, yp), (x1, y1), drawColor, eraserThickness)
                cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, eraserThickness)
            else:
                cv2.line(img, (xp,yp),(x1,y1),drawColor,brushThickness)
                cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, brushThickness)

            xp,yp=x1,y1

        if fingers[1] and fingers[0]==0 and fingers[2]==0:
            #print("Brush size")
            xp, yp = 0, 0
            xs1, ys1 = lmList[4][1], lmList[4][2]
            xs2, ys2 = lmList[8][1], lmList[8][2]
            cx,cy=(xs1+xs2)//2,(ys1+ys2)//2
            cv2.circle(img, (xs1, ys1), 5, drawColor, cv2.FILLED)
            cv2.circle(img, (xs2, ys2), 5, drawColor, cv2.FILLED)
            cv2.line(img,(xs1,ys1),(xs2,ys2),drawColor,3)



            length=math.hypot(xs2-xs1,ys2-ys1)
            if length<50:
                cv2.circle(img, (cx, cy), 10, (0,0,255), cv2.FILLED)
            #print(length)
            if length>50 and drawColor!=(0,0,0):
                brushThickness=round(length/3)
                cv2.circle(img, (cx, cy), brushThickness, drawColor, cv2.FILLED)
                cv2.putText(img,"Value:"+str(brushThickness),(1100,40),cv2.FONT_HERSHEY_PLAIN,2,drawColor,2)
            elif length>50 and drawColor==(0,0,0):
                eraserThickness=round(length/2)
                cv2.circle(img, (cx, cy), eraserThickness, drawColor, cv2.FILLED)
                cv2.putText(img, "Value:" + str(eraserThickness), (1100, 40), cv2.FONT_HERSHEY_PLAIN, 2, drawColor,2)



    imgGray=cv2.cvtColor(imgCanvas,cv2.COLOR_BGR2GRAY)
    _, imgInv=cv2.threshold(imgGray,50,255,cv2.THRESH_BINARY_INV)

    imgInv=cv2.cvtColor(imgInv,cv2.COLOR_GRAY2BGR)
    img=cv2.bitwise_and(img,imgInv)
    img = cv2.bitwise_or(img, imgCanvas)

    img[0:79, 0:923]=header
    #img=cv2.addWeighted(img,0.5,imgCanvas,0.5,0)
    cv2.imshow("okay" ,img)
    #cv2.imshow("canva",imgCanvas)
    cv2.waitKey(1)
