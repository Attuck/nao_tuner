#LEARN  IMAGES

import time
from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule

count = 1000
period = 500
moduleName = "pythonModule"
NAO_IP = "10.84.118.19"  # Replace here with your NaoQi's IP address.
PC_IP = "127.0.0.1"   # Replace here with your computer IP address
PORT = 9559
memValue = "SoundDetected" # ALMemory variable where the ALVisionRecognition module outputs its results.

#-------------------------------------MODULE--------------------------------
print("Creando modulo de ALSL")
class myModule(ALModule):

  def SoundDetected(self, strVarName, value, strMessage):
    """callback when data change"""
    print "FOFI_sound_localization-detected", strVarName, " ", value, " ", strMessage
    global count
    count = count-1

myBroker = ALBroker("myBroker",
  "0.0.0.0",   # listen to anyone
  0,           # find a free port and use it
  NAO_IP,         # parent broker IP
  PORT)       # parent broker port
pythonModule = myModule(moduleName)
#--------------------------------PROXY----------------------------------------
print("Creando Proxy de ALSL")
try:
    sd = ALProxy("ALSoundDetection", NAO_IP, PORT)
	
except Exception,e:
    print "Could not create proxy to ALSoundDetection"
    print "Error was: ",e
    sys.exit(1)
memoryProxy = ALProxy("ALMemory", NAO_IP, PORT)
# Sets the sensitivity of the detection to 0.3 (less sensitive than default).
# The default value is 0.9.
sd.setParameter("Sensitivity", 0.3)
print ("Sensitivity set to 0.5")
#-----------------------------EVENT-----------------------------------------
memoryProxy.subscribeToEvent("ALSoundLocalization/SoundLocated", moduleName, "SoundDetected")
try:
	
	sd.subscribe(moduleName)
except RuntimeError,e:
  print "Error when subscribing to micro event"
  exit(1)

while count>0:
  time.sleep(1)


memoryProxy.unsubscribeToEvent(memValue, moduleName)
sd.unsubscribe(moduleName)

print ('end of sound_localization python script')


#______________________________END__________________________________________________











