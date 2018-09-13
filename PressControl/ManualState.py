import press_globals as pg
import Adafruit_CharLCD as LCD
import time

class ManualState:
    def __init__(self):
        self.start_time = time.time()
        pass
    def enter(self, allSensorValues, lcd, led_gpio):
        self.start_time = time.time()
        print "Entering Manual State"
        lcd.set_color(1.0, 0.0, 0.0)
        return self
    def exit(self, allSensorValues, lcd, led_gpio):
        print "Exiting Manual State"
        return True
    def in_state(self, allSensorValues, lcd, led_gpio):
        print "In Manual State"
        try:
            lcd.clear()
            lcd.message("In Manual State\n" + "Top Temp: " + '{0:.1f}'.format(allSensorValues[0]) +
                        "\nBot Temp: " + '{0:.1f}'.format(allSensorValues[1]) +
                        "\nPressure:" +  '{0:.1f}'.format(allSensorValues[2][3]/10.)
                        )
        except Exception as e:
            print(e)


