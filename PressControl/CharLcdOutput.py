import Adafruit_CharLCD as LCD
import Adafruit_GPIO.MCP230xx as MCP

import Utilities


class CharLcdOutput:
    @staticmethod
    def setup_char_lcd():
        # setting up I2C for character LCD
        lcd_rs = 0
        lcd_en = 1
        lcd_d4 = 2
        lcd_d5 = 3
        lcd_d6 = 4
        lcd_d7 = 5
        lcd_red = 6
        lcd_green = 7
        lcd_blue = 8

        lcd_columns = 20
        lcd_rows = 4

        try:
            gpio = MCP.MCP23017(0x22, busnum=1)

            return LCD.Adafruit_RGBCharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7,
                                               lcd_columns, lcd_rows, lcd_red, lcd_green, lcd_blue,
                                               gpio=gpio)
        except:
            print 'Using Fake LCD'
            return Utilities.FakeLCD()