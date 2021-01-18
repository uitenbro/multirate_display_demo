# USAGE
# python facial_landmarks.py --shape-predictor shape_predictor_68_face_landmarks.dat --image images/example_01.jpg 

# import the necessary packages
#from imutils import face_utils
import numpy as np
import argparse
#import imutils
#import dlib
import cv2
import time
import math
import random

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-m", "--mode", required=False, default = "smooth",
  help="mode - smooth or random")
ap.add_argument("-s", "--speed", required=False, default = 5,
  help="percent - percent step per 20Hz frame (5\% default)")

args = vars(ap.parse_args())

# initialize 
#image = cv2.imread(args["image"])
originalImage = cv2.imread("tapes.png")
twentyHzLayer = np.zeros(originalImage.shape, dtype=originalImage.dtype)
thirteenHzLayer = np.zeros(originalImage.shape, dtype=originalImage.dtype)
tenHzLayer = np.zeros(originalImage.shape, dtype=originalImage.dtype)
fiveHzLayer = np.zeros(originalImage.shape, dtype=originalImage.dtype)
twoHzLayer = np.zeros(originalImage.shape, dtype=originalImage.dtype)
outputImage = np.zeros(originalImage.shape, dtype=originalImage.dtype)

barTotalHeight = 289 #pixels
barWidth = 20 # pixels

# Anchor coordinates
xOffset = 199
yOffset = 4

bar1BottomRightX = 122 + xOffset
bar1BottomRightY = 364 + yOffset
bar2BottomRightX = 324 + xOffset
bar2BottomRightY = 364 + yOffset
bar3BottomRightX = 526 + xOffset
bar3BottomRightY = 364 + yOffset
bar4BottomRightX = 728 + xOffset
bar4BottomRightY = 364 + yOffset
bar5BottomRightX = 929 + xOffset
bar5BottomRightY = 364 + yOffset

value1BottomLeftX = 74  + xOffset
value1BottomLeftY = 427 + yOffset
value2BottomLeftX = 275 + xOffset
value2BottomLeftY = 427 + yOffset
value3BottomLeftX = 475 + xOffset
value3BottomLeftY = 427 + yOffset
value4BottomLeftX = 676 + xOffset
value4BottomLeftY = 427 + yOffset
value5BottomLeftX = 878 + xOffset
value5BottomLeftY = 427 + yOffset

textOffset = 48 # pixels

speedBottomLeftX = 40 
speedBottomLeftY = 140

maxHeight = 100
maxDisplayValue = 15

speed = args["speed"]/100 #percent per 20Hz step
mode = args["mode"] #smooth or random

if mode == "smooth":
    height = 0
    sign = 1 #1 is up -1 is down)
else:
    height = 50
    sign = 0

def stepInput(mode, speed, prevHeight, sign):
    if (mode == "smooth"):
        nextHeight = height + sign*speed*maxHeight
        #print (nextHeight, sign)
    else: # mode = random
        randomSign = random.randrange(-1, 3) # set random up or down
        if (randomSign > 0): #up
            nextHeight = height + speed*maxHeight
        else: # down 
            nextHeight = height - speed*maxHeight
        #print(randomSign, nextHeight)

    if (nextHeight > maxHeight):
        nextHeight = maxHeight
        sign = -1 #change direction for smooth mode
    if (nextHeight < 0):
        nextHeight = 0
        sign = 1 #change direction smooth mode

    return (nextHeight, sign)    


def drawBar(id, height):
    heightPixels = int(barTotalHeight*height/100)
    #print(heightPixels)

    if (id == "1"):
        cv2.rectangle(twentyHzLayer, (bar1BottomRightX-barWidth, bar1BottomRightY-heightPixels), (bar1BottomRightX, bar1BottomRightY), (0, 255, 0), -1)
    elif (id == "2"):
        cv2.rectangle(thirteenHzLayer, (bar2BottomRightX-barWidth, bar2BottomRightY-heightPixels), (bar2BottomRightX, bar2BottomRightY), (0, 255, 0), -1)
    elif (id == "3"):
        cv2.rectangle(tenHzLayer, (bar3BottomRightX-barWidth, bar3BottomRightY-heightPixels), (bar3BottomRightX, bar3BottomRightY), (0, 255, 0), -1)
    elif (id == "4"):
        cv2.rectangle(eightHzLayer, (bar4BottomRightX-barWidth, bar4BottomRightY-heightPixels), (bar4BottomRightX, bar4BottomRightY), (0, 255, 0), -1)
    elif (id == "5"):
        cv2.rectangle(fiveHzLayer, (bar5BottomRightX-barWidth, bar5BottomRightY-heightPixels), (bar5BottomRightX, bar5BottomRightY), (0, 255, 0), -1)
    drawBarValueText(id, height)

def drawDisplayText(id, height):

    height = "{:2.1f}".format((maxDisplayValue*height/100))
    if (id == "1") or (id == "0"):
        cv2.putText(twoHzLayer, "{:>4}".format(height), (value1BottomLeftX, value1BottomLeftY),
            cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2)
    if (id == "2") or (id == "0"):
        cv2.putText(twoHzLayer, "{:>4}".format(height), (value2BottomLeftX, value2BottomLeftY),
            cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2)
    if (id == "3") or (id == "0"):
        cv2.putText(twoHzLayer, "{:>4}".format(height), (value3BottomLeftX, value3BottomLeftY),
            cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2)
    if (id == "4") or (id == "0"):
        cv2.putText(twoHzLayer, "{:>4}".format(height), (value4BottomLeftX, value4BottomLeftY),
            cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2)
    if (id == "5") or (id == "0"):
        cv2.putText(twoHzLayer, "{:>4}".format(height), (value5BottomLeftX, value5BottomLeftY),
            cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2)             

def drawTruthText(id, height):

    height = "{:2.1f}".format((maxDisplayValue*height/100))
    if (id == "1") or (id == "0"):
        cv2.putText(twentyHzLayer, "{:>4}".format(height), (value1BottomLeftX, value1BottomLeftY + 2*textOffset),
            cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2)
    if (id == "2") or (id == "0"):
        cv2.putText(twentyHzLayer, "{:>4}".format(height), (value2BottomLeftX, value2BottomLeftY + 2*textOffset),
            cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2)
    if (id == "3") or (id == "0"):
        cv2.putText(twentyHzLayer, "{:>4}".format(height), (value3BottomLeftX, value3BottomLeftY + 2*textOffset),
            cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2)
    if (id == "4") or (id == "0"):
        cv2.putText(twentyHzLayer, "{:>4}".format(height), (value4BottomLeftX, value4BottomLeftY + 2*textOffset),
            cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2)
    if (id == "5") or (id == "0"):
        cv2.putText(twentyHzLayer, "{:>4}".format(height), (value5BottomLeftX, value5BottomLeftY + 2*textOffset),
            cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2)             

def drawBarValueText(id, height):

    height = "{:2.1f}".format((maxDisplayValue*height/100)) 
    if (id == "1"):
        cv2.putText(twentyHzLayer, "{:>4}".format(height), (value1BottomLeftX, value1BottomLeftY + textOffset),
            cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2)
    elif (id == "2"):
        cv2.putText(thirteenHzLayer, "{:>4}".format(height), (value2BottomLeftX, value2BottomLeftY + textOffset),
            cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2)
    elif (id == "3"):
        cv2.putText(tenHzLayer, "{:>4}".format(height), (value3BottomLeftX, value3BottomLeftY + textOffset),
            cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2)
    elif (id == "4"):
        cv2.putText(eightHzLayer, "{:>4}".format(height), (value4BottomLeftX, value4BottomLeftY + textOffset),
            cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2)
    elif (id == "5"):
        cv2.putText(fiveHzLayer, "{:>4}".format(height), (value5BottomLeftX, value5BottomLeftY + textOffset),
            cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2)             

def drawSpeedText(speed):

    speedText = "{:2.0f}".format(speed*100)
    cv2.putText(twentyHzLayer, "{:>4}".format(speedText), (speedBottomLeftX, speedBottomLeftY),
        cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2)

def mergeLayers():
    #print(twentyHzLayer.shape, twentyHzLayer1.shape)
    #outputImage = cv2.addWeighted(twentyHzLayer, .5, originalImage, .5, 0) # outputImage)
    #outputImage = 0.5*twentyHzLayer[:,:,:] + 0.5*twentyHzLayer1[:,:,:]

    print(outputImage.shape)
    print(outputImage[0])
    return outputImage

def run40HzStep(frame):
    startTime = time.time()
    #print(startTime)
    global mode
    global speed
    global height
    global sign
    global twentyHzLayer
    global thirteenHzLayer
    global tenHzLayer
    global eightHzLayer
    global fiveHzLayer
    global twoHzLayer
    global outputImage


    frameInfo = ""

    if (frame % 2) != 0: # 20Hz
        frameInfo += " 20Hz"
        #update data input
        (height, sign) = stepInput(mode, speed, height, sign)

        #capture mask of current 20 Hz Layer and restore the outputImage
        mask = twentyHzLayer.copy()
        outputImage[mask >0] = originalImage[mask>0]

        #reset 20Hz layer to zero 
        twentyHzLayer = np.zeros(originalImage.shape, dtype=originalImage.dtype)
        #draw 20 Hz elements
        drawBar("1", height)

        drawSpeedText(speed)
        #drawTruthText("1", height)
    if (frame % 3) == 0:
        frameInfo += " 13Hz"
        thirteenHzLayer = np.zeros(originalImage.shape, dtype=originalImage.dtype)
        drawBar("2", height)
        #drawTruthText("2", height)
    if (frame % 4) == 0:
        frameInfo += " 10Hz"
        tenHzLayer = np.zeros(originalImage.shape, dtype=originalImage.dtype)
        drawBar("3", height)
        #drawTruthText("3", height)
    if (frame %5) == 0:
        frameInfo += " 8Hz"
        eightHzLayer = np.zeros(originalImage.shape, dtype=originalImage.dtype)
        drawBar("4", height)   
        #drawTruthText("4", height)
    if (frame %8) == 0:
        frameInfo += " 8Hz"
        fiveHzLayer = np.zeros(originalImage.shape, dtype=originalImage.dtype)
        drawBar("5", height)
        #drawTruthText("5", height)
    if (frame % 20) == 0: # 2Hz
        frameInfo += " 2Hz"
        #reset 20Hz layer to zero 
        twoHzLayer = np.zeros(originalImage.shape, dtype=originalImage.dtype)
        drawDisplayText("0", height)

    #get 20Hz layer mask restore areas that aren't going to be filled to original image
    mask = twentyHzLayer.copy()
    outputImage[mask == 0] = originalImage[mask == 0]
    #overlay 20Hz layer
    outputImage[mask > 0] = twentyHzLayer[mask > 0]

    #get 13.3Hz layer mask and overlay 2Hz layer
    mask = thirteenHzLayer.copy()
    outputImage[mask > 0] = thirteenHzLayer[mask > 0]
    #get 10Hz layer mask and overlay 2Hz layer
    mask = tenHzLayer.copy()
    outputImage[mask > 0] = tenHzLayer[mask > 0]
    #get 8Hz layer mask and overlay 2Hz layer
    mask = eightHzLayer.copy()
    outputImage[mask > 0] = eightHzLayer[mask > 0]
    #get 5Hz layer mask and overlay 2Hz layer
    mask = fiveHzLayer.copy()
    outputImage[mask > 0] = fiveHzLayer[mask > 0]
    #get 2Hz layer mask and overlay 2Hz layer
    mask = twoHzLayer.copy()
    outputImage[mask > 0] = twoHzLayer[mask > 0]

    # cv2.imshow("thirteenHzLayer", thirteenHzLayer)
    # cv2.waitKey(1)

    # cv2.imshow("tenHzLayer", tenHzLayer)
    # cv2.waitKey(1)

    cv2.imshow("Refresh Rate Model", outputImage)
    key = cv2.waitKey(1)
    if key == 32: #spacebar
        print("spacebar")
        cv2.waitKey(0)
    elif key == ord('r'):
        mode = "random"
        height = 50
    elif key == ord('s'):
        mode = "smooth"
        sign = 1
        height = 0
    elif key == ord('+') or key == ord('='):
        speed += .01
        if speed >= 1:
            speed = 1 
            print(speed)
    elif key == ord('-') :
        speed -= .01
        if speed <= 0: 
            speed = .01
            print(speed)
    elif key == 27:
        exit()




    elapsed = time.time()-startTime
    if elapsed < (.025):
        time.sleep(.025-elapsed)
        elapsed = time.time()-startTime
        frameInfo = " {:>3} msec".format(math.floor(elapsed*1000)) + frameInfo
    else:
        frameInfo = " {:>3} msec".format(math.floor(elapsed*1000)) + " *overrun {:>3} msec*".format(math.floor((elapsed-0.025)*1000)) + frameInfo

        frameInfo = "{:>3}:".format(frame) + frameInfo
        print(frameInfo)

x = 100000    
frameCountMax = 120 #set up 3 sec major frame 25msec * 120 = 3 sec
frame = 0


while x > 0:

    run40HzStep(frame)

    frame+=1
    if frame >= 120:
        frame = 0

    x-=1




