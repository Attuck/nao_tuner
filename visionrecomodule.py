#LEARN  IMAGES

import time
import naoqi

# create python module
class VisionRecoModule(ALModule):
    """A module to use vision recognition"""

    memValue = "PictureDetected" # ALMemory variable where the ALVisionRecognition module outputs its results.

    def __init__(self, strModuleName, strNaoIp, strNaoPort):
        naoqi.ALModule.__init__(self, strModuleName )
        self.strNaoIp = strNaoIp
        self.strNaoPort = strNaoPort
        try:
            self.memory = ALProxy("ALMemory", strNaoIp, strNaoPort)
        except RuntimeError,e:
            print "Error when creating ALMemory proxy:"+str(e)
    
    def start(self):
        """Have the python module called back when picture recognition results change."""
        try:
        memoryProxy.subscribeToEvent(self.memValue, self.getName(), "pictureChanged")
        except RuntimeError,e:
        print "Error when subscribing to micro event"
        exit(1)
        
    def pictureChanged(self, strVarName, value, strMessage):
        """callback when data change"""
        print "datachanged", strVarName
        #TODO write read mem values

    def stop(self):
        memoryProxy.unsubscribeToEvent(memValue, moduleName)













