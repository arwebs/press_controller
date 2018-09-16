import press_globals as pg
import Adafruit_CharLCD as LCD
import time

class ManualState:
    def __init__(self):
        self.start_time = time.time()
        pass
    def enter(self, allSensorValues, lcd, led_gpio):
        self.start_time = time.time()
        with open('/home/pi/press_data/manual-run-data-' + str(self.start_time) + '.txt', 'a') as the_file:
            the_file.write('\nManual Run started..\nPressure,Top Temperature,Bottom Temperature,Top Blanket On,Bottom Blanket On')

        print "Entering Manual State"
        lcd.set_color(1.0, 0.0, 0.0)
        return self
    def exit(self, allSensorValues, lcd, led_gpio):
        print "Exiting Manual State"
        with open('/home/pi/press_data/manual-run-data-' + str(self.start_time) + '.txt', 'a') as the_file:
            the_file.write('\n-----Manual Run ended-----')
        return True
    def in_state(self, allSensorValues, lcd, led_gpio):
        print "In Manual State"
        try:
            lcd.clear()
            lcd.message("In Manual State\n" + "Top Temp: " + '{0:.1f}'.format(allSensorValues[0]) +
                        "\nBot Temp: " + '{0:.1f}'.format(allSensorValues[1]) +
                        "\nPressure:" +  '{0:.1f}'.format(allSensorValues[2][3]/10.)
                        )
            with open('/home/pi/press_data/manual-run-data-' + str(self.start_time) + '.txt', 'a') as the_file:
                the_file.write(
                    '\nTime,Pressure,Top Temperature,Bottom Temperature,Top Blanket On,Bottom Blanket On' +
                    str(time.time()) + ',' + str(allSensorValues[2][3]/10.) + ',' + str(allSensorValues[0])+
                    ','+ str(allSensorValues[1]) + ',' + str(pg.top_heat_blanket_on) + ',' + str(pg.bottom_heat_blanket_on))
        except Exception as e:
            print(e)


