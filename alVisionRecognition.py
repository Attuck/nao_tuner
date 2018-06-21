#LEARN  IMAGES

import time
from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule

count = 10
period = 500
moduleName = "pythonModule"
NAO_IP = "10.84.118.19"  # Replace here with your NaoQi's IP address.
PC_IP = "127.0.0.1"   # Replace here with your computer IP address
PORT = 9559
memValue = "PictureDetected" # ALMemory variable where the ALVisionRecognition module outputs its results.


print("Creando modulo")

# create python module
class myModule(ALModule):
  """python class myModule test auto documentation"""

  def pictureChanged(self, strVarName, value, strMessage):
    """callback when data change"""
    print "datachanged", strVarName, " ", value, " ", strMessage
    global count
    count = count-1

myBroker = ALBroker("myBroker",
  "0.0.0.0",   # listen to anyone
  0,           # find a free port and use it
  NAO_IP,         # parent broker IP
  PORT)       # parent broker port
pythonModule = myModule(moduleName)

print("creando proxy de memoria")
# Create a proxy to ALMemory
try:
  memoryProxy = ALProxy("ALMemory", NAO_IP, PORT)
except RuntimeError,e:
  print "Error when creating ALMemory proxy:"
  exit(1)


# Have the python module called back when picture recognition results change.
try:
  memoryProxy.subscribeToEvent(memValue, moduleName, "pictureChanged")
except RuntimeError,e:
  print "Error when subscribing to micro event"
  exit(1)


# Let the picture recognition run for a little while (will stop after 'count' calls of the callback).
# You can check the results using a browser connected on your Nao, then
# Advanced -> Memory -> type PictureDetected in the field
while count>0:
  time.sleep(1)


# unsubscribe modules
memoryProxy.unsubscribeToEvent(memValue, moduleName)
#recoProxy.unsubscribe(moduleName)


print 'end of vision_recognition python script'











