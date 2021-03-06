

import time
import naoqi

class SoundLocalizationModule(naoqi.ALModule):
    """A module to use sound localization"""

    def __init__(self, strModuleName, strNaoIp, strNaoPort):
        naoqi.ALModule.__init__(self, strModuleName )
        self.BIND_PYTHON( self.getName(),"callback" )
        self.strNaoIp = strNaoIp
        self.strNaoPort = strNaoPort
        try:
            self.sd = naoqi.ALProxy("ALSoundDetection", strNaoIp, strNaoPort)
        except Exception,e:
            print "Could not create proxy to ALSoundDetection",e
        try:
            self.memory = naoqi.ALProxy("ALMemory", strNaoIp, strNaoPort)
        except RuntimeError,e:
            print "Error when creating ALMemory proxy:"+str(e)

    def start(self):
        self.memory.subscribeToEvent("ALSoundLocalization/SoundLocated", self.getName(), "soundDetected")
        try:
            self.sd.subscribe(self.getName())
        except RuntimeError,e:
            print "Error when subscribing to micro event", e
        self.sd.setParameter("Sensitivity", 0.1)

    def soundDetected(self, strVarName, value, strMessage):
        """callback when data change"""
        self.memory.insertData("azimuth", value[1][0])
        print "az", (value[1][0])
        #print "FOFI_sound_localization-detected", strVarName, " ", value, " ", strMessage,"\n"

    def stop(self):
        self.memory.unsubscribeToEvent("ALSoundLocalization/SoundLocated", self.getName())
        self.sd.unsubscribe(self.getName())










