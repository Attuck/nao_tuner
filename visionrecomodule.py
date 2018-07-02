import time
import naoqi


class VisionRecoModule(naoqi.ALModule):
    """A module to use vision recognition"""

    def __init__(self, strModuleName, strNaoIp, strNaoPort):
        naoqi.ALModule.__init__(self, strModuleName )
        self.BIND_PYTHON(self.getName(), "pictureChanged")
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
        print "datachanged", strVarName, " ", value, " ", strMessage
        try:
            objectName = value[1][0][0][0]
            print objectName
            self.memory.insertData("visionrecog",objectName)
        except Exception, e:
            print e
        
        #TODO write read mem values

    def stop(self):
        self.memory.unsubscribeToEvent("PictureDetected", self.getName())
        print "VisionRecog stopped!"













