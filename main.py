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

NAO_IP = "10.0.252.126" # Default

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


    # Warning: SoundReceiver must be a global variable
    # The name given to the constructor must be the name of the
    # variable
    global SoundReceiver
    SoundReceiver = SoundReceiverModule("SoundReceiver", pip)
    SoundReceiver.start()



    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print
        print "Interrupted by user, shutting down"
        myBroker.shutdown()
        sys.exit(0)



if __name__ == "__main__":
    main()