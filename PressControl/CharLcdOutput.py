import Adafruit_CharLCD as LCD
import Adafruit_GPIO.MCP230xx as MCP
import RPi.GPIO as GPIO

import Utilities


class CharLcdOutput:
    @staticmethod
    def setup_char_lcd():
        # setting up I2C for character LCD
        lcd_rs = 8
        lcd_en = 10
        lcd_d4 = 4
        lcd_d5 = 5
        lcd_d6 = 6
        lcd_d7 = 7
        lcd_red = 13
        lcd_green = 14
        lcd_blue = 15

        lcd_columns = 20
        lcd_rows = 4

        try:
            gpio = MCP.MCP23017(0x22, busnum=1)

            # must set enable bit to low value
            gpio.setup(9, GPIO.OUT)
            gpio.output(9,GPIO.LOW)

            return LCD.Adafruit_RGBCharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7,
                                               lcd_columns, lcd_rows, lcd_red, lcd_green, lcd_blue,
                                               gpio=gpio)
        except Exception as e:
            print 'Using Fake LCD'
            print(e)
            return Utilities.FakeLCD()