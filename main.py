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
from speechrecomodule import SpeechRecoModule
from visionrecomodule import VisionRecoModule
import naoqi
import sys
import time
import almath
import random
from naoqi import ALProxy

NAO_IP = "10.0.252.126" # Default

positionErrorThresholdPos = 0.01
positionErrorThresholdAng = 0.03
"""
NOTES_TO_FREQ ={:'La':864.00,
                :'Mi':323.63,
                :'Do':256.87,
                :'Sol':384.87}
                """
PITCH_THRESHHOLD = 0.2
SLEEP_TIME = 2
def log_diff(n,m):
    return np.log(n) - np.log(m)


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
        
        global SoundReceiver
        global motionProxy
        global SpeechRecogModule

        try:
            SoundReceiver = SoundReceiverModule("SoundReceiver", pip, pport)
            tts = naoqi.ALProxy("ALTextToSpeech", pip, pport)
            naoqi.ALProxy('ALBasicAwareness',pip, pport).stopAwareness()
            MemoryProxy = naoqi.ALProxy("ALMemory",pip, pport)
            SpeechRecogModule = SpeechRecoModule('SpeechRecogModule', pip, pport)
            motionProxy = naoqi.ALProxy("ALMotion", pip, pport)
            VisionRecogModule= VisionRecoModule('VisionRecoModule', pip, pport)
        except Exception,e:
            print "Could not create proxy"
            print "Error was: ",e
        
        
        """
            #Detecta 'Ayuda' 
        """
        SpeechRecogModule.start()
        end_time = time.time() + 10 #cada 10 segundos dice algo
        recognized_help = False
        loop_regog = True
        while loop_regog:
            readdata = MemoryProxy.getData("speechrecog")
            while not recognized_help:
                if readdata == "ayuda":
                    recognized_help = True
                    loop_regog = False
                else:
                    if time.time() > end_time:
                        break
                    readdata = MemoryProxy.getData("speechrecog")
            tts.say("Pídame ayuda")
        SpeechRecogModule.stop()

        """
            #Detecta dirección y se mueve hacia el sonido
            #TODO
        """
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
        """
            #Detecta ukulele
            #TODO read mem values
        """
        VisionRecogModule.start()
        time.sleep(15)
        VisionRecogModule.stop()
        """
            #Empieza a escuchar cada cuerda, calcula la frecuencia más cercana y dar retroalimentación para afinarla
        """
        SoundReceiver.start()
        time.sleep(SLEEP_TIME)
        i = 0
        afinando = True
        notas = NOTES_TO_FREQ.keys()
        while (afinando):
            TTSProxy.say("Toque la cuerda número " str(i+1) ", que debe ser la nota " + notas[i])
            try:
                lastfreq =[MemoryProxy.getData("freqs"+i) for i in range(0,10)]
                print "ultimasFreq :", str(lastfreq)
            except RuntimeError,e:
                # catch exception
                print "error read data", e
                lastfreq = 0

            if lastfreq != 0:
                medianfreq = np.median(lastfreq)
                TTSProxy.say("La frecuencia que escuché es  de" + str(medianfreq) + "hercios")
                logdiff = log_diff(medianfreq,NOTES_TO_FREQ[notas[i]])
                if abs(log_diff) <= PITCH_THRESHHOLD:
                    TTSProxy.say("La cuerda está afinada Muy Bien!")
                    if(i == len(NOTES_TO_FREQ)-1):
                        afinando = False
                    else:
                        i+=1
                else:
                    if logdiff > 0:
                        TTSProxy.say("La cuerda está muy alta, bájele")
                    else:
                        TTSProxy.say("La cuerda está muy baja, súbale")
            else:
                TTSProxy.say("No pude escuchar ni picha, Baaai")
            time.sleep(SLEEP_TIME)
            i+=1

        """
            #Se devuele el robot al punto inicial y debería poder empezar de nuevo.
        """
        SoundReceiver.pause()
        DeMediaVuelta() 
        MuevaseAlCentro(x, y, Theta)
        DeMediaVuelta()
        
    except KeyboardInterrupt:
        print "Interrupted by user, shutting down"
        SpeechRecogModule.stop()
        SoundReceiver.stop()
        TTSProxy.say("Adios")
        myBroker.shutdown()
        sys.exit(0)
    finally:
        print "Interrupted by user, shutting down"
        SpeechRecogModule.stop()
        SoundReceiver.stop()
        TTSProxy.say("Adios")
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