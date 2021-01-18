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
ap.add_argument("-s", "--speed", required=False, default = 1,
  help="seconds - time to travers full range")

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

modelRateBottomLeftX = 45
modelRateBottomLeftY = 100

speedBottomLeftX = 35 
speedBottomLeftY = 235

toleranceBottomLeftX = 45
toleranceBottomLeftY = 370

bar1LabelX = 230
bar2LabelX = 430
bar3LabelX = 640
bar4LabelX = 840
bar5LabelX = 1040

bar1LabelY = 45
bar2LabelY = 45
bar3LabelY = 45
bar4LabelY = 45
bar5LabelY = 45

maxHeight = 100
maxDisplayValue = 15

bar1Height = 0
bar2Height = 0
bar3Height = 0
bar4Height = 0
bar5Height = 0

def initRates(nativeRate):
    # (bar1Modulo, bar2Modulo, bar3Modulo, bar4Modulo, bar5Modulo, twoHzModulo, loopMax)
    if nativeRate >= 40:
        return (2, 3, 4, 5, 8, 20, 120) #    20, 13, 10, 8,        5
    elif nativeRate >= 30:
        return (1, 2, 3, 4, 6, 15, 300) # 30,  15,   10,  7.5,     5
    elif nativeRate >= 25:
        return (1, 2, 3, 4, 5, 12, 600) #   25,  12.5, 8.3,   6.2, 5
    elif nativeRate >= 20:
        return (1, 2, 3, 4, 5, 10, 60)  #    20,     10,    6.7,   5, 4

tolerance = .05
nativeRate = 25.0 #Hz
period = 1/nativeRate
(bar1Modulo, bar2Modulo, bar3Modulo, bar4Modulo, bar5Modulo, twoHzModulo, loopMax) = initRates(nativeRate)


def stepRate():
    global nativeRate
    global period
    global bar1Modulo, bar2Modulo, bar3Modulo, bar4Modulo, bar5Modulo, twoHzModulo, loopMax

    if nativeRate == 40:
        nativeRate = 30
    elif nativeRate == 30:
        nativeRate = 25
    elif nativeRate == 25:
        nativeRate = 20    
    elif nativeRate == 20:
        nativeRate = 40
    period = 1/nativeRate
    (bar1Modulo, bar2Modulo, bar3Modulo, bar4Modulo, bar5Modulo, twoHzModulo, loopMax) = initRates(nativeRate)


speed = args["speed"] 
mode = args["mode"] #smooth or random

if mode == "smooth":
    height = 0
    sign = 1 #1 is up -1 is down)
else:
    height = 50
    sign = 0



def stepInput(mode, speed, prevHeight, sign):
    # speed = seconds to traverse full range (sec/100%)
    # height range 0 - 100%
    if speed == 0:
        speedMultiplier = 1 # full scale (flashing)
    else:
        speedMultiplier = (bar1Modulo/nativeRate)/speed

    if (mode == "smooth"):
        nextHeight = height + sign*speedMultiplier*maxHeight
        #print (nextHeight, sign)
    else: # mode = random
        randomSign = random.randrange(-1, 3) # set random up or down
        if (randomSign > 0): #up
            nextHeight = height + speedMultiplier*maxHeight
        else: # down 
            nextHeight = height - speedMultiplier*maxHeight
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
    global bar1Height, bar2Height, bar3Height, bar4Height, bar5Height

    if (id == "1"):
        cv2.rectangle(twentyHzLayer, (bar1BottomRightX-barWidth, bar1BottomRightY-heightPixels), (bar1BottomRightX, bar1BottomRightY), (0, 255, 0), -1)
        bar1Height = height
    elif (id == "2"):
        cv2.rectangle(thirteenHzLayer, (bar2BottomRightX-barWidth, bar2BottomRightY-heightPixels), (bar2BottomRightX, bar2BottomRightY), (0, 255, 0), -1)
        bar2Height = height
    elif (id == "3"):
        cv2.rectangle(tenHzLayer, (bar3BottomRightX-barWidth, bar3BottomRightY-heightPixels), (bar3BottomRightX, bar3BottomRightY), (0, 255, 0), -1)
        bar3Height = height
    elif (id == "4"):
        cv2.rectangle(eightHzLayer, (bar4BottomRightX-barWidth, bar4BottomRightY-heightPixels), (bar4BottomRightX, bar4BottomRightY), (0, 255, 0), -1)
        bar4Height = height
    elif (id == "5"):
        cv2.rectangle(fiveHzLayer, (bar5BottomRightX-barWidth, bar5BottomRightY-heightPixels), (bar5BottomRightX, bar5BottomRightY), (0, 255, 0), -1)
        bar5Height = height
    drawBarValueText(id, height)
    #print("u: ", bar1Height, bar2Height, bar3Height, bar4Height, bar5Height)

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

def drawErrorText():
    global bar1Height, bar2Height, bar3Height, bar4Height, bar5Height
    #print("e: ", bar1Height, bar2Height, bar3Height, bar4Height, bar5Height)
    #print("e: ", bar1Height-bar1Height, bar1Height-bar2Height, bar1Height-bar3Height, bar1Height-bar4Height, bar1Height-bar5Height)
    
    bar1Error = abs(bar1Height - bar1Height)
    bar1ErrorText = "{:2.0f}%".format(bar1Error)
    if bar1Error > tolerance*100:
        color = (0, 254,254)
        cv2.circle(twentyHzLayer, (value1BottomLeftX-5, (value1BottomLeftY-10) + 2*textOffset), 10, color, -1)
    else:
        color = (255, 255, 255)
    cv2.putText(twentyHzLayer, "{}".format(bar1ErrorText), (value1BottomLeftX, value1BottomLeftY + 2*textOffset),
            cv2.FONT_HERSHEY_SIMPLEX, 1.25, color, 2)
    
    bar2Error = abs(bar1Height - bar2Height)
    bar2ErrorText = "{:2.0f}%".format(bar2Error)
    if bar2Error > tolerance*100:
        color = (0, 254,254)
        cv2.circle(twentyHzLayer, (value2BottomLeftX-5, (value2BottomLeftY-10) + 2*textOffset), 10, color, -1)
    else:
        color = (255, 255, 255)
    cv2.putText(twentyHzLayer, "{}".format(bar2ErrorText), (value2BottomLeftX, value2BottomLeftY + 2*textOffset),
            cv2.FONT_HERSHEY_SIMPLEX, 1.25, color, 2)

    bar3Error = abs(bar1Height - bar3Height)
    bar3ErrorText = "{:2.0f}%".format(bar3Error)
    if bar3Error > tolerance*100:
        color = (0, 254,254)
        cv2.circle(twentyHzLayer, (value3BottomLeftX-5, (value3BottomLeftY-10) + 2*textOffset), 10, color, -1)
    else:
        color = (255, 255, 255)        
    cv2.putText(twentyHzLayer, "{}".format(bar3ErrorText), (value3BottomLeftX, value3BottomLeftY + 2*textOffset),
            cv2.FONT_HERSHEY_SIMPLEX, 1.25, color, 2)

    bar4Error = abs(bar1Height - bar4Height)
    bar4ErrorText = "{:2.0f}%".format(bar4Error)
    if bar4Error > tolerance*100:
        color = (0, 254,254)
        cv2.circle(twentyHzLayer, (value4BottomLeftX-5, (value4BottomLeftY-10) + 2*textOffset), 10, color, -1)
    else:
        color = (255, 255, 255)
    cv2.putText(twentyHzLayer, "{}".format(bar4ErrorText), (value4BottomLeftX, value4BottomLeftY + 2*textOffset),
            cv2.FONT_HERSHEY_SIMPLEX, 1.25, color, 2)

    bar5Error = abs(bar1Height - bar5Height)
    bar5ErrorText = "{:2.0f}%".format(bar5Error)
    if bar5Error > tolerance*100:
        color = (0, 254,254)
        cv2.circle(twentyHzLayer, (value5BottomLeftX-5, (value5BottomLeftY-10) + 2*textOffset), 10, color, -1)
    else:
        color = (255, 255, 255)
    cv2.putText(twentyHzLayer, "{}".format(bar5ErrorText), (value5BottomLeftX, value5BottomLeftY + 2*textOffset),
            cv2.FONT_HERSHEY_SIMPLEX, 1.25, color, 2)             

def drawBarValueText(id, height):

    heightText = "{:2.0f}%".format(height) 
    if (id == "1"):
        cv2.putText(twentyHzLayer, "{:>4}".format(heightText), (value1BottomLeftX, value1BottomLeftY + textOffset),
            cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2)
    elif (id == "2"):
        cv2.putText(thirteenHzLayer, "{:>4}".format(heightText), (value2BottomLeftX, value2BottomLeftY + textOffset),
            cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2)
    elif (id == "3"):
        cv2.putText(tenHzLayer, "{:>4}".format(heightText), (value3BottomLeftX, value3BottomLeftY + textOffset),
            cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2)
    elif (id == "4"):
        cv2.putText(eightHzLayer, "{:>4}".format(heightText), (value4BottomLeftX, value4BottomLeftY + textOffset),
            cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2)
    elif (id == "5"):
        cv2.putText(fiveHzLayer, "{:>4}".format(heightText), (value5BottomLeftX, value5BottomLeftY + textOffset),
            cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2)             

def drawLabelsSettings(speed):

    modelRateText = "{:2.1f} Hz".format(nativeRate)
    cv2.putText(twoHzLayer, "{:>5}".format(modelRateText), (modelRateBottomLeftX, modelRateBottomLeftY),
        cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2)

    speedText = "{:1.2f} sec".format(speed)
    cv2.putText(twoHzLayer, "{: >8}".format(speedText), (speedBottomLeftX, speedBottomLeftY),
        cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2)
    toleranceText = "{:.0f}%".format(tolerance*100)
    cv2.putText(twoHzLayer, "{: >4}".format(toleranceText), (toleranceBottomLeftX, toleranceBottomLeftY),
        cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2)

    bar1RateText = "{:2.1f} Hz".format(nativeRate/bar1Modulo)
    cv2.putText(twoHzLayer, "{:>5}".format(bar1RateText), (bar1LabelX, bar1LabelY),
        cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2)
    bar2RateText = "{:2.1f} Hz".format(nativeRate/bar2Modulo)
    cv2.putText(twoHzLayer, "{:>5}".format(bar2RateText), (bar2LabelX, bar2LabelY),
        cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2)
    bar3RateText = "{:2.1f} Hz".format(nativeRate/bar3Modulo)
    cv2.putText(twoHzLayer, "{:>5}".format(bar3RateText), (bar3LabelX, bar3LabelY),
        cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2)
    bar4RateText = "{:2.1f} Hz".format(nativeRate/bar4Modulo)
    cv2.putText(twoHzLayer, "{:>5}".format(bar4RateText), (bar4LabelX, bar4LabelY),
        cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2)
    bar5RateText = "{:2.1f} Hz".format(nativeRate/bar5Modulo)
    cv2.putText(twoHzLayer, "{:>5}".format(bar5RateText), (bar5LabelX, bar5LabelY),
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
    global tolerance
    global height
    global sign
    global twentyHzLayer
    global thirteenHzLayer
    global tenHzLayer
    global eightHzLayer
    global fiveHzLayer
    global twoHzLayer
    global outputImage
    #global bar1Modulo bar2Modulo bar3Modulo bar4Modulo loopMax

    frameInfo = ""

    if (frame % bar1Modulo) == 0: 
        frameInfo += " {:0.2f}Hz".format(nativeRate/bar1Modulo)
        #update data input
        (height, sign) = stepInput(mode, speed, height, sign)

        #capture mask of current 20 Hz Layer and restore the outputImage
        mask = twentyHzLayer.copy()
        outputImage[mask >0] = originalImage[mask>0]

        #reset 20Hz layer to zero 
        twentyHzLayer = np.zeros(originalImage.shape, dtype=originalImage.dtype)
        #draw 20 Hz elements
        drawBar("1", height)

    if (frame % bar2Modulo) == 0:
        frameInfo += " {:0.2f}Hz".format(nativeRate/bar2Modulo)
        thirteenHzLayer = np.zeros(originalImage.shape, dtype=originalImage.dtype)
        drawBar("2", height)
        #drawTruthText("2", height)
    if (frame % bar3Modulo) == 0:
        frameInfo += " {:0.2f}Hz".format(nativeRate/bar3Modulo)
        tenHzLayer = np.zeros(originalImage.shape, dtype=originalImage.dtype)
        drawBar("3", height)
        #drawTruthText("3", height)
    if (frame % bar4Modulo) == 0:
        frameInfo += " {:0.2f}Hz".format(nativeRate/bar4Modulo)
        eightHzLayer = np.zeros(originalImage.shape, dtype=originalImage.dtype)
        drawBar("4", height)   
        #drawTruthText("4", height)
    if (frame % bar5Modulo) == 0:
        frameInfo += " {:0.2f}Hz".format(nativeRate/bar5Modulo)
        fiveHzLayer = np.zeros(originalImage.shape, dtype=originalImage.dtype)
        drawBar("5", height)
        #drawTruthText("5", height)
    if (frame % twoHzModulo) == 0: # 2Hz
        frameInfo += " {:0.2f}Hz".format(nativeRate/twoHzModulo)
        #reset 20Hz layer to zero 
        twoHzLayer = np.zeros(originalImage.shape, dtype=originalImage.dtype)
        drawDisplayText("0", height)
        drawLabelsSettings(speed)

    drawErrorText()

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
    elif key == ord('-'):
        speed += 0.25
        if speed >= 10:
            speed = 10 
            print(speed)
    elif key == ord('+') or key == ord('='):
        speed -= 0.25
        if speed <= 0: 
            speed = 0
            #print(speed)
    elif key == ord(']'):
        tolerance += 0.01
        if tolerance >= .10:
            tolerance = .10 
    elif key == ord('[') :
        tolerance -= 0.01
        if tolerance <= 0: 
            tolerance = 0
            #print(speed)
    elif key == ord('n'):
        stepRate() 
    elif key == 27:
        exit()

    elapsed = time.time()-startTime
    if elapsed < (period):
        time.sleep(period-elapsed)
        elapsed = time.time()-startTime
        frameInfo = " {:>3} msec".format(math.floor(elapsed*1000)) + frameInfo
        frameInfo = "{:>3}:".format(frame) + frameInfo
    else:
        frameInfo = " {:>3} msec".format(math.floor(elapsed*1000)) + frameInfo + " *overrun* {:>3} msec".format(math.floor((elapsed-period)*1000))
        frameInfo = "{:>3}:".format(frame) + frameInfo

        print(frameInfo)

x = 100000    
frame = 0

while x > 0:

    run40HzStep(frame)

    frame+=1
    if frame >= loopMax:
        frame = 0

    x-=1




