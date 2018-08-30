import press_globals as pg

def set_value_from_pot(pot_value, min_value, max_value):
    return (pot_value * (max_value-min_value))/1024.0


class ConfigState:

    def __init__(self):
        self.config_step = 0
        pass

    def enter(self):
        print "Entering Setup State"
        self.config_step = 0
        return self

    def exit(self):
        print "Exiting Setup State"
        return True

    def in_state(self, allSensorValues, lcd, led_gpio):

        if pg.start_button:
            self.config_step = (self.config_step + 1) % 2
        lcd.clear()
        if self.config_step == 0:
            pg.top_rampup_time = set_value_from_pot(allSensorValues[2][2], 20., 100.)
            pg.bottom_rampup_time = set_value_from_pot(allSensorValues[2][3], 20., 100.)
            pg.total_run_duration = set_value_from_pot(allSensorValues[2][1], max(pg.top_rampup_time, pg.bottom_rampup_time), 120.)
            lcd.message("Timing Config:\nTop Ramp-up: " +
                        str(pg.top_rampup_time) +
                        "\nTotal Duration: " +
                        str(pg.total_run_duration) +
                        "\nBottom Ramp-up: " +
                        str(pg.bottom_rampup_time)
                        )
        elif self.config_step == 1:
            pg.target_pressure = set_value_from_pot(allSensorValues[2][1], 20., 100.)
            pg.top_max_temp = set_value_from_pot(allSensorValues[2][2], 50., 100.)
            pg.bottom_max_temp = set_value_from_pot(allSensorValues[2][3], 50., 100.)
            lcd.message("Temp/Press Config:\nTop max temp: " +
                        str(pg.top_max_temp) +
                        "\nMax pressure: " +
                        str(pg.target_pressure) +
                        "\nBottom max temp: " +
                        str(pg.bottom_max_temp)
                        )

        pg.top_heat_blanket_on = False
        pg.bottom_heat_blanket_on = False
        pg.intake_solenoid_on = False
        pg.exhaust_solenoid_on = False
