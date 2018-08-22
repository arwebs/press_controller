import press_globals as pg
import Adafruit_CharLCD as LCD

class ManualState:
    def __init__(self):
        pass
    def enter(self):
        print "Entering Manual State"
        return self
    def exit(self):
        print "Exiting Manual State"
        return True
    def in_state(self, allSensorValues, lcd, led_gpio):
        print "In Manual State"
        try:
            lcd.clear()
            lcd.set_color(1.0,0.0,0.0)
            lcd.message("In Manual State\n" + "T1: " + str(allSensorValues[0]) + " T2: " + str(allSensorValues[1]))
        except Exception as e:
            print(e)


