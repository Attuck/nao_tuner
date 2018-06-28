

import time
import naoqi

memValue = "PictureDetected" # ALMemory variable where the ALVisionRecognition module outputs its results.


class VisionRecoModule(naoqi.ALModule):
    """A module to use vision recognition"""


    def __init__(self, strModuleName, strNaoIp, strNaoPort):
        naoqi.ALModule.__init__(self, strModuleName )
        #self.BIND_PYTHON( self.getName(),"callback" )
        self.strNaoIp = strNaoIp
        self.strNaoPort = strNaoPort
        try:
            self.memory = naoqi.ALProxy("ALMemory", strNaoIp, strNaoPort)
        except RuntimeError,e:
            print "Error when creating ALMemory proxy:"+str(e)
    
    def start(self):
        """Have the python module called back when picture recognition results change."""
        try:
            self.memory.subscribeToEvent("PictureDetected", self.getName(), "pictureChanged")
        except RuntimeError,e:
            print "Error when subscribing to micro event"
            exit(1)
        print "VisionRecog started!"
        
    def pictureChanged(self, strVarName, value, strMessage):
        """callback when data change"""
        print "FOFI_vision_recog-detected", strVarName, " ", value, " ", strMessage
        self.memory.insertData("visionrecog", "ukulele")
        #TODO write read mem values

    def stop(self):
        self.memory.unsubscribeToEvent("PictureDetected", self.getName())
        print "VisionRecog stopped!"












