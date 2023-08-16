# -*- coding: utf-8 -*-
"""
A simple spoofing example
"""

#############################################
# The following code demonstrates a simple  #
# log file data transmission of an RS41     #
# radiosonde with an RS41-SG/P radiosonde   #
# simulation framework. The code loads      #
# messages from an RS41 log file and        #
# transmits the new message (via an audio   #
# channel or an RF transmitter) in one-     #
# second intervals.                         #
#                                           #
# The code was written by Paz Hameiri in    #
# 2023                                      #
#                                           #
# For more information regarding the RS41'  #
# transmission protocol, see bazjo's work   #
# on RS41 radiosonde at:                    #
# https://github.com/bazjo/RS41_Decoding    #
#                                           #
# If required, install the following:       #
# pip install pyserial                      #
# pip install pyaudio                       #
# pip install skyfield                      #
# pip install keyboard                      #
# pip install pymap3d                       #
# pip install reedsolo                      #
#############################################

from time import sleep
import serial
import pyaudio
from threading import Thread
from skyfield.api import load
import random
import datetime
import keyboard

from RS41Functions import *
from RS41SubframeRW import *
from RS41BlocksRW import *
from RS41SimFunctions import *

# Selects between serial transmission and audio transmission
SerialOrAudio = "Audio"
COMPort = "COM3"

# Define a tranmission function
def TxFunction():
    PrevTriggerTx = False
    while RunTxFunction:
        if (TriggerTx and (TriggerTx != PrevTriggerTx)):
            PrevTriggerTx = TriggerTx
            print("                                                                   Tx: "
                  + datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M:%S.%f")[:-4])
            
            # Check if the output should go to the serial port or to the audio
            if SerialOrAudio == "Serial":
                # Write to the serial port
                ser.write(RFMessageByteArray[0:RFMessageNumOfBytes])
            else:
                AudioStream.write((Amplitude*WaveData).tobytes())
                
        elif TriggerTx != PrevTriggerTx:
            PrevTriggerTx = TriggerTx
        sleep(0.02)

# Define subframe array
SubFrameArray = bytearray(51*16) # 51*16 bytes

# %% RS-41 Model declarations
#############################################
# RS-41 Model declarations #
#############################################

FrameLength = 0x140 # 320 bytes per RS41 regular frame message
LastSubframe = 50 # Last subframe number in each subframe cycle

# %% Program start
#############################################
# Program start #
#############################################

# Open a log file and read its contents
LogFileName = 'RS41-SGP 2021-01-09-S1511071.txt'
LoggedMessagesLength, LoggedMessages = ReadLogFile(LogFileName)

# Declare message bytes array
MessageBytes = bytearray(1024)

# Load Subframe data from the text file
LoadSuccess, LoggedMessageIndex = LoadSubframeDataFromLog(LastSubframe + 1, LoggedMessagesLength,
                                                        LoggedMessages, SubFrameArray, MessageBytes)

if not(LoadSuccess):
    print("Loading the subframes data from the log file failed")

# RS41 Preamble = 40 bytes of 0x55
PreambleLength = 40
Preamble = bytearray([0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55,
                      0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55,
                      0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55,
                      0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55])

# Prefrom data whitening and reverse bits order MSB->LSB, LSB->MSB
ReversedEncryptedMessageBytes = DataWhitening(FrameLength, MessageBytes)

# Gather the complete data bytes that will be transmitted
TxDataBytes = Preamble + ReversedEncryptedMessageBytes

# Calculate the number of bytes to be tranmitted
TxDataBytesLength = 40 + FrameLength # 40 preamble bytes + FrameLength [Bytes]

# Define RS-41 DataRate
DataRate = 4800 # [BAUD]

# Define RS-41 RF transmission parameters
FrequencyStart = 401400000 # [Hz]
FrequencyDeviation = 2400 # [Hz]

TxFrequency = FrequencyStart/1000000

# Define RS-41 RF transmission parameters for HELTEC LoRa Node 151 433MHz
Modulation = 2 # 2 = Gaussian filter BT = 0.5
Power = -3 # Output power in dBm:  Supports -3dBm to +16dBm, +20dBm

# Calculate the number of bytes in the packet
RFMessageHeaderLength = 16
RFMessageNumOfBytes = RFMessageHeaderLength + TxDataBytesLength # 16 header bytes + TxDataBytes [Bytes]
# Build the RF message byte array
RFMessageByteArray = SetupRFMessage(RFMessageNumOfBytes, TxDataBytesLength, FrequencyStart, DataRate, FrequencyDeviation, Modulation, Power)

# Prepeare the tranmission channel (Serial/Audio)
# Check if the output should go to the serial port or to the audio
if SerialOrAudio == "Serial": 
    # Setup the serial port
    ser = serial.Serial(COMPort, 57600, timeout=0.7) 
else:
    # Define a WAV parameters
    Amplitude = 0.5 # In range of [0:1]
    SamplesRate = 44100 # In samples/seconds
    SampleRateMultipliler = SamplesRate / DataRate
    
    # Prepare an audio channel
    PAudio = pyaudio.PyAudio()
    AudioStream = PAudio.open(format = pyaudio.paFloat32, channels = 1, rate = SamplesRate, output = True)

# Data transmission loop
LoggedMessageIndex = 0
PreviousFrameNumber = -1

DebugSeconds = 10000000

TriggerTx = False
RunTxFunction = True

if __name__ == '__main__':
    Thread(target = TxFunction).start()

InitialUTCTime = datetime.datetime.now(datetime.timezone.utc)
TxPreparationUTCTime = InitialUTCTime
TxUTCTime = InitialUTCTime + datetime.timedelta(seconds=10)

DebugTimeDiff = 0
while (LoggedMessageIndex < LoggedMessagesLength) and (DebugTimeDiff < DebugSeconds):
    UTCTime = datetime.datetime.now(datetime.timezone.utc)
    UTCTimeMicroseconds = UTCTime.microsecond
    
    DebugTimeDiff = int((UTCTime - InitialUTCTime).total_seconds())
    
    if (UTCTimeMicroseconds < 50000) & (UTCTime >= TxPreparationUTCTime):
        # Prepare the next data to be transmitter
                 
        # Load the logged message
        LogRecordToMessageBytes(LoggedMessageIndex, LoggedMessages, MessageBytes)

        # Try and correct the data using the Reed-Solomon ECC
        RSRecovered = False
        try:
            RSRecovered = DecodeReedSolomon(MessageBytes)
        except Exception: 
            pass

        # Advance LoggedMessageIndex
        LoggedMessageIndex = LoggedMessageIndex + 1
        
        # Zero frame number skipping time
        FrameSkippingSleepTime = 0
        
        # Check RS41 STATUS block CRC code
        if CheckSTATUSblockCRC(MessageBytes):
            # Get frame number
            FrameNumber = GetFrameNumber(MessageBytes)
            
            # Check if there's a previous FrameNumber.
            # If so, calculate sleeping time in case of frame number skipping
            if (PreviousFrameNumber > -1):
                FrameSkippingSleepTime = FrameNumber - PreviousFrameNumber - 1
            
            # Update PreviousFrameNumber
            PreviousFrameNumber = FrameNumber

        # Calculate future transmission time
        TxUTCTime = UTCTime.replace(microsecond=0) + datetime.timedelta(seconds=FrameSkippingSleepTime)
        TxPreparationUTCTime = TxUTCTime + datetime.timedelta(seconds=1)
        
        # Prefrom data whitening and reverse bits order MSB->LSB, LSB->MSB
        ReversedEncryptedMessageBytes = DataWhitening(FrameLength, MessageBytes)

        # Place the data bytes in the outgoing message
        TxDataBytes[PreambleLength:TxDataBytesLength] = ReversedEncryptedMessageBytes
        RFMessageByteArray[16:16+TxDataBytesLength] = TxDataBytes
        
        # Check if the output should go to the serial port or to the audio
        if SerialOrAudio == "Audio":
            # Build the wave data from the TxDataBytes and wave paramters
            WaveData = BuildAudioStream(TxDataBytes, TxDataBytesLength, SampleRateMultipliler, DataRate, SamplesRate)
             
        # Print preparation details
        print('Prep end: ' + datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M:%S.%f")[:-4] +
              ', Skip time: ' + str(FrameSkippingSleepTime) +
              ', Next prep: ' + TxPreparationUTCTime.strftime("%H:%M:%S") +
              ', Expected Tx: ' + TxUTCTime.strftime("%H:%M:%S"))

    # Flag transmission
    if ((UTCTimeMicroseconds > 600000) and (UTCTimeMicroseconds < 700000) and (TriggerTx == False) and (UTCTime >= TxUTCTime)):
        TriggerTx = True
    elif ((UTCTimeMicroseconds > 800000) and TriggerTx):
        TriggerTx = False

    # Wait for 20ms
    sleep(0.02)
    
    try:  # used try so that if user pressed other than the given key error will not be shown
        if keyboard.is_pressed('q'):  # if key 'q' is pressed 
            break  # finishing the loop
    except:
        print ("Press q to quit")
                
RunTxFunction = False
    
# Close the tranmission channel (Serial/Audio)
if SerialOrAudio == "Serial":
    # Close the serial port
    ser.close()
else:
    # Wait for 1 second and then close the audio stream
    sleep(1)
    AudioStream.stop_stream()
    AudioStream.close()
    PAudio.terminate()
