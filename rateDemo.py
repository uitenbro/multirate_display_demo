import threading
import time
import math

nativeRate = 40.0 # 40Hz
period = 1/nativeRate # 25 msec
frameModulo = 3 # Modulo 3 of 40Hz gives a 13.33Hz rate (75msec period)
jitter = 10/100 # 10% jitter in scheduling will be reported
keepRunning = True # Boolean to support execution loop
frame = 0  # minor frame number
frameInfo = "" # Text to capture frame information
loopMax = 120 # Major frame loop counter must ensure smooth rollover
nativeRateWorkload = 19/1000 # msec
threadOneWorkload = 50/1000 # msec

def runRateOneThread():
    global nativeRate
    global jitter
    global keepRunning
    global threadOneWorkload

    #initialize start and elapsed time
    startTime = 0
    elapsed = 0
    
    # calculate deadline duration
    deadlineDuration =1/(nativeRate/frameModulo)

    # main loop for the thread
    while keepRunning:

        # wait for the semphore to be released from scheduler
        threadOneLock.acquire()

        # if this is the first execution
        if startTime == 0:       

            # capture initial start time
            startTime = time.time()

        # after the first execution
        else: 

            # calculate total time since previous startTime
            now = time.time()
            totalTime = now - startTime
            
            # capture new start time
            startTime = now
            
            # compare the total duration against the deadline for jitter
            frameInfo = "{:>3}:".format(frame)
            frameInfo += " {: >5.2f}Hz".format(nativeRate/frameModulo)
            frameInfo += " Used {: >5.2f} msec".format(math.floor(elapsed*1000))
            frameInfo += " of Total Frame {: >7.2f} msec".format(totalTime*1000)
            if (totalTime < deadlineDuration*(1-jitter) or totalTime > deadlineDuration*(1+jitter)):
                frameInfo += " ** violation ** {: >7.2f} msec".format((totalTime-deadlineDuration)*1000)
                frameInfo += " > {: >7.2f}%".format(jitter*100)
            print(frameInfo)

        # do work for this thread
        time.sleep(threadOneWorkload) # simulate thread workload 

        # capture elapsed time for this thread
        elapsed = time.time() - startTime

    print("Finished Thread")

# create an aperiodic thread and associate a function
threadOne = threading.Thread(target=runRateOneThread)
threadOneStarted = False
# create a semphore to control periodic execution of the aperiodic thread
threadOneLock = threading.Lock()

# define minor frame step function
def runOneStep(frame):
    global threadOneStarted
    global nativeRate
    global period
    global nativeRateWorkload

    # Capture minor frame start time
    startTime = time.time()
    
    # Initialize frame info text
    frameInfo = ""
    
    # Run native rate items
    time.sleep(nativeRateWorkload) # simulate workload of processing

    # if its time to start the aperiodic task (determined by frame counting)
    if (frame % frameModulo) == 0: 

        # capture frame information
        frameInfo += " {:0.2f}Hz".format(nativeRate/frameModulo)

        # start the thread if it isn't already started
        if (threadOneStarted == False):
            threadOne.start()
            threadOneStarted = True

        # give the semaphore to unblock the thread at the appropriate rate
        threadOneLock.release()
    
    # setup sleep timer to create periodic rate exuction associated with the nativeRate
    now = time.time()
    elapsed = now-startTime
    schedText = frameInfo

    # If elapsed time is less than the period
    if elapsed < (period): 
        # sleep remaining time to get to periodic rate
        time.sleep(period-elapsed)
        # capture total time for display
        totalTime = time.time()-startTime
        frameInfo = "{: >3}:    Exec".format(frame)
        frameInfo += " Used {: >5.2f} msec".format(math.floor(elapsed*1000))        
        frameInfo += " of Total Frame {: >7.2f} msec ".format(totalTime*1000) + schedText      
    # elapsed time greater than period therefore the scheduler has overrun
    else:
        # set total time to elapsed time and print error
        totalTime = elapsed
        frameInfo = "{: >3}:    Exec".format(frame)
        frameInfo += " Used {: >5.2f} msec".format(math.floor(elapsed*1000))        
        frameInfo += " of Total Frame {: >7.2f} msec".format(totalTime*1000) + " ** overrun ** {: >5.2f} msec ".format((elapsed - period)*1000) + schedText

    # print frame excution timing data
    print(frameInfo)

# setup a minor frame counter that runs the minor frame, counts, and rolls over as needed
while keepRunning:
    runOneStep(frame)
    frame+=1
    if frame >= loopMax:
        frame = 0
        print("type 'stop' to quit, anything else to continue")
        stop  = input()
        print (stop)
        if stop == "stop": keepRunning = False # stop the threading loop so it exits

# stop thread and then exit
threadOneLock.release()
threadOne.join()