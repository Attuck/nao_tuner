# -*- coding: utf-8 -*-

###########################################################
# Main to control al of the project´s modules.

# Syntax:
#    python scriptname --pip <ip> --pport <port>
# 
#    --pip <ip>: specify the ip of your robot (without specification it will use the NAO_IP defined some line below
#
# Author: Ricardo Apú, Pablo Vargas, Jean Carlo Zúñiga
# UCR
###########################################################

from optparse import OptionParser
from soundreciever import SoundReceiverModule
import naoqi
import sys
import time
import almath
import random

NAO_IP = "10.0.252.126" # Default

positionErrorThresholdPos = 0.01
positionErrorThresholdAng = 0.03



def main():
    """ Main entry point
    """
    parser = OptionParser()
    parser.add_option("--pip",
        help="Parent broker port. The IP address or your robot",
        dest="pip")
    parser.add_option("--pport",
        help="Parent broker port. The port NAOqi is listening to",
        dest="pport",
        type="int")
    parser.set_defaults(
        pip=NAO_IP,
        pport=9559)

    (opts, args_) = parser.parse_args()
    pip   = opts.pip
    pport = opts.pport
    
    # We need this broker to be able to construct
    # NAOqi modules and subscribe to other modules
    # The broker must stay alive until the program exists
    myBroker = naoqi.ALBroker("myBroker",
    "0.0.0.0",   # listen to anyone
    0,           # find a free port and use it
    pip,         # parent broker IP
    pport)       # parent broker port
    try:    
        ##
        global motionProxy
        motionProxy = naoqi.ALProxy("ALMotion", pip, pport)

        # Warning: SoundReceiver must be a global variable
        # The name given to the constructor must be the name of the
        # variable


        naoqi.ALProxy('ALBasicAwareness').stopAwareness()

        MuevaLaCabeza()
        theHeadPosition = motionProxy.getPosition("Head", 0, False)
        
        print theHeadPosition
        
        x = 0.5
        y = 0.0
        Theta = theHeadPosition[4] 
        AnguloHeadYaw = theHeadPosition[4] 
        AnguloHeadPitch = theHeadPosition[5]   
        RoteElCuerpo(Theta, AnguloHeadYaw, AnguloHeadPitch)    
            
        MuevaseAUkelele(x, y, Theta)

        global SoundReceiver
        SoundReceiver = SoundReceiverModule("SoundReceiver", pip, pport)
        SoundReceiver.start()
        time.sleep(5)
        try:
            # create proxy on ALMemory
            memProxy = naoqi.ALProxy("ALMemory",pip, pport)
            #getData
            lastfreq = memProxy.getData("ultimaFreq")
            print "ultimaFreq :", str(lastfreq)
        except RuntimeError,e:
            # catch exception
            print "error read data", e
            lastfreq = 0

        try:
            tts = naoqi.ALProxy("ALTextToSpeech", pip, pport)
            if lastfreq != 0:
                tts.say("La frecuencia que escuché es  de" + str(lastfreq) + "hercios")
            else:
                tts.say("No pude escuchar ni picha, Adiós")
        except Exception,e:
            print "Could not create proxy to ALTextToSpeech"
            print "Error was: ",e
        SoundReceiver.STOP()
        DeMediaVuelta() 
        MuevaseAlCentro(x, y, Theta)
        DeMediaVuelta() 

        
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print
        print "Interrupted by user, shutting down"
        myBroker.shutdown()
        sys.exit(0)



def MuevaLaCabeza():
    motionProxy.setAngles("HeadYaw", random.uniform(-1.0, 1.0), 0.6)
    motionProxy.setAngles("HeadPitch", random.uniform(-0.5, 0.5), 0.6)
    theHeadPosition = motionProxy.getPosition("Head", 0, False)
    targetPos  = almath.Position6D(theHeadPosition)
    
    target  = [
        theHeadPosition[0],
        theHeadPosition[1],
        theHeadPosition[2],
        theHeadPosition[3],
        theHeadPosition[4],
        theHeadPosition[5]]
    fractionMaxSpeed = 0.5
    axisMask         = 7 # just control position
    motionProxy.waitUntilMoveIsFinished()

def RoteElCuerpo (Theta, AnguloHeadYaw, AnguloHeadPitch):  
    fractionMaxSpeed = 0.5
    axisMask         = 7 # just control position   
    motionProxy.moveTo(0.0, 0.0, Theta)
    angulos = [0, 0]
    nombres = ["HeadYaw", "HeadPitch" ]
    motionProxy.setAngles(nombres, angulos, fractionMaxSpeed)
    theHeadPosition = motionProxy.getPosition("Head", 0, False)
    targetPos  = almath.Position6D(theHeadPosition)
        
def MuevaseAUkelele( x, y, Theta):
    print "ahora caminando hacia el chico"  
    print "en x: " + str(x) + "\nen y: " + str(y) + "\nen Theta: " + str(Theta)
    motionProxy.moveToward(x, y, Theta)
    EjecuteMovimiento(x, y, Theta)

def MuevaseAlCentro( x, y, Theta):
    print "ahora caminando hacia el centro" 
    x = x * -1
    y = y * -1 
    motionProxy.moveToward(x, y, Theta)
    EjecuteMovimiento(x, y, Theta)   

def DeMediaVuelta():
    motionProxy.moveTo(0.0, 0.0, 3.14159)

def EjecuteMovimiento( x, y, Theta):
    x = 0.5
    y = 0.0
    initPosition = almath.Pose2D(motionProxy.getRobotPosition(True))
    print "EJECUTE en x: " + str(x) + "\nen y: " + str(y) + "\nen Theta: " + str(Theta)
    targetDistance = almath.Pose2D(x,y,Theta * almath.PI / 180)
    expectedEndPosition = initPosition * targetDistance
    # enableArms = self.getParameter("Arms movement enabled")
    # self.motion.setMoveArmsEnabled(enableArms, enableArms)
    motionProxy.moveTo(x,y, Theta * almath.PI / 180)

    # The move is finished so output
    realEndPosition = almath.Pose2D(motionProxy.getRobotPosition(False))
    positionError = realEndPosition.diff(expectedEndPosition)
    positionError.theta = almath.modulo2PI(positionError.theta)
    if (abs(positionError.x) < positionErrorThresholdPos
        and abs(positionError.y) < positionErrorThresholdPos
        and abs(positionError.theta) < positionErrorThresholdAng):
        #onArrivedAtDestination()
        print "on arrived destination"
    else:
        #onStoppedBeforeArriving(positionError.toVector())
        print "onStoppedBeforeArriving" + str(positionError.toVector())

if __name__ == "__main__":
    main()