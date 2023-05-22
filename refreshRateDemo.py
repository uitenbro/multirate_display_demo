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
import viz
import threading

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-m", "--mode", required=False, default = "smooth",
  help="mode - smooth or random")
ap.add_argument("-s", "--speed", required=False, default = 2,
  help="seconds - time to travers full range")

args = vars(ap.parse_args())

lineType = cv2.LINE_AA

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

ballYawBottomLeftX = 15 
ballYawBottomLeftY = 645

ballRollBottomLeftX = 15 
ballRollBottomLeftY = 730

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

pfdCenterPixelX = 325
pfdCenterPixelY = 225
pfdOffset = 200 #pixels
halfPfdWidth = int(pfdOffset/2)
roll = 60
pitch = 0
yaw = 0
signRoll = 1
signPitch = 1
signYaw = 1

maxRoll = 60 # degrees
minYaw  = 0 # degrees
maxYaw  = 360 # degrees

bar1Height = 0
bar2Height = 0
bar3Height = 0
bar4Height = 0
bar5Height = 0

# initialize static layer masks for reseting layers
originalImage = cv2.imread("tapes.png")
bar1Layer = np.zeros(originalImage.shape, dtype=originalImage.dtype)
bar1Layer[60:390, pfdCenterPixelX-halfPfdWidth:pfdCenterPixelX+halfPfdWidth] = (255,255,255) # top rectangle around bar and line
bar1Layer[535:originalImage.shape[0], pfdCenterPixelX-halfPfdWidth:pfdCenterPixelX+halfPfdWidth] = (255,255,255) # bottom rectangle around sphere
bar1Layer[445:490, pfdCenterPixelX-halfPfdWidth:pfdCenterPixelX+halfPfdWidth] = (255,255,255) #  rectangle around bar value % display line

bar2Layer = np.zeros(originalImage.shape, dtype=originalImage.dtype)
bar2Layer[60:390, pfdCenterPixelX+pfdOffset-halfPfdWidth:pfdCenterPixelX+pfdOffset+halfPfdWidth] = (255,255,255) # top rectangle around bar and line
bar2Layer[535:originalImage.shape[0], pfdCenterPixelX+pfdOffset-halfPfdWidth:pfdCenterPixelX+pfdOffset+halfPfdWidth] = (255,255,255) # bottom rectangle around sphere
bar2Layer[445:490, pfdCenterPixelX+pfdOffset-halfPfdWidth:pfdCenterPixelX+pfdOffset+halfPfdWidth] = (255,255,255) #  rectangle around bar value % display line

bar3Layer = np.zeros(originalImage.shape, dtype=originalImage.dtype)
bar3Layer[60:390, pfdCenterPixelX+2*pfdOffset-halfPfdWidth:pfdCenterPixelX+2*pfdOffset+halfPfdWidth] = (255,255,255) # top rectangle around bar and line
bar3Layer[535:originalImage.shape[0], pfdCenterPixelX+2*pfdOffset-halfPfdWidth:pfdCenterPixelX+2*pfdOffset+halfPfdWidth] = (255,255,255) # bottom rectangle around sphere
bar3Layer[445:490, pfdCenterPixelX+2*pfdOffset-halfPfdWidth:pfdCenterPixelX+2*pfdOffset+halfPfdWidth] = (255,255,255) #  rectangle around bar value % display line

bar4Layer = np.zeros(originalImage.shape, dtype=originalImage.dtype)
bar4Layer[60:390, pfdCenterPixelX+3*pfdOffset-halfPfdWidth:pfdCenterPixelX+3*pfdOffset+halfPfdWidth] = (255,255,255) # top rectangle around bar and line
bar4Layer[535:originalImage.shape[0], pfdCenterPixelX+3*pfdOffset-halfPfdWidth:pfdCenterPixelX+3*pfdOffset+halfPfdWidth] = (255,255,255) # bottom rectangle around sphere
bar4Layer[445:490, pfdCenterPixelX+3*pfdOffset-halfPfdWidth:pfdCenterPixelX+3*pfdOffset+halfPfdWidth] = (255,255,255) #  rectangle around bar value % display line

bar5Layer = np.zeros(originalImage.shape, dtype=originalImage.dtype)
bar5Layer[60:390, pfdCenterPixelX+4*pfdOffset-halfPfdWidth:pfdCenterPixelX+4*pfdOffset+halfPfdWidth] = (255,255,255) # top rectangle around bar and line
bar5Layer[535:originalImage.shape[0], pfdCenterPixelX+4*pfdOffset-halfPfdWidth:pfdCenterPixelX+4*pfdOffset+halfPfdWidth] = (255,255,255) # bottom rectangle around sphere
bar5Layer[445:490, pfdCenterPixelX+4*pfdOffset-halfPfdWidth:pfdCenterPixelX+4*pfdOffset+halfPfdWidth] = (255,255,255) #  rectangle around bar value % display line

oneHzLayer = np.zeros(originalImage.shape, dtype=originalImage.dtype)
oneHzLayer[390:450, pfdCenterPixelX-halfPfdWidth:originalImage.shape[1]] = (255,255,255) # rectangle around 2hz display line
oneHzLayer[0:60, pfdCenterPixelX-halfPfdWidth:originalImage.shape[1]] = (255,255,255) # rectangle around top labels
oneHzLayer[0:originalImage.shape[0], 0:240] = (255,255,255) # rectangle around side labels

errorLayer = np.zeros(originalImage.shape, dtype=originalImage.dtype)
errorLayer[495:530, pfdCenterPixelX-halfPfdWidth:originalImage.shape[1]] = (255,255,255) #  rectangle around error display line

outputImage = originalImage.copy();

def initRates(nativeRate):
    # (bar1Modulo, bar2Modulo, bar3Modulo, bar4Modulo, bar5Modulo, oneHzModulo, loopMax)

    if nativeRate >= 40:
        return (2, 3, 4, 8, 40, 40, 120) # 20.0,   13.0,   10.0,    5.0,   1.0
    elif nativeRate >= 30:
        return (1, 2, 3, 6, 30, 30, 300) # 30.0,   15.0,   10.0,    5.0,   1.0  
        #return (1, 2, 3, 4, 6, 15, 300) # 30.0,   15.0,   10.0,    7.5,   5.0
    elif nativeRate >= 25:
        return (1, 2, 3, 4, 5, 25, 600)  # 25.0,   12.5,    8.3,    6.2,   5.0
    elif nativeRate >= 20:
        return (1, 2, 3, 4, 5, 20, 60)   # 20.0,   10.0,    6.7,    5.0,   4.0    
    elif nativeRate >= 10:
        return (1, 2, 3, 5, 10, 10, 1000)# 10.0,    5.0,    3.3,    2.0,   1.0

tolerance = 0.05  # 5%
nativeRate = 10.0 # 30Hz
period = 1/nativeRate
(bar1Modulo, bar2Modulo, bar3Modulo, bar4Modulo, bar5Modulo, oneHzModulo, loopMax) = initRates(nativeRate)
jitter = 0.025 # 1%

def stepRate():
    global nativeRate
    global period
    global bar1Modulo, bar2Modulo, bar3Modulo, bar4Modulo, bar5Modulo, oneHzModulo, loopMax

    if nativeRate == 40:
        nativeRate = 30
    elif nativeRate == 30:
        nativeRate = 25
    elif nativeRate == 25:
        nativeRate = 20    
    elif nativeRate == 20:
        nativeRate = 10
    elif nativeRate == 10:
        nativeRate = 40

    period = 1/nativeRate
    (bar1Modulo, bar2Modulo, bar3Modulo, bar4Modulo, bar5Modulo, oneHzModulo, loopMax) = initRates(nativeRate)


speed = args["speed"] 
mode = args["mode"] #smooth or random

if mode == "smooth":
    height = 0
    sign = 1 #1 is up -1 is down)
else:
    height = 50
    sign = 0



def stepBarInput(mode, speed, prevHeight, sign):
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
        if (randomSign > 0): #up====
            nextHeight = maxHeight/2 + random.randrange(0, int(speedMultiplier*maxHeight))
        else: # down 
            nextHeight = maxHeight/2 - random.randrange(0, int(speedMultiplier*maxHeight))
        #print(randomSign, nextHeight)

    if (nextHeight > maxHeight):
        nextHeight = maxHeight
        sign = -1 #change direction for smooth mode
    if (nextHeight < 0):
        nextHeight = 0
        sign = 1 #change direction smooth mode

    return (nextHeight, sign)    

def stepPfdInput(mode, speed, prevYaw, prevPitch, prevRoll, signYaw, signPitch, signRoll):

    if speed == 0:
        speedMultiplier = 1 # full scale (flashing)
    else:
        speedMultiplier = (bar1Modulo/nativeRate)/speed

    if (mode == "smooth") or (mode == "target"):
        nextRoll = prevRoll + signRoll*speedMultiplier*maxRoll*2
        nextYaw = prevYaw + signYaw*speedMultiplier*maxYaw
    else: # mode = random
        randomSign = random.randrange(-1, 2) # set random up or down
        if (randomSign > 0): #up
            nextRoll = prevRoll + speedMultiplier*maxRoll*2
            nextYaw = prevYaw + speedMultiplier*maxYaw
        else: # down 
            nextRoll = prevRoll - speedMultiplier*maxRoll*2
            nextYaw = prevYaw - speedMultiplier*maxYaw
        #print(randomSign, nextRoll)

    if (nextRoll >= maxRoll):
        nextRoll = maxRoll
        signRoll = -1 #change direction for smooth mode
    if (nextRoll <= -maxRoll):
        nextRoll = -maxRoll
        signRoll = 1 #change direction smooth mode

    if (nextYaw >= maxYaw):
        nextYaw = maxYaw
        signYaw = -1 #change direction for smooth mode
    if (nextYaw <= minYaw):
        nextYaw = minYaw
        signYaw = 1 #change direction smooth mode
       
    #print(nextRoll)

    return (nextYaw,0, nextRoll, signYaw, signPitch, signRoll)    

def drawSphere(barLayer, pfdCenterPixelX,pfdCenterPixelY,pfdTotalWidth,yaw, roll):   
    global lineType

    pfdCenterPixelY=pfdCenterPixelY+425
    # draw outside circle boundary
    cv2.ellipse(barLayer, (pfdCenterPixelX,pfdCenterPixelY), (int(pfdTotalWidth/2), int(pfdTotalWidth/2)), 0, 0, 360, (255,255,255), 2, lineType=lineType) 

    yaw = yaw%180
    #print (yaw)

    # draw meridians
    if (yaw <= 90):
        cv2.ellipse(barLayer, (pfdCenterPixelX,pfdCenterPixelY), (int(pfdTotalWidth/2*math.sin(math.radians(yaw))), int(pfdTotalWidth/2)), roll, -90, 90, (0,255,255), 2, lineType=lineType) 
    else:
        cv2.ellipse(barLayer, (pfdCenterPixelX,pfdCenterPixelY), (int(pfdTotalWidth/2*math.sin(math.radians(yaw))), int(pfdTotalWidth/2)), roll, 90, 270, (0,255,255), 2, lineType=lineType) 
    if (yaw+45 <= 90) or (yaw+45>=180):
       if yaw+45>180: yaw = yaw-180
       cv2.ellipse(barLayer, (pfdCenterPixelX,pfdCenterPixelY), (int(pfdTotalWidth/2*math.sin(math.radians(yaw+45))), int(pfdTotalWidth/2)), roll, -90, 90, (255,0,255), 2, lineType=lineType) 
    elif(yaw+45<180):
       cv2.ellipse(barLayer, (pfdCenterPixelX,pfdCenterPixelY), (int(pfdTotalWidth/2*math.sin(math.radians(yaw+45))), int(pfdTotalWidth/2)), roll, 90, 270, (255,0,255), 2, lineType=lineType) 
    # if (yaw+60 <= 90) or (yaw+60>1=80):
    #     if yaw+60>180: yaw = yaw-180
    #     cv2.ellipse(barLayer, (pfdCenterPixelX,pfdCenterPixelY), (int(pfdTotalWidth/2*math.sin(math.radians(yaw+60))), int(pfdTotalWidth/2)), roll, -90, 90, (255,255,255), 2, lineType=lineType) 
    # elif(yaw+60<180):
    #     cv2.ellipse(barLayer, (pfdCenterPixelX,pfdCenterPixelY), (int(pfdTotalWidth/2*math.sin(math.radians(yaw+60))), int(pfdTotalWidth/2)), roll, 90, 270, (255,255,255), 2, lineType=lineType) 
    if (yaw+90 <= 90) or (yaw+90>=180):
       if yaw+90>180: yaw = yaw-180
       cv2.ellipse(barLayer, (pfdCenterPixelX,pfdCenterPixelY), (int(pfdTotalWidth/2*math.sin(math.radians(yaw+90))), int(pfdTotalWidth/2)), roll, -90, 90, (255,255,0), 2, lineType=lineType) 
    elif(yaw+90<180):
       cv2.ellipse(barLayer, (pfdCenterPixelX,pfdCenterPixelY), (int(pfdTotalWidth/2*math.sin(math.radians(yaw+90))), int(pfdTotalWidth/2)), roll, 90, 270, (255,255,0), 2, lineType=lineType) 
    # if (yaw+120 <= 90) or (yaw+120>=180):
    #     if yaw+120>180: yaw = yaw-180
    #     cv2.ellipse(barLayer, (pfdCenterPixelX,pfdCenterPixelY), (int(pfdTotalWidth/2*math.sin(math.radians(yaw+120))), int(pfdTotalWidth/2)), roll, -90, 90, (255,255,255), 2, lineType=lineType) 
    # elif(yaw+120<180):
    #    cv2.ellipse(barLayer, (pfdCenterPixelX,pfdCenterPixelY), (int(pfdTotalWidth/2*math.sin(math.radians(yaw+120))), int(pfdTotalWidth/2)), roll, 90, 270, (255,255,255), 2, lineType=lineType) 
    if (yaw+135 <= 90) or (yaw+135>=180):
       if yaw+150>180: yaw = yaw-180
       cv2.ellipse(barLayer, (pfdCenterPixelX,pfdCenterPixelY), (int(pfdTotalWidth/2*math.sin(math.radians(yaw+135))), int(pfdTotalWidth/2)), roll, -90, 90, (0,255,0), 2, lineType=lineType) 
    elif(yaw+135<180):
       cv2.ellipse(barLayer, (pfdCenterPixelX,pfdCenterPixelY), (int(pfdTotalWidth/2*math.sin(math.radians(yaw+135))), int(pfdTotalWidth/2)), roll, 90, 270, (0,255,0), 2, lineType=lineType) 

def drawBar(id, height):
    heightPixels = int(barTotalHeight*height/100)
    #print(heightPixels)
    global bar1Height, bar2Height, bar3Height, bar4Height, bar5Height
    global lineType
    targetHeight = int(11/15*barTotalHeight)

    if (id == "1"):
        cv2.rectangle(outputImage, (bar1BottomRightX-barWidth, bar1BottomRightY-heightPixels), (bar1BottomRightX, bar1BottomRightY), (0, 255, 0), -1)
        bar1Height = height
        if mode == "target":
            cnt = np.array([(bar1BottomRightX, bar1BottomRightY-targetHeight),
                (bar1BottomRightX+15, bar1BottomRightY-targetHeight-8),(bar1BottomRightX+15, bar1BottomRightY-targetHeight+8)])
            cv2.drawContours(outputImage, [cnt], 0, (147, 20, 255), -1)
    elif (id == "2"):
        cv2.rectangle(outputImage, (bar2BottomRightX-barWidth, bar2BottomRightY-heightPixels), (bar2BottomRightX, bar2BottomRightY), (0, 255, 0), -1)
        bar2Height = height
        if mode == "target":
            cnt = np.array([(bar2BottomRightX, bar2BottomRightY-targetHeight),
                (bar2BottomRightX+15, bar2BottomRightY-targetHeight-8),(bar2BottomRightX+15, bar2BottomRightY-targetHeight+8)])
            cv2.drawContours(outputImage, [cnt], 0, (147, 20, 255), -1)
    elif (id == "3"):
        cv2.rectangle(outputImage, (bar3BottomRightX-barWidth, bar3BottomRightY-heightPixels), (bar3BottomRightX, bar3BottomRightY), (0, 255, 0), -1)
        bar3Height = height
        if mode == "target":
            cnt = np.array([(bar3BottomRightX, bar3BottomRightY-targetHeight),
                (bar3BottomRightX+15, bar3BottomRightY-targetHeight-8),(bar3BottomRightX+15, bar3BottomRightY-targetHeight+8)])
            cv2.drawContours(outputImage, [cnt], 0, (147, 20, 255), -1)        
    elif (id == "4"):
        cv2.rectangle(outputImage, (bar4BottomRightX-barWidth, bar4BottomRightY-heightPixels), (bar4BottomRightX, bar4BottomRightY), (0, 255, 0), -1)
        bar4Height = height
        if mode == "target":
            cnt = np.array([(bar4BottomRightX, bar4BottomRightY-targetHeight),
                (bar4BottomRightX+15, bar4BottomRightY-targetHeight-8),(bar4BottomRightX+15, bar4BottomRightY-targetHeight+8)])
            cv2.drawContours(outputImage, [cnt], 0, (147, 20, 255), -1)        
    elif (id == "5"):
        cv2.rectangle(outputImage, (bar5BottomRightX-barWidth, bar5BottomRightY-heightPixels), (bar5BottomRightX, bar5BottomRightY), (0, 255, 0), -1)
        bar5Height = height
        if mode == "target":
            cnt = np.array([(bar5BottomRightX, bar5BottomRightY-targetHeight),
                (bar5BottomRightX+15, bar5BottomRightY-targetHeight-8),(bar5BottomRightX+15, bar5BottomRightY-targetHeight+8)])
            cv2.drawContours(outputImage, [cnt], 0, (147, 20, 255), -1)

    drawBarValueText(id, height)
    #print("u: ", bar1Height, bar2Height, bar3Height, bar4Height, bar5Height)

def drawDisplayText(id, height):
    global lineType

    height = "{: 2.1f}".format((maxDisplayValue*height/100))
    if (id == "1") or (id == "0"):
        cv2.putText(outputImage, "{:>4.1f}".format(height), (value1BottomLeftX, value1BottomLeftY),
            cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2, lineType=lineType)
    if (id == "2") or (id == "0"):
        cv2.putText(outputImage, "{:>4.1f}".format(height), (value2BottomLeftX, value2BottomLeftY),
            cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2, lineType=lineType)
    if (id == "3") or (id == "0"):
        cv2.putText(outputImage, "{:>4.1f}".format(height), (value3BottomLeftX, value3BottomLeftY),
            cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2, lineType=lineType)
    if (id == "4") or (id == "0"):
        cv2.putText(outputImage, "{:>4.1f}".format(height), (value4BottomLeftX, value4BottomLeftY),
            cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2, lineType=lineType)
    if (id == "5") or (id == "0"):
        cv2.putText(outputImage, "{:>4.1f}".format(height), (value5BottomLeftX, value5BottomLeftY),
            cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2, lineType=lineType)             

def drawErrorText():
    global lineType
    #print(bar1Height, bar2Height, bar3Height, bar4Height, bar5Height)

    if mode == "target":
        truth = 11/15*100
    else:
        truth = bar1Height
    #print(truth-bar1Height, truth-bar2Height, truth-bar3Height, truth-bar4Height, truth-bar5Height)
    
    #clear error layer
    #errorLayer = np.zeros(originalImage.shape, dtype=originalImage.dtype)

    bar1Error = abs(truth - bar1Height)
    bar1ErrorText = "{: 2.1f}%".format(bar1Error)
    if bar1Error > tolerance*100:
        color = (0, 254,254)
        cv2.circle(outputImage, (value1BottomLeftX-10, (value1BottomLeftY-15) + 2*textOffset), 10, color, -1)
    else:
        color = (255, 255, 255)
    cv2.putText(outputImage, "{:>4}".format(bar1ErrorText), (value1BottomLeftX, value1BottomLeftY + 2*textOffset),
            cv2.FONT_HERSHEY_SIMPLEX, 1.25, color, 2, lineType=lineType)

    bar2Error = abs(truth - bar2Height)
    bar2ErrorText = "{:2.1f}%".format(bar2Error)
    if bar2Error > tolerance*100:
        color = (0, 254,254)
        cv2.circle(outputImage, (value2BottomLeftX-10, (value2BottomLeftY-15) + 2*textOffset), 10, color, -1)
    else:
        color = (255, 255, 255)
    cv2.putText(outputImage, "{:>4}".format(bar2ErrorText), (value2BottomLeftX, value2BottomLeftY + 2*textOffset),
            cv2.FONT_HERSHEY_SIMPLEX, 1.25, color, 2, lineType=lineType)

    bar3Error = abs(truth - bar3Height)
    bar3ErrorText = "{:2.1f}%".format(bar3Error)
    if bar3Error > tolerance*100:
        color = (0, 254,254)
        cv2.circle(outputImage, (value3BottomLeftX-10, (value3BottomLeftY-15) + 2*textOffset), 10, color, -1)
    else:
        color = (255, 255, 255)        
    cv2.putText(outputImage, "{:>4}".format(bar3ErrorText), (value3BottomLeftX, value3BottomLeftY + 2*textOffset),
            cv2.FONT_HERSHEY_SIMPLEX, 1.25, color, 2, lineType=lineType)

    bar4Error = abs(truth - bar4Height)
    bar4ErrorText = "{:2.1f}%".format(bar4Error)
    if bar4Error > tolerance*100:
        color = (0, 254,254)
        cv2.circle(outputImage, (value4BottomLeftX-10, (value4BottomLeftY-15) + 2*textOffset), 10, color, -1)
    else:
        color = (255, 255, 255)
    cv2.putText(outputImage, "{:>4}".format(bar4ErrorText), (value4BottomLeftX, value4BottomLeftY + 2*textOffset),
            cv2.FONT_HERSHEY_SIMPLEX, 1.25, color, 2, lineType=lineType)

    bar5Error = abs(truth - bar5Height)
    bar5ErrorText = "{:2.1f}%".format(bar5Error)
    if bar5Error > tolerance*100:
        color = (0, 254,254)
        cv2.circle(outputImage, (value5BottomLeftX-10, (value5BottomLeftY-15) + 2*textOffset), 10, color, -1)
    else:
        color = (255, 255, 255)
    cv2.putText(outputImage, "{:>4}".format(bar5ErrorText), (value5BottomLeftX, value5BottomLeftY + 2*textOffset),
            cv2.FONT_HERSHEY_SIMPLEX, 1.25, color, 2, lineType=lineType)             

def drawBarValueText(id, height):
    global lineType

    heightText = "{:0>5.1f}".format(height/100*maxDisplayValue) 
    if (id == "1"):
        cv2.putText(outputImage, heightText, (value1BottomLeftX-10, value1BottomLeftY + textOffset),
            cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2, lineType=lineType)
    elif (id == "2"):
        cv2.putText(outputImage, heightText, (value2BottomLeftX-10, value2BottomLeftY + textOffset),
            cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2, lineType=lineType)
    elif (id == "3"):
        cv2.putText(outputImage, heightText, (value3BottomLeftX-10, value3BottomLeftY + textOffset),
            cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2, lineType=lineType)
    elif (id == "4"):
        cv2.putText(outputImage, heightText, (value4BottomLeftX-10, value4BottomLeftY + textOffset),
            cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2, lineType=lineType)
    elif (id == "5"):
        cv2.putText(outputImage, heightText, (value5BottomLeftX-10, value5BottomLeftY + textOffset),
            cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2, lineType=lineType)             

def drawLabelsSettings(speed):
    global lineType

    modelRateText = "{:2.1f} Hz".format(nativeRate)
    cv2.putText(outputImage, "{:>5}".format(modelRateText), (modelRateBottomLeftX, modelRateBottomLeftY),
        cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2, lineType=lineType)

    speedText = "{:1.2f} sec".format(speed)
    cv2.putText(outputImage, "{: >8}".format(speedText), (speedBottomLeftX, speedBottomLeftY),
        cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2, lineType=lineType)
    toleranceText = "{:.0f}%".format(tolerance*100)
    cv2.putText(outputImage, "{: >5}".format(toleranceText), (toleranceBottomLeftX, toleranceBottomLeftY),
        cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2, lineType=lineType)

    ballYawText = "{:0.0f}/sec".format((maxYaw-minYaw)/speed)
    cv2.putText(outputImage, "{:>7}".format(ballYawText), (ballYawBottomLeftX, ballYawBottomLeftY),
        cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2, lineType=lineType)    

    ballRollText = "{:0.0f}/sec".format((2*maxRoll)/speed)
    cv2.putText(outputImage, "{:>7}".format(ballRollText), (ballRollBottomLeftX, ballRollBottomLeftY),
        cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2, lineType=lineType)

    bar1RateText = "{:2.1f} Hz".format(nativeRate/bar1Modulo)
    cv2.putText(outputImage, "{:>7}".format(bar1RateText), (bar1LabelX, bar1LabelY),
        cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2, lineType=lineType)
    bar2RateText = "{:2.1f} Hz".format(nativeRate/bar2Modulo)
    cv2.putText(outputImage, "{:>7}".format(bar2RateText), (bar2LabelX, bar2LabelY),
        cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2)
    bar3RateText = "{:2.1f} Hz".format(nativeRate/bar3Modulo)
    cv2.putText(outputImage, "{:>7}".format(bar3RateText), (bar3LabelX, bar3LabelY),
        cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2, lineType=lineType)
    bar4RateText = "{:2.1f} Hz".format(nativeRate/bar4Modulo)
    cv2.putText(outputImage, "{:>7}".format(bar4RateText), (bar4LabelX, bar4LabelY),
        cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2)
    bar5RateText = "{:2.1f} Hz".format(nativeRate/bar5Modulo)
    cv2.putText(outputImage, "{:>7}".format(bar5RateText), (bar5LabelX, bar5LabelY),
        cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 255, 255), 2, lineType=lineType)

def drawPFD(id, yaw, pitch, roll):
    global pfd1Layer
    global bar1Layer
    global bar2Layer
    global bar3Layer
    global bar4Layer
    global bar5Layer
    global pfdOffset
    global lineType

    #yawRange = 180 # +/- degrees
    pitchRange = 90 # +/- degrees
    rollRange = 90 # +/- degress
    pfdTotalHeight = 300 # pixels
    pfdTotalWidth = 180 # pixels

    pixelsPerDegree = 1

    pitchInPixels = pitch*pixelsPerDegree

    # draw horizon line
    centerHorizon = pfdTotalHeight/2 + pitchInPixels
    if centerHorizon > pfdTotalHeight:
        centerHorizon = pfdTotalHeight

    horizonLeftX = int(pfdCenterPixelX - pfdTotalWidth/2)
    horizonLeftY = int(pfdCenterPixelY - pfdTotalWidth/2*math.atan(math.radians(roll)))
    horizonRightX = int(pfdCenterPixelX + pfdTotalWidth/2)
    horizonRightY = int(pfdCenterPixelY + pfdTotalWidth/2*math.atan(math.radians(roll)))
    #print (roll)

    if (id == "1"):
        cv2.line(outputImage, (horizonLeftX, horizonLeftY), (horizonRightX, horizonRightY), (255,255,255), 2, lineType=lineType)
        drawSphere(outputImage, pfdCenterPixelX,pfdCenterPixelY,pfdTotalWidth,yaw, roll)
    elif (id == "2"):
        cv2.line(outputImage, (horizonLeftX+pfdOffset, horizonLeftY), (horizonRightX+pfdOffset, horizonRightY), (255,255,255), 2, lineType=lineType)
        drawSphere(outputImage, pfdCenterPixelX+pfdOffset,pfdCenterPixelY,pfdTotalWidth,yaw, roll)
    elif (id == "3"):
        cv2.line(outputImage, (horizonLeftX+pfdOffset*2, horizonLeftY), (horizonRightX+pfdOffset*2, horizonRightY), (255,255,255), 2, lineType=lineType)
        drawSphere(outputImage, pfdCenterPixelX+pfdOffset*2,pfdCenterPixelY,pfdTotalWidth,yaw, roll)
    elif (id == "4"):
        cv2.line(outputImage, (horizonLeftX+pfdOffset*3, horizonLeftY), (horizonRightX+pfdOffset*3, horizonRightY), (255,255,255), 2, lineType=lineType)
        drawSphere(outputImage, pfdCenterPixelX+pfdOffset*3,pfdCenterPixelY,pfdTotalWidth,yaw, roll)
    elif (id == "5"):
        cv2.line(outputImage, (horizonLeftX+pfdOffset*4, horizonLeftY), (horizonRightX+pfdOffset*4, horizonRightY), (255,255,255), 2, lineType=lineType)
        drawSphere(outputImage, pfdCenterPixelX+pfdOffset*4,pfdCenterPixelY,pfdTotalWidth,yaw, roll)

def runRateOneThread():
    global nativeRate
    global jitter
    global keepRunning

    startTime = 0

    while keepRunning:
        threadOneLock.acquire()
        deadlineDuration =1/(nativeRate/bar1Modulo)
        now = time.time()
        totalTime = now - startTime
        startTime = now

        outputImage[bar1Layer > 0] = originalImage[bar1Layer > 0]
        drawBar("1", height)
        #drawPFD("1", yaw, pitch, roll)
        
        elapsed = time.time()-startTime
        
        if (totalTime < deadlineDuration*(1-jitter) or totalTime > deadlineDuration*(1+jitter)):
            frameInfo = "{:>3}:".format(frame)
            frameInfo += " {: >5.2f}Hz".format(nativeRate/bar1Modulo)
            frameInfo += " {: >5.2f} msec".format(math.floor(elapsed*1000))
            frameInfo += " {: >7.2f} msec".format(totalTime*1000)
            frameInfo += " ** violation ** {: >7.2f} msec".format((totalTime-deadlineDuration)*1000)
            frameInfo += " > {: >7.2f}%".format(jitter*100)
            print(frameInfo)

    print("Finish One")

def runRateTwoThread():
    global nativeRate
    global jitter
    global keepRunning

    startTime = 0

    while keepRunning:
        threadTwoLock.acquire()
        deadlineDuration =1/(nativeRate/bar2Modulo)
        now = time.time()
        totalTime = now - startTime
        startTime = now

        outputImage[bar2Layer > 0] = originalImage[bar2Layer > 0]
        drawBar("2", height)
        #drawPFD("2", yaw, pitch, roll)
        
        elapsed = time.time()-startTime
        
        if (totalTime < deadlineDuration*(1-jitter) or totalTime > deadlineDuration*(1+jitter)):
            frameInfo = "{:>3}:".format(frame)
            frameInfo += " {: >5.2f}Hz".format(nativeRate/bar2Modulo)
            frameInfo += " {: >5.2f} msec".format(math.floor(elapsed*1000))
            frameInfo += " {: >7.2f} msec".format(totalTime*1000)
            frameInfo += " ** violation ** {: >7.2f} msec".format((totalTime-deadlineDuration)*1000)
            frameInfo += " > {: >7.2f}%".format(jitter*100)
            print(frameInfo)

    print("Finish Two")


def runRateThreeThread():
    global nativeRate
    global jitter
    global keepRunning

    startTime = 0

    while keepRunning:
        threadThreeLock.acquire()
        deadlineDuration =1/(nativeRate/bar3Modulo)
        now = time.time()
        totalTime = now - startTime
        startTime = now

        outputImage[bar3Layer > 0] = originalImage[bar3Layer > 0]
        drawBar("3", height)
        #drawPFD("3", yaw, pitch, roll)
        
        elapsed = time.time()-startTime
        
        if (totalTime < deadlineDuration*(1-jitter) or totalTime > deadlineDuration*(1+jitter)):
            frameInfo = "{:>3}:".format(frame)
            frameInfo += " {: >5.2f}Hz".format(nativeRate/bar3Modulo)
            frameInfo += " {: >5.2f} msec".format(math.floor(elapsed*1000))
            frameInfo += " {: >7.2f} msec".format(totalTime*1000)            
            frameInfo += " ** violation ** {: >7.2f} msec".format((totalTime-deadlineDuration)*1000)
            frameInfo += " > {: >7.2f}%".format(jitter*100)
            print(frameInfo)

    print("Finish Three")

def runRateFourThread():
    global nativeRate
    global jitter
    global keepRunning

    startTime = 0

    while keepRunning:
        threadFourLock.acquire()
        deadlineDuration =1/(nativeRate/bar4Modulo)
        now = time.time()
        totalTime = now - startTime
        startTime = now

        outputImage[bar4Layer > 0] = originalImage[bar4Layer > 0]
        drawBar("4", height)
        #drawPFD("4", yaw, pitch, roll)
        
        elapsed = time.time()-startTime
        
        if (totalTime < deadlineDuration*(1-jitter) or totalTime > deadlineDuration*(1+jitter)):
            frameInfo = "{:>3}:".format(frame)
            frameInfo += " {: >5.2f}Hz".format(nativeRate/bar4Modulo)
            frameInfo += " {: >5.2f} msec".format(math.floor(elapsed*1000))
            frameInfo += " {: >7.2f} msec".format(totalTime*1000)
            frameInfo += " ** violation ** {: >7.2f} msec".format((totalTime-deadlineDuration)*1000)
            frameInfo += " > {: >7.2f}%".format(jitter*100)
            print(frameInfo)

    print("Finish Four")

def runRateFiveThread():
    global nativeRate
    global jitter
    global keepRunning

    startTime = 0

    while keepRunning:
        threadFiveLock.acquire()
        deadlineDuration =1/(nativeRate/bar5Modulo)
        now = time.time()
        totalTime = now - startTime
        startTime = now

        outputImage[bar5Layer > 0] = originalImage[bar5Layer > 0]
        drawBar("5", height)
        #drawPFD("5", yaw, pitch, roll)
        
        elapsed = time.time()-startTime
        
        if (totalTime < deadlineDuration*(1-jitter) or totalTime > deadlineDuration*(1+jitter)):
            frameInfo = "{:>3}:".format(frame)
            frameInfo += " {: >5.2f}Hz".format(nativeRate/bar5Modulo)
            frameInfo += " {: >5.2f} msec".format(math.floor(elapsed*1000))
            frameInfo += " {: >7.2f} msec".format(totalTime*1000)
            frameInfo += " ** violation ** {: >7.2f} msec".format((totalTime-deadlineDuration)*1000)
            frameInfo += " > {: >7.2f}%".format(jitter*100)
            print(frameInfo)

    print("Finish Five")

def runLowThread():
    global nativeRate
    global jitter
    global keepRunning

    startTime = 0

    while keepRunning:
        threadLowLock.acquire()
        deadlineDuration =1/(nativeRate/oneHzModulo)
        now = time.time()
        totalTime = now - startTime
        startTime = now

        outputImage[oneHzLayer > 0] = originalImage[oneHzLayer > 0]
        #drawDisplayText("0", height)
        drawLabelsSettings(speed)
        
        elapsed = time.time()-startTime
        
        if (totalTime < deadlineDuration*(1-jitter) or totalTime > deadlineDuration*(1+jitter)):
            frameInfo = "{:>3}:".format(frame)
            frameInfo += " {: >5.2f}Hz".format(nativeRate/bar5Modulo)
            frameInfo += " {: >5.2f} msec".format(math.floor(elapsed*1000))
            frameInfo += " {: >7.2f} msec".format(totalTime*1000)
            frameInfo += " ** violation ** {: >7.2f} msec".format((totalTime-deadlineDuration)*1000)
            frameInfo += " > {: >7.2f}%".format(jitter*100)
            print(frameInfo)

    print("Finish Low")

threadOne = threading.Thread(target=runRateOneThread)
threadOneStarted = False
threadOneLock = threading.Lock()

threadTwo = threading.Thread(target=runRateTwoThread)
threadTwoStarted = False
threadTwoLock = threading.Lock()

threadThree = threading.Thread(target=runRateThreeThread)
threadThreeStarted = False
threadThreeLock = threading.Lock()

threadFour = threading.Thread(target=runRateFourThread)
threadFourStarted = False
threadFourLock = threading.Lock()

threadFive = threading.Thread(target=runRateFiveThread)
threadFiveStarted = False
threadFiveLock = threading.Lock()

threadLow = threading.Thread(target=runLowThread)
threadLowStarted = False
threadLowLock = threading.Lock()


def runOneStep(frame):
    startTime = time.time()
    #print(startTime)
    global mode
    global speed
    global tolerance
    global height
    global sign
    global yaw, pitch, roll
    global signYaw, signPitch, signRoll
    global bar1Layer
    global bar2Layer
    global bar3Layer
    global bar4Layer
    global bar5Layer
    global oneHzLayer
    global errorLayer
    global pfd1Layer
    global sphereLayer
    global outputImage
    global lineType
    global threadOneStarted
    global threadTwoStarted
    global threadThreeStarted
    global threadFourStarted
    global threadFiveStarted
    global threadLowStarted
    global keepRunning
    
    frameInfo = ""

    if ((frame-1) % bar1Modulo) == 0: # load balance highest rate to odd frames
        #update data input
        (height, sign) = stepBarInput(mode, speed, height, sign)
        (yaw, pitch, roll, signYaw, signPitch, signRoll) = stepPfdInput(mode, speed, yaw, pitch, roll, signYaw, signPitch, signRoll)
        
        frameInfo += " {:0.2f}Hz".format(nativeRate/bar1Modulo)
        if (threadOneStarted == False):
            threadOne.start()
            threadOneStarted = True
        threadOneLock.release()
    if (frame % bar2Modulo) == 0:
        frameInfo += " {:0.2f}Hz".format(nativeRate/bar2Modulo)
        if (threadTwoStarted == False):
            threadTwo.start()
            threadTwoStarted = True
        threadTwoLock.release()
    if (frame % bar3Modulo) == 0:
        frameInfo += " {:0.2f}Hz".format(nativeRate/bar3Modulo)
        if (threadThreeStarted == False):
            threadThree.start()
            threadThreeStarted = True
        threadThreeLock.release()
    if (frame % bar4Modulo) == 0:
        frameInfo += " {:0.2f}Hz".format(nativeRate/bar4Modulo)
        if (threadFourStarted == False):
            threadFour.start()
            threadFourStarted = True
        threadFourLock.release()
    if (frame % bar5Modulo) == 0:
        frameInfo += " {:0.2f}Hz".format(nativeRate/bar5Modulo)
        if (threadFiveStarted == False):
            threadFive.start()
            threadFiveStarted = True
        threadFiveLock.release()
    if (frame % oneHzModulo) == 0: # clear 1 Hz layers and draw 1 Hz elements
        frameInfo += " {:0.2f}Hz".format(nativeRate/oneHzModulo)
        if (threadLowStarted == False):
            threadLow.start()
            threadLowStarted = True
        threadLowLock.release()

    # compare displayed values to truth at the end of the frame where inputs where updated
    #outputImage[errorLayer > 0] = originalImage[errorLayer > 0]
    #drawErrorText()
    #outputImage[errorLayer > 0] = errorLayer[errorLayer > 0]

    # cv2.imshow("errorLayer", errorLayer)
    # cv2.waitKey(1)
    # cv2.imshow("oneHzLayer", oneHzLayer)
    # cv2.waitKey(1)
    # cv2.imshow("bar3Layer", bar3Layer)
    # cv2.waitKey(1)
    # cv2.imshow("bar4Layer", bar4Layer)
    # cv2.waitKey(1)
    # cv2.imshow("bar5Layer", bar5Layer)
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
        roll = 0
    elif key == ord('-'):
        speed += 0.25
        if speed >= 10:
            speed = 10 
            print(speed)
    elif key == ord('+') or key == ord('='):
        speed -= 0.25
        if speed <= 0: 
            speed = 0.25
            #print(speed)
    elif key == ord(']'):
        tolerance += 0.01
        if tolerance >= .20:
            tolerance = .20 
    elif key == ord('[') :
        tolerance -= 0.01
        if tolerance <= 0: 
            tolerance = 0
            #print(speed)
    elif key == ord('n'):
        stepRate() 
    elif key == ord('j') or key == 0:
        sign = 1 
        signYaw = 1
        signRoll = 1
    elif key == ord('k') or key == 1:
        sign = -1 
        signYaw = -1
        signRoll = -1
    elif key == ord('t'):
        mode = "target" 
    elif key == ord('3') or key == 3:
        roll += 5
    elif key == ord('2') or key == 2:
        roll -= 5
    elif key == ord('a'):
        if (lineType==cv2.LINE_AA):
            lineType=cv2.LINE_8
            print("line_8")
        elif (lineType==cv2.LINE_8):
            lineType=cv2.LINE_4
            print("line_4")
        elif (lineType==cv2.LINE_4):
            lineType=cv2.LINE_AA
            print("line_aa")

    elif key == 27:
        keepRunning = False
        print("Waiting for threads")
        threadOneLock.release()
        threadTwoLock.release()
        threadThreeLock.release()
        threadFourLock.release()
        threadFiveLock.release()
        threadLowLock.release()
        threadOne.join()
        threadTwo.join()
        threadThree.join()
        threadFour.join()
        threadFive.join()
        threadLow.join()
        print("Finished")
        exit()
    elif key != -1:
        print ("\n\n(", key, chr(key), ") function not found\n")
        print ("(spacebar) pause\n(s) smooth mode\n(r) random mode\n(t) target mode")
        print ("(-/+) data speed control\n([/]) tolerance control")
        print ("(j/up-arrow) up\n(k/down-arrow) down\n(n) step model rate")
        print ("(a) toggle anit-alias (line_aa, line_8, line_4)")
        print ("(esc) quit\n\n")

    now = time.time()
    elapsed = now-startTime
    schedText = frameInfo
    if elapsed < (period-0.0005): # tuning by 5usec
        time.sleep(period-elapsed-0.0005) # tuning by 5usec
        totalTime = time.time()-startTime
        frameInfo = "{: >3}:    Exec ".format(frame)
        frameInfo += " {: >5.2f} msec".format(math.floor(elapsed*1000))        
        frameInfo += " {: >7.2f} msec ".format(totalTime*1000) + schedText      
    else:
        totalTime = elapsed
        frameInfo = "{: >3}:    Exec ".format(frame)
        frameInfo += " {: >5.2f} msec".format(math.floor(elapsed*1000))        
        frameInfo += " {: >7.2f} msec".format(totalTime*1000) + " ** overrun ** {: >5.2f} msec ".format((elapsed - period)*1000) + schedText

        print(frameInfo)

frame = 0
keepRunning = True
while keepRunning:
    runOneStep(frame)
    frame+=1
    if frame >= loopMax:
        frame = 0




