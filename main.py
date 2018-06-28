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
from soundlocalization import SoundLocalizationModule
import naoqi
import sys
import time
import almath
import random
from numpy import sin, cos
import numpy as np

NAO_IP = "10.84.118.19" # Default

positionErrorThresholdPos = 0.01
positionErrorThresholdAng = 0.03
NOTES = ['Laaaa','Miiiii','Dooooo','Sooool']
FREQ = [880.00,659.25,523.25,783.991]


PITCH_THRESHHOLD = 0.1
SLEEP_TIME = 4
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
        global SpeechRecogModule
        global SoundLocModule
        global VisionRecogModule
        
        try:
            
            TTSProxy = naoqi.ALProxy("ALTextToSpeech", pip, pport)
            motionProxy = naoqi.ALProxy("ALMotion", pip, pport)
            MemoryProxy = naoqi.ALProxy("ALMemory",pip, pport)
            #naoqi.ALProxy('ALBasicAwareness',pip, pport).stopAwareness()
           
            SoundReceiver = SoundReceiverModule("SoundReceiver", pip, pport)
            SpeechRecogModule = SpeechRecoModule('SpeechRecogModule', pip, pport)
            VisionRecogModule= VisionRecoModule('VisionRecoModule', pip, pport)
            SoundLocModule = SoundLocalizationModule('SoundLocModule', pip, pport)
        except Exception,e:
            print "Could not create proxy"
            print "Error was: ",e
        
        
        """
            #Detecta 'Ayuda' y guarda en qué dirección la detectó
        """
        SpeechRecogModule.start()
        SoundLocModule.start()
        TTSProxy.say('Pidame ayuda')
        MemoryProxy.insertData("speechrecog", "None")
        MemoryProxy.insertData("azimuth", "0.0")
        
        while True:
            time.sleep(3)
            try:
                readdata = MemoryProxy.getData("speechrecog")
                azimuth = float(MemoryProxy.getData("azimuth"))
            except Exception as e:
                print "readdata error", e
                readdata = ''
                azimuth = 0.0
            print azimuth
            if readdata == "ayuda":
                #MuevaLaCabeza(11)
                print azimuth
                MemoryProxy.insertData("speechrecog", "None")
                break
        TTSProxy.say('O key')
        SpeechRecogModule.stop()
        SoundLocModule.stop()

        """
            #Se mueve hacia la dirección del sonido detectado

        """
        angle = azimuth
        h = 0.2
        x = h/sin(angle)
        y = h/cos(angle)
        motionProxy.moveTo(x, y, angle)

        """
            #Detecta ukulele
            #TODO read mem values
        """
        # VisionRecogModule.start()
        # TTSProxy.say('Muéstreme el ukelele')
        # MemoryProxy.insertData("visionrecog", "None")
        # while True:
        #     readdata = ''
        #     try:
        #         readdata = MemoryProxy.getData("visionrecog")
        #     except Exception as e:
        #         print "readdata error", e
        #     if readdata == "ukulele":
        #         MemoryProxy.insertData("visionrecog", "None")
        #         break
        # VisionRecogModule.stop()
        """
            #Empieza a escuchar cada cuerda, calcula la frecuencia más cercana y dar retroalimentación para afinarla
        """
        SoundReceiver.start()
        time.sleep(SLEEP_TIME)
        i = 0
        afinando = True
        while (afinando):
            TTSProxy.say("Toque la cuerda número " + str(i+1) + ", que debe ser la nota " + NOTES[i])
            time.sleep(SLEEP_TIME)
            try:
                lastfreq =[MemoryProxy.getData("freqs"+str(j)) for j in range(0,10)]
                print "ultimasFreq :", str(lastfreq)
            except RuntimeError,e:
                # catch exception
                print "error read data", e
                lastfreq = 0

            if lastfreq != 0:
                medianfreq = np.median(lastfreq)
                TTSProxy.say("La frecuencia que escuché es  de" + str(medianfreq)[:-10] + "hercios")
                logdiff = log_diff(medianfreq,FREQ[i])
                if np.absolute(logdiff) <= PITCH_THRESHHOLD:
                    TTSProxy.say("La cuerda está afinada Muy Bien!")
                    if(i == len(NOTES)-1):
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

        """
            #Se devuele el robot al punto inicial y debería poder empezar de nuevo.
        """
        h = 0.2
        x = h/sin(angle)
        y = h/cos(angle)
        motionProxy.moveTo(x, y, angle)
        TTSProxy.say('La afinación de su ukelele está 5 de 7. Chao!')
        
    except KeyboardInterrupt:
        print "Interrupted by user, shutting down"
        SpeechRecogModule.stop()
        SoundReceiver.stop()
        SoundLocModule.stop()
        TTSProxy.say("Adios")
        myBroker.shutdown()
        sys.exit(0)
    except Exception as e:
        type, value, traceback = sys.exc_info()
        print('Error %s: %s' % (value, str(traceback)))
        SpeechRecogModule.stop()
        SoundReceiver.stop()
        SoundLocModule.stop()
        TTSProxy.say("Adios")
        myBroker.shutdown()
        raise e
        sys.exit(0)
    finally:
        print "Finally"
        SpeechRecogModule.stop()
        SoundReceiver.stop()
        SoundLocModule.stop()
        myBroker.shutdown()
        sys.exit(0)


def MuevaLaCabeza(angle):
    # Set stiffness on for Head motors
    motionProxy.setStiffnesses("Head", 1.0)
    # Will go to 1.0 then 0 radian
    # in two seconds
    motionProxy.post.angleInterpolation(
        ["HeadYaw"],
        [0.0,1.5],
        [1  , 2],
        False
    )
    # Gently set stiff off for Head motors
    motionProxy.setStiffnesses("Head", 0.0)

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