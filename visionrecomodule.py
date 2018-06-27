

import time
import naoqi


class VisionRecoModule(ALModule):
    """A module to use vision recognition"""

    memValue = "PictureDetected" # ALMemory variable where the ALVisionRecognition module outputs its results.

    def __init__(self, strModuleName, strNaoIp, strNaoPort):
        naoqi.ALModule.__init__(self, strModuleName )
        self.BIND_PYTHON( self.getName(),"callback" )
        self.strNaoIp = strNaoIp
        self.strNaoPort = strNaoPort
        try:
            self.memory = naoqi.ALProxy("ALMemory", strNaoIp, strNaoPort)
        except RuntimeError,e:
            print "Error when creating ALMemory proxy:"+str(e)
    
    def start(self):
        """Have the python module called back when picture recognition results change."""
        try:
        self.memory.subscribeToEvent(memValue, self.getName(), "pictureChanged")
        except RuntimeError,e:
        print "Error when subscribing to micro event"
        exit(1)
        
    def pictureChanged(self, strVarName, value, strMessage):
        """callback when data change"""
        print "FOFI_vision_recog-detected", strVarName, " ", value, " ", strMessage
        #TODO write read mem values

    def stop(self):
        self.memory.unsubscribeToEvent(memValue, self.getName())













