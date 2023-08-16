/*
 * board.h
 *
 *  Created on: 2020年3月17日
 *      Author: 86157
 */

#ifndef INC_BOARD_H_
#define INC_BOARD_H_
#include "usb_device.h"
//#include "SX127x.h"
#include "usbd_cdc_if.h"

// RTC_HandleTypeDef hrtc;

// SPI_HandleTypeDef hspi1;

// TIM_HandleTypeDef htim4;

 extern USBD_HandleTypeDef hUsbDeviceFS;
extern  uint16_t begin_flag ;
extern  uint16_t num        ;
 void SystemClock_Config(void);
 void MX_GPIO_Init(void);
 void MX_RTC_Init(void);
 void MX_SPI1_Init(void);
 void MX_TIM4_Init(void);
 void Board_Init(void);

#endif /* INC_BOARD_H_ */
