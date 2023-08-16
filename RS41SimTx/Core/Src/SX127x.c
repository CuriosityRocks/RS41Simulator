#include "stm32l1xx_hal.h"
#include "stm32l1xx_hal_spi.h"
#include "SX127x.h"

extern SPI_HandleTypeDef hspi1;

uint16_t RX_LoRa_Flag = 0;

unsigned int	BitRateFrac = 0;

unsigned char   power_data[16]={0X80,0X81,0X82,0X83,0X84,0X85,0X86,0X87,0X88,0x89,0x8a,0x8b,0x8c,0x8d,0x8e,0x8f};

unsigned char   RF_FS_IRQFLAGS2_STATUS;

void gByteWritefunc(unsigned char buffer)
{
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_4, GPIO_PIN_RESET);//set NSS(PA_4) to low
    HAL_SPI_Transmit(&hspi1, &buffer, 1, 10);
}

unsigned char gByteReadfunc(void)
{
    unsigned char temp=0;
    
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_4, GPIO_PIN_RESET);//set NSS(PA_4) to low
    HAL_SPI_Receive(&hspi1, &temp, 1,10);
	
	return temp;
}

void SX127xWriteBuffer( unsigned char addr, unsigned char buffer)
{
	HAL_GPIO_WritePin(GPIOA, GPIO_PIN_4, GPIO_PIN_RESET);//set NSS(PA_4) to low
	gByteWritefunc(addr|0x80);
	gByteWritefunc(buffer);
	HAL_GPIO_WritePin(GPIOA, GPIO_PIN_4, GPIO_PIN_SET);//set NSS(PA_4) to high
}

unsigned char SX127xReadBuffer(unsigned char addr)
{
	unsigned char Value;
	
	HAL_GPIO_WritePin(GPIOA, GPIO_PIN_4, GPIO_PIN_RESET);//set NSS(PA_4) to low
	gByteWritefunc(addr & 0x7f);
	Value = gByteReadfunc();
	HAL_GPIO_WritePin(GPIOA, GPIO_PIN_4, GPIO_PIN_SET);//set NSS(PA_4) to high
	
	return Value; 
}

void SX127xReset(void)
{
	HAL_GPIO_WritePin(GPIOA, GPIO_PIN_3, GPIO_PIN_RESET);//set LoRa RESET(PA_1) to low
	HAL_Delay(200);
	HAL_GPIO_WritePin(GPIOA, GPIO_PIN_3, GPIO_PIN_SET);
	HAL_Delay(500);
}

void SX127xFSKSetOpMode( RFMode_SET opMode )
{
	unsigned char opModePrev;
	opModePrev=SX127xReadBuffer(REG_FS_OPMODE);
	opModePrev &=0xf8;
	opModePrev |= (unsigned char)opMode;
	SX127xWriteBuffer( REG_FS_OPMODE, opModePrev);
}

int SX127xFSKGetOpMode()
{
	return(SX127xReadBuffer(REG_FS_OPMODE) & 0x03);
}

void SX127xFSKLoRa( Debugging_fsk_ook opMode )
{
	unsigned char opModePrev;
	opModePrev=SX127xReadBuffer(REG_FS_OPMODE);
	opModePrev &=0x7F;
	opModePrev |= (unsigned char)opMode;
	SX127xWriteBuffer( REG_FS_OPMODE, opModePrev);
}

void SX127xFSKSetRFFrequency(unsigned int TxFrequency)
{
	int n=TxFrequency/61.035;
	unsigned char Frequency[3];
	Frequency[0]=n>>16;
	Frequency[1]=n>>8;
	Frequency[2]=n>>0;
	SX127xWriteBuffer( REG_FS_FRFMSB, Frequency[0]);
	SX127xWriteBuffer( REG_FS_FRFMID, Frequency[1]);
	SX127xWriteBuffer( REG_FS_FRFLSB, Frequency[2]);
}

void SX127xFSKSetBitRate(unsigned int BitRate, unsigned char BitRateFrac)
{
	int n=FXOSC/BitRate - BitRateFrac/16;
	unsigned char BitRateBytes[2];
	BitRateBytes[0]=n>>8;
	BitRateBytes[1]=n>>0;
	SX127xWriteBuffer( REG_FS_BRMSB, BitRateBytes[0]);
	SX127xWriteBuffer( REG_FS_BRLSB, BitRateBytes[1]);
	SX127xWriteBuffer( REG_FS_BITRATEFRAC, BitRateFrac & 0x0F);
}

void SX127xFSKSetFreqDev(unsigned int FreqDev)
{
	int n=FreqDev/FSTEP;
	unsigned char FreqDevBytes[2];
	FreqDevBytes[0]=n>>8;
	FreqDevBytes[1]=n>>0;
	SX127xWriteBuffer( REG_FS_FDEVMSB, FreqDevBytes[0] & 0x1F);
	SX127xWriteBuffer( REG_FS_FDEVLSB, FreqDevBytes[1]);
}

void SX127xFSKSetRFPower(signed char power )
{
	// Power levels available: -3dBm to +16dBm, +20dBm

	SX127xWriteBuffer( REG_FS_OCP, 0x3f);    // Enables overload current protection (OCP) for PA:
										     // 0x3F = OCP enabled + threshold set to the highest possible current.

	if (power > 11)
	{
		//Set Pmax to +20dBm for PA_HP, Must turn off PA_LF or PA_HF, and set RegOcp
		SX127xWriteBuffer( REG_FS_PADAC, 0x87);  // Enables the +20dBm option on PA_BOOST pin:
												 // 0x84 = Default value
												 // 0x87 = +20dBm on PA_BOOST when OutputPower=1111
		unsigned char PACONFIG = (unsigned char)power;
		if (PACONFIG > 17)
		{
			PACONFIG = 17;
		}
		PACONFIG = (PACONFIG - 0x02) | 0x80;
		SX127xWriteBuffer( REG_FS_PACONFIG, PACONFIG ); //
	}
	else
	{
		//Set PA_LF, Must turn off PA_HF
		SX127xWriteBuffer( REG_FS_PADAC, 0x84);  // Enables the +20dBm option on PA_BOOST pin:
												 // 0x84 = Default value
												 // 0x87 = +20dBm on PA_BOOST when OutputPower=1111
		signed char LocalPower = power;
		if (LocalPower < -3)
		{
			LocalPower = 0;
		}
		else
		{
			LocalPower = LocalPower + 3;
		}
		unsigned char PACONFIG = (unsigned char)LocalPower;
		PACONFIG = PACONFIG | 0x20;
		SX127xWriteBuffer( REG_FS_PACONFIG, PACONFIG ); //
	}
}

void SX127xFSKSetGaussianMode(unsigned char GaussianMode )
{
	unsigned char RECVER_DAT;
	RECVER_DAT= SX127xReadBuffer( REG_FS_PARAMP);
	RECVER_DAT = ( RECVER_DAT & ~RFFS_PARAMP_DATA_SHAPING_MASK );
	RECVER_DAT = ( RECVER_DAT | ( ( GaussianMode & 0X03) << 5 ) );
	SX127xWriteBuffer( REG_FS_PARAMP, RECVER_DAT );
}

void SX127xFSKSetFIFOThreshold(unsigned char FIFOThreshold )
{
	unsigned char RECVER_DAT;
	RECVER_DAT= SX127xReadBuffer( REG_FS_FIFOTHRESH);
	RECVER_DAT = ( RECVER_DAT & ~RFFS_FIFO_THRESHOLD_MASK );
	RECVER_DAT = ( RECVER_DAT | ( FIFOThreshold & RFFS_FIFO_THRESHOLD_MASK ));
	SX127xWriteBuffer( REG_FS_FIFOTHRESH, RECVER_DAT );
}

void SX127xFSKSetPacketFormat(BOOL_t enable )
{
	unsigned char RECVER_DAT;
	RECVER_DAT= SX127xReadBuffer( REG_FS_PACKETCONFIG1);
	RECVER_DAT = ( RECVER_DAT & ~RFFS_PACKETCONFIG1_PACKET_FORMAT_MASK );
	if (enable) RECVER_DAT = ( RECVER_DAT | RFFS_PACKETCONFIG1_PACKET_FORMAT_MASK );
	SX127xWriteBuffer( REG_FS_PACKETCONFIG1, RECVER_DAT );
}

void SX127xFSKSetSyncOn(BOOL_t enable )
{
	unsigned char RECVER_DAT;
	RECVER_DAT= SX127xReadBuffer( REG_FS_SYNCCONFIG);
	RECVER_DAT = ( RECVER_DAT & ~RFFS_SYNCCONFIG_SYNC_ON_MASK );
	if (enable) RECVER_DAT = ( RECVER_DAT | RFFS_SYNCCONFIG_SYNC_ON_MASK );
	SX127xWriteBuffer( REG_FS_SYNCCONFIG, RECVER_DAT );
}

void SX127xFSKSetCrcOn(BOOL_t enable )
{
	unsigned char RECVER_DAT;
	RECVER_DAT= SX127xReadBuffer( REG_FS_PACKETCONFIG1);
	RECVER_DAT = ( RECVER_DAT & ~RFFS_PACKETCONFIG1_CRC_ON_MASK );
	if (enable) RECVER_DAT = ( RECVER_DAT | RFFS_PACKETCONFIG1_CRC_ON_MASK );
	SX127xWriteBuffer( REG_FS_PACKETCONFIG1, RECVER_DAT );
}

void SX127xFSKSetPreambleSize(unsigned int PreambleSize)
{
	unsigned char PreambleSizeBytes[2];
	PreambleSizeBytes[0]=PreambleSize>>8;
	PreambleSizeBytes[1]=PreambleSize>>0;
	SX127xWriteBuffer( REG_FS_PREAMBLEMSB, PreambleSizeBytes[0]);
	SX127xWriteBuffer( REG_FS_PREAMBLELSB, PreambleSizeBytes[1]);
}

void SX127xFSK_INT(MetaDataStruct SetupData)
{
	SX127xFSKSetOpMode(Sleep_mode);
	SX127xFSKLoRa(FSK_mode);
	SX127xFSKSetOpMode(Stdby_mode);

	SX127xWriteBuffer( REG_FS_DIOMAPPING1,GPIO_VARE_1);
	SX127xWriteBuffer( REG_FS_DIOMAPPING2,GPIO_VARE_2);
	SX127xFSKSetRFFrequency(SetupData. FrequencyStart);
	SX127xFSKSetBitRate(SetupData.DataRate, BitRateFrac);
	SX127xFSKSetFreqDev(SetupData.FrequencyDeviation);
	SX127xFSKSetGaussianMode(SetupData.GaussianMode);
	SX127xFSKSetRFPower(SetupData.Power);
	SX127xFSKSetSyncOn(false); // false = No Sync
	SX127xFSKSetPacketFormat(false); // false = Fixed size
	SX127xFSKSetCrcOn(false); // false = CRC off
	SX127xFSKSetPreambleSize(0); // 0 = No preamble
	SX127xFSKSetFIFOThreshold(FIFO_THRESHOLD);
}

void SX127xFSKSetPayloadLength(unsigned int PayloadLength )
{
	// Set mode to Stdby
	SX127xFSKSetOpMode( Stdby_mode );

	// Set payload length
	unsigned char PayloadLengthBytes[2];
	PayloadLengthBytes[0]=PayloadLength>>8 & RFFS_PACKETCONFIG2_PAYLOAD_LENGTH_MASK;
	PayloadLengthBytes[1]=PayloadLength>>0;
	unsigned char RECVER_DAT;
	RECVER_DAT= SX127xReadBuffer( REG_FS_PACKETCONFIG2);
	RECVER_DAT = ( RECVER_DAT & ~RFFS_PACKETCONFIG2_PAYLOAD_LENGTH_MASK ) | PayloadLengthBytes[0];
	SX127xWriteBuffer( REG_FS_PACKETCONFIG2, RECVER_DAT );
	SX127xWriteBuffer( REG_FS_PALOADLENGTHLSB, PayloadLengthBytes[1]);
}

void FUN_RF_SENDPACKET(unsigned char *RF_TRAN_P,unsigned char LEN)
{
	unsigned char ASM_i;
	HAL_GPIO_WritePin(GPIOA, GPIO_PIN_4, GPIO_PIN_RESET);
	gByteWritefunc( 0x80 );
	for( ASM_i = 0; ASM_i < LEN; ASM_i++ )
	{
		gByteWritefunc( *RF_TRAN_P );RF_TRAN_P++;
	}
	HAL_GPIO_WritePin(GPIOA, GPIO_PIN_4, GPIO_PIN_SET);
	SX127xWriteBuffer(REG_FS_DIOMAPPING1,0x40);
	SX127xWriteBuffer(REG_FS_DIOMAPPING2,0x00);

	SX127xFSKSetOpMode( Transmitter_mode );
}
