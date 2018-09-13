import press_globals as pg

def set_value_from_pot(pot_value, min_value, max_value):
    return min_value + (pot_value * (max_value-min_value))/1024.0


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
            pg.top_rampup_time = set_value_from_pot(allSensorValues[2][1], 20., 100.)
            pg.bottom_rampup_time = set_value_from_pot(allSensorValues[2][2], 20., 100.)
            pg.total_run_duration = max(max(pg.top_rampup_time, pg.bottom_rampup_time), set_value_from_pot(allSensorValues[2][0], 20., 120.))
            lcd.message("Timing Config:\nTop Ramp-up: " +
                        '{0:.1f}'.format(pg.top_rampup_time) +
                        "\nBottom Ramp-up: " +
                        '{0:.1f}'.format(pg.bottom_rampup_time) +
                        "\nTotal Duration: " +
                        '{0:.1f}'.format(pg.total_run_duration)
                        )
            pg.top_rampup_time = pg.top_rampup_time * 60
            pg.bottom_rampup_time = pg.bottom_rampup_time * 60
            pg.total_run_duration = pg.total_run_duration * 60

        elif self.config_step == 1:
            pg.target_pressure = set_value_from_pot(allSensorValues[2][0], 20., 100.)
            pg.top_max_temp = set_value_from_pot(allSensorValues[2][1], 50., 100.)
            pg.bottom_max_temp = set_value_from_pot(allSensorValues[2][2], 50., 100.)
            lcd.message("Temp/Press Config:\nTop max temp: " +
                        '{0:.1f}'.format(pg.top_max_temp)  +
                        "\nBot max temp: " +
                        '{0:.1f}'.format(pg.bottom_max_temp) +
                        "\nTarget pressure: " +
                        '{0:.1f}'.format(pg.target_pressure)
                        )

        pg.top_heat_blanket_on = False
        pg.bottom_heat_blanket_on = False
        pg.intake_solenoid_on = False
        pg.exhaust_solenoid_on = False
