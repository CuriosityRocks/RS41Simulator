/*
The following code was written for the HELTEC AUTOMATION LoRa Node 151 development kit.
It was developed from HELTEC AUTOMATION's Pingpong_CDC.zip example code.
The code was developed to enable the transmission of RS41 frames with the RS41 simulation framework, developed by Paz Hameiri.
The code is doing the following tasks:
1. Initialize the board.
2. Wait for the reception of a complete message from the USB port, comprising transmission parameters and a complete RS41 basic frame.
3. Setup for transmission, according to the transmission parameters (if required)
4. Transmit the RS41 frame.
5. Return to step 2.
The header of the message comprises the following parameters:
    uint16_t NumOfBytes:         A parameter that contains the number of bytes to be received from the PC
    uint32_t FrequencyStart:     A parameter that contains the transmission frequency in Hz
    uint32_t DataRate:           A parameter that contains the transmission data rate in BAUD
    uint32_t FrequencyDeviation: A parameter that contains the transmission frequency deviation in Hz
    uint8_t  GaussianMode:       A parameter that contains the transmission gaussian shaping mode:
                                 0 = no shaping,
                                 1 = Gaussian filter BT = 1.0,
                                 2 = Gaussian filter BT = 0.5,
                                 3 = Gaussian filter BT = 0.3
    int8_t   Power:              A parameter that contains the transmission output power in dBm. Supports -3dBm to +16dBm, +20dBm
The header is followed by a complete RS41 basic frame.
*/

#include "main.h"
#include "board.h"
#include "SX127x.h"
#include "usbd_cdc_if.h"

// USB buffer parameters
uint8_t  USBBuffer[1024];
uint16_t USBBufferPointer = 0;

// Transmission buffer
uint8_t  TxBuffer[1024];
unsigned int TxDataSize = 0;
unsigned int TxBufferPointer = 0;

// PcReceptionStruct size in bytes
uint8_t PcReceptionStructSize = 16; // [Bytes]

// Define structs to hold the metadata
MetaDataStruct SetupData;
MetaDataStruct PcReceptionData;

uint16_t 		begin_flag   = 0;
uint16_t 		num          = 0;

int main(void)
{
	unsigned char Irq_flag_RX = 0;

	Board_Init();
	//usb_printf("Board setup\r\n");
	HAL_Delay(10);


	SetupData.NumOfBytes = 0;             // Holds the number of bytes in the packet received from the PC
	SetupData.FrequencyStart = 404000000; // Frequency in Hz
	SetupData.DataRate = 4800;            // Data rate in BAUD
	SetupData.FrequencyDeviation = 2400;  // Frequency deviation in Hz
	SetupData.GaussianMode = 2;           // 0 = no shaping, 			    1 = Gaussian filter BT = 1.0,
	  	  	  	  	  	  	  	          // 2 = Gaussian filter BT = 0.5,  3 = Gaussian filter BT = 0.3
	SetupData.Power = 19;                 // Output power in dBm:  Supports -3dBm to +16dBm, +20dBm

	SX127xReset();
	SX127xFSK_INT(SetupData);
	//usb_printf("Transceiver setup\r\n");

	uint32_t StartTime = 0;
	uint32_t MaximumTicksPerMessage = 1000; // [milliseconds]
	int NumOfBytes = 1023;
	int AckNumber = 0;

	while (1)
	{
		// USB message reception

		// Check if the USBBuffer is filling.
		if (USBBufferPointer > 0)
		{
			// Check if this is the start of the message reception
			if (StartTime == 0)
				{
					// Set the start time
					StartTime = HAL_GetTick();
				}
			// Check if the expected number of byte were received
			else if ((NumOfBytes == 1023) && (USBBufferPointer >= 2))
			{
				NumOfBytes = ((int)USBBuffer[0] << 8) | (int)USBBuffer[1];
			}
			// Check if 64 bytes were sent. If so, send the number of accumulated bytes.
			else if ((USBBufferPointer % 64 == 0) && (AckNumber != USBBufferPointer))
			{
				usb_printf("%d",USBBufferPointer);
				AckNumber = USBBufferPointer;
			}
			else if (USBBufferPointer >= NumOfBytes)
			{
				// Read the transmission data from the buffer
				PcReceptionData.NumOfBytes 		   = ( (uint16_t)USBBuffer[ 0] <<  8 ) |   (uint16_t)USBBuffer[ 1];
				PcReceptionData.FrequencyStart     = ( (uint32_t)USBBuffer[ 2] << 24 ) | ( (uint32_t)USBBuffer[ 3] << 16 ) |
												     ( (uint32_t)USBBuffer[ 4] <<  8 ) |   (uint32_t)USBBuffer[ 5];
				PcReceptionData.DataRate           = ( (uint32_t)USBBuffer[ 6] << 24 ) | ( (uint32_t)USBBuffer[ 7] << 16 ) |
												     ( (uint32_t)USBBuffer[ 8] <<  8 ) |   (uint32_t)USBBuffer[ 9];
				PcReceptionData.FrequencyDeviation = ( (uint32_t)USBBuffer[10] << 24 ) | ( (uint32_t)USBBuffer[11] << 16 ) |
												     ( (uint32_t)USBBuffer[12] <<  8 ) |   (uint32_t)USBBuffer[13];
				PcReceptionData.GaussianMode       =  USBBuffer[14];
				PcReceptionData.Power              =  USBBuffer[15];

				// Copy the data to the Tx buffer
				memcpy(TxBuffer, USBBuffer + PcReceptionStructSize, NumOfBytes);
				TxDataSize = NumOfBytes - PcReceptionStructSize;

				// Send the number of bytes received
				usb_printf("%d",USBBufferPointer);

				// Send a success message and zero the related variables
				usb_printf("Message reception OK");
				NumOfBytes = 1023;
				USBBufferPointer = 0;
				AckNumber = 0;
				StartTime = 0;

				// Check if the metadata requires to update the initialization
				if ( ( SetupData.FrequencyStart     != PcReceptionData.FrequencyStart    ) ||
					 ( SetupData.DataRate           != PcReceptionData.DataRate          ) ||
					 ( SetupData.FrequencyDeviation != PcReceptionData.FrequencyDeviation) ||
					 ( SetupData.GaussianMode       != PcReceptionData.GaussianMode      ) ||
					 ( SetupData.Power              != PcReceptionData.Power             ) )
				{
					SX127xReset();
					SX127xFSK_INT(PcReceptionData);
					SetupData = PcReceptionData;
				}
			}
			// else, if no valid messages were received in the designated timeframe, fail the reception
			else if (HAL_GetTick() - StartTime > MaximumTicksPerMessage)
			{
				// Send a failure message and zero the related variables
				usb_printf("Message reception failed");
				NumOfBytes = 1023;
				USBBufferPointer = 0;
				AckNumber = 0;
				StartTime = 0;
				TxDataSize = 0;
			}
		}

		// Transmission management

		// Check if this is the beginning of the transmission
		if ((TxBufferPointer == 0) && (TxDataSize > 0))
		{
			// Set payload length
			SX127xFSKSetPayloadLength(TxDataSize);
		}

		// Check if there is data to send to the FIFO
		if (TxBufferPointer < TxDataSize)
		{
			// Turn LED On
			HAL_GPIO_WritePin(GPIOB, GPIO_PIN_8, GPIO_PIN_SET);

			// Check if there's more data to be sent than the FIFO can accept
			if ((TxDataSize - TxBufferPointer) > FIFO_DATA_CHUNKS )
			{
				// Send a data chunk to the FIFO
				FUN_RF_SENDPACKET(&(TxBuffer[TxBufferPointer]),FIFO_DATA_CHUNKS);
				TxBufferPointer += FIFO_DATA_CHUNKS;
			}
			else
			{
				// Send the rest of the data to the FIFO
				unsigned int Remaining_Data = TxDataSize - TxBufferPointer;
				unsigned char LEN = Remaining_Data>>0;
				FUN_RF_SENDPACKET(&(TxBuffer[TxBufferPointer]),LEN);
				TxBufferPointer = TxDataSize;
			}
		}

		while(TxDataSize > 0)
		{
			// Read interrupts register numbere 2
			Irq_flag_RX = SX127xReadBuffer( REG_FS_IRQFLAGS2 );

			// Check if the transmission is over
			if((Irq_flag_RX & FS_IRQN_TXD_Value) == FS_IRQN_TXD_Value)
			  {
				// Set the transceiver to stdby mode
				SX127xFSKSetOpMode( Stdby_mode );
				SX127xWriteBuffer( REG_FS_DIOMAPPING1, 0X00 );
				SX127xWriteBuffer( REG_FS_DIOMAPPING2, 0x00 );

				// Turn LED Off
				HAL_GPIO_WritePin(GPIOB, GPIO_PIN_8, GPIO_PIN_RESET);

				// Clear relevant parameters
				TxBufferPointer = 0;
				TxDataSize = 0;

				// Exit the inner while loop
				break;
				}
			// Else, check if the FIFO can be loaded with another data chunk and that there's data to send
			else if (((Irq_flag_RX & FS_IRQN_FIFO_LEVEL_Value) == 0) && (TxBufferPointer < TxDataSize))
			{
				// Exit the inner while loop
				break;
			}
		}
	}
}
