# -*- coding: utf-8 -*-

###########################################################
# Module that retrieves robot´s audio buffer, computes the fft(Fast fourier transform) of the given window and estimates the pitch of what its hearing.
#
#
# Author: Ricardo Apú ( https://github.com/Attuck)
# Based on work by Alexandre Mazel (https://stackoverflow.com/a/24699052) and Matt Zucker (https://github.com/mzucker/python-tuner)
###########################################################

import naoqi
import numpy as np

# Constant to send to the ALAudiodevice and use to compute the pitch based on the fft
SAMPLE_RATE = 48000

class SoundReceiverModule(naoqi.ALModule):
    """
    Use this object to get call back from the ALMemory of the naoqi world.
    Your callback needs to be a method with two parameter (variable name, value).
    """

    def __init__( self, strModuleName, strNaoIp, strNaoPort ):
        try:
            naoqi.ALModule.__init__(self, strModuleName )
            self.BIND_PYTHON( self.getName(),"callback" )
            self.strNaoIp = strNaoIp
            self.strNaoPort = strNaoPort
            self.outfile = None
            self.aOutfile = [None]*(4-1); # ASSUME max nbr channels = 4
            # create proxy on ALMemory
            self.memProxy = naoqi.ALProxy("ALMemory",strNaoIp,strNaoPort)
            self.pause = False
            self.write_index = 0
            self.MAX_INDEX = 10

        except BaseException, err:
            print( "ERR: abcdk.naoqitools.SoundReceiverModule: loading error: %s" % str(err) );

    # __init__ - end
    def __del__( self ):
        print( "INF: abcdk.SoundReceiverModule.__del__: cleaning everything" )
        self.stop()

    def start( self ):
        audio = naoqi.ALProxy( "ALAudioDevice", self.strNaoIp, 9559 )
        nNbrChannelFlag = 3 # ALL_Channels: 0,  AL::LEFTCHANNEL: 1, AL::RIGHTCHANNEL: 2; AL::FRONTCHANNEL: 3  or AL::REARCHANNEL: 4.
        nDeinterleave = 0
        nSampleRate = SAMPLE_RATE
        audio.setClientPreferences( self.getName(),  nSampleRate, nNbrChannelFlag, nDeinterleave ) # setting same as default generate a bug !?!
        audio.subscribe( self.getName() )
        self.pause = True
        print( "INF: SoundReceiver: started!" )

    def stop( self ):
        print( "INF: SoundReceiver: stopping..." )
        audio = naoqi.ALProxy( "ALAudioDevice", self.strNaoIp, 9559 )
        audio.unsubscribe( self.getName() )
        self.pause = False
        print( "INF: SoundReceiver: stopped!" )
        if( self.outfile != None ):
            self.outfile.close()


    def processRemote( self, nbOfChannels, nbrOfSamplesByChannel, aTimeStamp, buffer ):
        """
        This is THE method that receives all the sound buffers from the "ALAudioDevice" module
        """
        #~ print( "process!" );
        #~ print( "processRemote: %s, %s, %s, lendata: %s, data0: %s (0x%x), data1: %s (0x%x)" % (nbOfChannels, nbrOfSamplesByChannel, aTimeStamp, len(buffer), buffer[0],ord(buffer[0]),buffer[1],ord(buffer[1])) );
        #~ print( "raw data: " ),
        #~ for i in range( 8 ):
            #~ print( "%s (0x%x), " % (buffer[i],ord(buffer[i])) ),
        #~ print( "" );
        if( self.pause ):
            aSoundDataInterlaced = np.fromstring( str(buffer), dtype=np.int16 )
            #~ print( "len data: %s " % len( aSoundDataInterlaced ) );
            #~ print( "data interlaced: " ),
            #~ for i in range( 8 ):
                #~ print( "%d, " % (aSoundDataInterlaced[i]) ),
            #~ print( "" );
            aSoundData = np.reshape( aSoundDataInterlaced, (nbOfChannels, nbrOfSamplesByChannel), 'F' )
            #~ print( "len data: %s " % len( aSoundData ) );
            #~ print( "len data 0: %s " % len( aSoundData[0] ) );
                # compute fft
            nBlockSize = nbrOfSamplesByChannel
            signal = aSoundData[0] * np.hanning( nBlockSize )
            aFft = ( np.fft.rfft(signal) / nBlockSize )
            fftData=abs(aFft)**2
            # find the maximum
            which = fftData[1:].argmax() + 1
            # use quadratic interpolation around the max if its not the last
            if which != len(fftData)-1:
                y0,y1,y2 = np.log(fftData[which-1:which+2:])
                x1 = (y2 - y0) * .5 / (2 * y1 - y2 - y0)

                # find the frequency and output it
                thefreq = (which+x1)*SAMPLE_RATE/nBlockSize
                #ignora frecuencias demasiado altas: probablemente ruido.
                if thefreq < 1100:
                    print "The freq is %f Hz." % (thefreq)
                    try:
                        #insertData. Value can be int, float, list, string
                        self.memProxy.insertData("freqs"+str(self.write_index % self.MAX_INDEX), thefreq)
                        #print "freqs"+str(self.write_index % self.MAX_INDEX)
                        self.write_index+=1
                    except RuntimeError,e:
                        # catch exception
                        print "error insert data", e
            else:
                thefreq = which*SAMPLE_RATE/nBlockSize
                if thefreq < 1100:
                    print "The freq is %f Hz." % (thefreq)
                    try:
                        #insertData. Value can be int, float, list, string
                        self.memProxy.insertData("freqs"+ str(self.write_index % self.MAX_INDEX), thefreq)
                        #print "freqs"+str(self.write_index % self.MAX_INDEX)
                        self.write_index+=1
                    except RuntimeError,e:
                        # catch exception
                        print "error insert data", e
            return 0
    # processRemote - end

    def pause( self ):
        self.pause = False
        self.write_index = 0

    def resume( self ):
        self.pause = True

    def version( self ):
        return "0.6"

# SoundReceiver - end
