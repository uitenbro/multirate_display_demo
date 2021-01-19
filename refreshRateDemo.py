# USAGE
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
ap.add_argument("-s", "--speed", required=False, default = 2,
  help="seconds - time to travers full range")

args = vars(ap.parse_args())

# initialize 
#image = cv2.imread(args["image"])
originalImage = cv2.imread("tapes.png")
bar1Layer = np.zeros(originalImage.shape, dtype=originalImage.dtype)
bar2Layer = np.zeros(originalImage.shape, dtype=originalImage.dtype)
bar3Layer = np.zeros(originalImage.shape, dtype=originalImage.dtype)
bar5Layer = np.zeros(originalImage.shape, dtype=originalImage.dtype)
twoHzLayer = np.zeros(originalImage.shape, dtype=originalImage.dtype)
errorLayer = np.zeros(originalImage.shape, dtype=originalImage.dtype)
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
nativeRate = 30.0 #Hz
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

    if (mode == "smooth") or (mode == "target"):
        nextHeight = height + sign*speedMultiplier*maxHeight
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
    targetHeight = int(11/15*barTotalHeight)

    if (id == "1"):
        cv2.rectangle(bar1Layer, (bar1BottomRightX-barWidth, bar1BottomRightY-heightPixels), (bar1BottomRightX, bar1BottomRightY), (0, 255, 0), -1)
        bar1Height = height
        if mode == "target":
            cnt = np.array([(bar1BottomRightX, bar1BottomRightY-targetHeight),
                (bar1BottomRightX+15, bar1BottomRightY-targetHeight-8),(bar1BottomRightX+15, bar1BottomRightY-targetHeight+8)])
            cv2.drawContours(bar1Layer, [cnt], 0, (147, 20, 255), -1)
    elif (id == "2"):
        cv2.rectangle(bar2Layer, (bar2BottomRightX-barWidth, bar2BottomRightY-heightPixels), (bar2BottomRightX, bar2BottomRightY), (0, 255, 0), -1)
        bar2Height = height
        if mode == "target":
            cnt = np.array([(bar2BottomRightX, bar2BottomRightY-targetHeight),
                (bar2BottomRightX+15, bar2BottomRightY-targetHeight-8),(bar2BottomRightX+15, bar2BottomRightY-targetHeight+8)])
            cv2.drawContours(bar2Layer, [cnt], 0, (147, 20, 255), -1)
    elif (id == "3"):
        cv2.rectangle(bar3Layer, (bar3BottomRightX-barWidth, bar3BottomRightY-heightPixels), (bar3BottomRightX, bar3BottomRightY), (0, 255, 0), -1)
        bar3Height = height
        if mode == "target":
            cnt = np.array([(bar3BottomRightX, bar3BottomRightY-targetHeight),
                (bar3BottomRightX+15, bar3BottomRightY-targetHeight-8),(bar3BottomRightX+15, bar3BottomRightY-targetHeight+8)])
            cv2.drawContours(bar3Layer, [cnt], 0, (147, 20, 255), -1)        
    elif (id == "4"):
        cv2.rectangle(bar4Layer, (bar4BottomRightX-barWidth, bar4BottomRightY-heightPixels), (bar4BottomRightX, bar4BottomRightY), (0, 255, 0), -1)
        bar4Height = height
        if mode == "target":
            cnt = np.array([(bar4BottomRightX, bar4BottomRightY-targetHeight),
                (bar4BottomRightX+15, bar4BottomRightY-targetHeight-8),(bar4BottomRightX+15, bar4BottomRightY-targetHeight+8)])
            cv2.drawContours(bar4Layer, [cnt], 0, (147, 20, 255), -1)        
    elif (id == "5"):
        cv2.rectangle(bar5Layer, (bar5BottomRightX-barWidth, bar5BottomRightY-heightPixels), (bar5BottomRightX, bar5BottomRightY), (0, 255, 0), -1)
        bar5Height = height
        if mode == "target":
            cnt = np.array([(bar5BottomRightX, bar5BottomRightY-targetHeight),
                (bar5BottomRightX+15, bar5BottomRightY-targetHeight-8),(bar5BottomRightX+15, bar5BottomRightY-targetHeight+8)])
            cv2.drawContours(bar5Layer, [cnt], 0, (147, 20, 255), -1)

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
    global errorLayer
    #print(bar1Height, bar2Height, bar3Height, bar4Height, bar5Height)

    if mode == "target":
        truth = 11/15*100
    else:
        truth = bar1Height
    #print(truth-bar1Height, truth-bar2Height, truth-bar3Height, truth-bar4Height, truth-bar5Height)
    
    #clear error layer
    errorLayer = np.zeros(originalImage.shape, dtype=originalImage.dtype)

    bar1Error = abs(truth - bar1Height)
    bar1ErrorText = "{:2.1f}%".format(bar1Error)
    if bar1Error > tolerance*100:
        color = (0, 254,254)
        cv2.circle(errorLayer, (value1BottomLeftX-10, (value1BottomLeftY-15) + 2*textOffset), 10, color, -1)
    else:
        color = (255, 255, 255)
    cv2.putText(errorLayer, "{:>4}".format(bar1ErrorText), (value1BottomLeftX, value1BottomLeftY + 2*textOffset),
            cv2.FONT_HERSHEY_SIMPLEX, 1.25, color, 2)
    
    bar2Error = abs(truth - bar2Height)
    bar2ErrorText = "{:2.1f}%".format(bar2Error)
    if bar2Error > tolerance*100:
        color = (0, 254,254)
        cv2.circle(errorLayer, (value2BottomLeftX-10, (value2BottomLeftY-15) + 2*textOffset), 10, color, -1)
    else:
        color = (255, 255, 255)
    cv2.putText(errorLayer, "{:>4}".format(bar2ErrorText), (value2BottomLeftX, value2BottomLeftY + 2*textOffset),
            cv2.FONT_HERSHEY_SIMPLEX, 1.25, color, 2)

    bar3Error = abs(truth - bar3Height)
    bar3ErrorText = "{:2.1f}%".format(bar3Error)
    if bar3Error > tolerance*100:
        color = (0, 254,254)
        cv2.circle(errorLayer, (value3BottomLeftX-10, (value3BottomLeftY-15) + 2*textOffset), 10, color, -1)
    else:
        color = (255, 255, 255)        
    cv2.putText(errorLayer, "{:>4}".format(bar3ErrorText), (value3BottomLeftX, value3BottomLeftY + 2*textOffset),
            cv2.FONT_HERSHEY_SIMPLEX, 1.25, color, 2)

    bar4Error = abs(truth - bar4Height)
    bar4ErrorText = "{:2.1f}%".format(bar4Error)
    if bar4Error > tolerance*100:
        color = (0, 254,254)
        cv2.circle(errorLayer, (value4BottomLeftX-10, (value4BottomLeftY-15) + 2*textOffset), 10, color, -1)
    else:
        color = (255, 255, 255)
    cv2.putText(errorLayer, "{:>4}".format(bar4ErrorText), (value4BottomLeftX, value4BottomLeftY + 2*textOffset),
            cv2.FONT_HERSHEY_SIMPLEX, 1.25, color, 2)

    bar5Error = abs(truth - bar5Height)
    bar5ErrorText = "{:2.1f}%".format(bar5Error)
    if bar5Error > tolerance*100:
        color = (0, 254,254)
        cv2.circle(errorLayer, (value5BottomLeftX-10, (value5BottomLeftY-15) + 2*textOffset), 10, color, -1)
    else:
        color = (255, 255, 255)
    cv2.putText(errorLayer, "{:>4}".format(bar5ErrorText), (value5BottomLeftX, value5BottomLeftY + 2*textOffset),
            cv2.FONT_HERSHEY_SIMPLEX, 1.25, color, 2)             

def drawBarValueText(id, height):

    heightText = "{:2.1f}%".format(height) 
    if (id == "1"):
        cv2.putText(bar1Layer, "{:>4}".format(heightText), (value1BottomLeftX-5, value1BottomLeftY + textOffset),
            cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2)
    elif (id == "2"):
        cv2.putText(bar2Layer, "{:>4}".format(heightText), (value2BottomLeftX-5, value2BottomLeftY + textOffset),
            cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2)
    elif (id == "3"):
        cv2.putText(bar3Layer, "{:>4}".format(heightText), (value3BottomLeftX-5, value3BottomLeftY + textOffset),
            cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2)
    elif (id == "4"):
        cv2.putText(bar4Layer, "{:>4}".format(heightText), (value4BottomLeftX-5, value4BottomLeftY + textOffset),
            cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2)
    elif (id == "5"):
        cv2.putText(bar5Layer, "{:>4}".format(heightText), (value5BottomLeftX-5, value5BottomLeftY + textOffset),
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
    cv2.putText(twoHzLayer, "{:>7}".format(bar1RateText), (bar1LabelX, bar1LabelY),
        cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2)
    bar2RateText = "{:2.1f} Hz".format(nativeRate/bar2Modulo)
    cv2.putText(twoHzLayer, "{:>7}".format(bar2RateText), (bar2LabelX, bar2LabelY),
        cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2)
    bar3RateText = "{:2.1f} Hz".format(nativeRate/bar3Modulo)
    cv2.putText(twoHzLayer, "{:>7}".format(bar3RateText), (bar3LabelX, bar3LabelY),
        cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2)
    bar4RateText = "{:2.1f} Hz".format(nativeRate/bar4Modulo)
    cv2.putText(twoHzLayer, "{:>7}".format(bar4RateText), (bar4LabelX, bar4LabelY),
        cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2)
    bar5RateText = "{:2.1f} Hz".format(nativeRate/bar5Modulo)
    cv2.putText(twoHzLayer, "{:>7}".format(bar5RateText), (bar5LabelX, bar5LabelY),
        cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2)

def runOneStep(frame):
    startTime = time.time()
    #print(startTime)
    global mode
    global speed
    global tolerance
    global height
    global sign
    global bar1Layer
    global bar2Layer
    global bar3Layer
    global bar4Layer
    global bar5Layer
    global twoHzLayer
    global errorLayer
    global outputImage

    frameInfo = ""

    if (frame % bar1Modulo) == 0: # load balance 20Hz to odd frames for 40Hz native rate
        frameInfo += " {:0.2f}Hz".format(nativeRate/bar1Modulo)
        #update data input
        (height, sign) = stepInput(mode, speed, height, sign)
        #clear bar# layer to zero and draw bar# layer elements
        bar1Layer = np.zeros(originalImage.shape, dtype=originalImage.dtype)
        drawBar("1", height)
    if (frame % bar2Modulo) == 0:
        frameInfo += " {:0.2f}Hz".format(nativeRate/bar2Modulo)
        bar2Layer = np.zeros(originalImage.shape, dtype=originalImage.dtype)
        drawBar("2", height)
    if (frame % bar3Modulo) == 0:
        frameInfo += " {:0.2f}Hz".format(nativeRate/bar3Modulo)
        bar3Layer = np.zeros(originalImage.shape, dtype=originalImage.dtype)
        drawBar("3", height)
    if (frame % bar4Modulo) == 0:
        frameInfo += " {:0.2f}Hz".format(nativeRate/bar4Modulo)
        bar4Layer = np.zeros(originalImage.shape, dtype=originalImage.dtype)
        drawBar("4", height)   
    if (frame % bar5Modulo) == 0:
        frameInfo += " {:0.2f}Hz".format(nativeRate/bar5Modulo)
        bar5Layer = np.zeros(originalImage.shape, dtype=originalImage.dtype)
        drawBar("5", height)
    if (frame % twoHzModulo) == 0: # clear 2 Hz layers and draw 2 Hz elements
        frameInfo += " {:0.2f}Hz".format(nativeRate/twoHzModulo)
        twoHzLayer = np.zeros(originalImage.shape, dtype=originalImage.dtype)
        drawDisplayText("0", height)
        drawLabelsSettings(speed)
    #if (frame % bar1Modulo) == 0:
        
    #compare displayed values to truth at the end of the frame where inputs where updated
    drawErrorText()

    #restore background
    outputImage = originalImage.copy()
    #outputImage[mask == 0] = originalImage[mask == 0] # restore only areas that arent in bar1 layer

    #get bar1 layer mask and overlay bar1 layer
    mask = bar1Layer.copy()
    outputImage[mask > 0] = bar1Layer[mask > 0]
    #get bar2 layer mask and overlay bar2 layer
    mask = bar2Layer.copy()
    outputImage[mask > 0] = bar2Layer[mask > 0]
    #get bar3 layer mask and overlay bar3 layer
    mask = bar3Layer.copy()
    outputImage[mask > 0] = bar3Layer[mask > 0]
    #get bar4 layer mask and overlay bar4 layer
    mask = bar4Layer.copy()
    outputImage[mask > 0] = bar4Layer[mask > 0]
    #get bar5 layer mask and overlay bar5 layer
    mask = bar5Layer.copy()
    outputImage[mask > 0] = bar5Layer[mask > 0]
    #get 2Hz layer mask and overlay 2Hz layer
    mask = twoHzLayer.copy()
    outputImage[mask > 0] = twoHzLayer[mask > 0]   
    #get error layer mask and overlay error layer
    mask = errorLayer.copy()
    outputImage[mask > 0] = errorLayer[mask > 0]

    # cv2.imshow("bar2Layer", bar2Layer)
    # cv2.waitKey(1)

    # cv2.imshow("bar3Layer", bar3Layer)
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
    elif key == ord('j') or key == 0:
        sign = 1 
    elif key == ord('k') or key == 1:
        sign = -1 
    elif key == ord('t'):
        mode = "target" 
    elif key == 27:
        exit()
    elif key != -1:
        print ("\n\n(", key, chr(key), ") function not found\n")
        print ("(spacebar) pause\n(s) smooth mode\n(r) random mode\n(t) target mode")
        print ("(-/+) data speed control\n([/]) tolerance control")
        print ("(j/up-arrow) up\n(k/down-arrow) down\n(n) step model rate")
        print ("(esc) quit\n\n")

    elapsed = time.time()-startTime
    if elapsed < (period):
        time.sleep(period-elapsed)
        elapsed = time.time()-startTime
        frameInfo = " {:>3} msec".format(math.floor(elapsed*1000)) + frameInfo
        frameInfo = "{:>3}:".format(frame) + frameInfo
    else:
        frameInfo = " {:>3} msec".format(math.floor(elapsed*1000)) + " *overrun* {:>3} msec".format(math.floor((elapsed-period)*1000)) + frameInfo 
        frameInfo = "{:>3}:".format(frame) + frameInfo

        print(frameInfo)

frame = 0
while 1:
    runOneStep(frame)
    frame+=1
    if frame >= loopMax:
        frame = 0




