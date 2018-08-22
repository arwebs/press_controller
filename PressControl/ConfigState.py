import press_globals as pg

class ConfigState:

    def __init__(self):
        pass

    def enter(self):
        print "Entering Setup State"
        return self

    def exit(self):
        print "Exiting Setup State"
        return True

    def in_state(self, allSensorValues, lcd, led_gpio):

        pg.top_heat_blanket_on = False
        pg.bottom_heat_blanket_on = False
        pg.intake_solenoid_on = False
        pg.exhaust_solenoid_on = False
