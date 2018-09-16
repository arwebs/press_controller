import press_globals as pg
import numpy as np
import time
import math
import Utilities

from datetime import timedelta
from enum import Enum

class AutoStates(Enum):
    Entering = 1
    Pressurizing = 2
    Running = 3
    Finished = 4
    Error = 5
    Aborted = 6





class AutomaticStateActions:
    def __init__(self):
        self.top_blanket_temperatures = []
        self.bottom_blanket_temperatures = []
        self.top_duty_cycle = 0.5
        self.bottom_duty_cycle = 0.5
        self.buffer_length = 10
        self.start_time = time.time()
        self.top_start_temperature = 0.
        self.bottom_start_temperature = 0.
        self.counter = 0
        self.reset_in = 0

    def perform_action(self, auto_state, allSensorValues, lcd, led_gpio):
        if auto_state == AutoStates.Entering:
            auto_state = self.prepare_for_run(allSensorValues, lcd, led_gpio)
        elif auto_state == AutoStates.Pressurizing:
            auto_state = self.pressurize(allSensorValues, lcd, led_gpio)
        elif auto_state == AutoStates.Running:
            auto_state = self.do_run(allSensorValues, lcd, led_gpio)
        elif auto_state == AutoStates.Finished:
            auto_state = self.finish(allSensorValues, lcd, led_gpio)
        elif auto_state == AutoStates.Error:
            auto_state = self.error(allSensorValues, lcd, led_gpio)
        elif auto_state == AutoStates.Aborted:
            auto_state = self.abort(allSensorValues, lcd, led_gpio)

        return auto_state

    def reset_pins(self, led_gpio):
        pins_to_reset = [pg.TOP_HOT_PIN, pg.TOP_COLD_PIN, pg.TOP_GOOD_PIN, pg.BOTTOM_HOT_PIN, pg.BOTTOM_COLD_PIN, pg.BOTTOM_GOOD_PIN, pg.RUN_IN_PROGRESS_PIN]
        for pin in pins_to_reset:
            led_gpio.output(pin, True)  # True is HIGH is OFF, False is LOW is ON


    def prepare_for_run(self, allSensorValues, lcd, led_gpio):
        lcd.clear()
        lcd.message("Press Green button\nto start run")
        self.reset_pins(led_gpio)
        # set run parameters
        lcd.set_color(0.0, 0.0, 0.0)
        if pg.start_button:
            return AutoStates.Pressurizing
        return AutoStates.Entering

    def pressurize(self, allSensorValues, lcd, led_gpio):
        lcd.clear()
        lcd.message("Pressurizing..." + str(allSensorValues[2][1]))
        lcd.set_color(0.0, 0.0, 1.0)
        led_gpio.output(pg.RUN_IN_PROGRESS_PIN, False)
        ## before allowing a transition to running state, set start time

        pg.intake_solenoid_on = not pg.intake_solenoid_off


        self.start_time = time.time()
        self.top_start_temperature = allSensorValues[0]
        self.bottom_start_temperature = allSensorValues[1]

        #verify which sensor value...and calibrate
        if allSensorValues[2][1] > 700:
            return AutoStates.Running
        return AutoStates.Pressurizing

        return AutoStates.Running

    def do_run(self, allSensorValues, lcd, led_gpio):
        lcd.clear()
        lcd.set_color(1.0, 0.0, 1.0)
        if pg.stop_button:
            return AutoStates.Error

        #unless being overridden, keep the intake solenoid on for the duration of the run
        pg.intake_solenoid_on = not pg.intake_solenoid_off

        #fill buffer of temperatures
        if math.isnan(allSensorValues[0]) or math.isnan(allSensorValues[1]):
            self.reset_in = 10
        else:
            self.top_blanket_temperatures.append(allSensorValues[0])
            self.bottom_blanket_temperatures.append(allSensorValues[1])
        self.reset_in = self.reset_in - 1
        led_gpio.output(pg.ERROR_PIN, self.reset_in <= 0)
        #if the buffer is full, calculate duty cycle
        if len(self.top_blanket_temperatures) >= self.buffer_length:
            self.top_duty_cycle = self.top_duty_cycle +\
                                  self.determine_blanket_desired_duty_cycle(pg.top_rampup_time, self.top_blanket_temperatures, self.top_start_temperature, pg.top_max_temp)
            self.bottom_duty_cycle = self.bottom_duty_cycle +\
                                     self.determine_blanket_desired_duty_cycle(pg.bottom_rampup_time, self.bottom_blanket_temperatures, self.bottom_start_temperature, pg.bottom_max_temp)

            # constrain duty cycles to 0-100%
            self.top_duty_cycle = max(0., min(1., self.top_duty_cycle))
            self.bottom_duty_cycle = max(0., min(1., self.bottom_duty_cycle))

            #clear out buffers
            self.top_blanket_temperatures = []
            self.bottom_blanket_temperatures = []

        # if we're too hot, take immediate action
        top_target_temp = self.determine_target_temperature(pg.top_rampup_time, self.top_start_temperature, pg.top_max_temp)
        bottom_target_temp = self.determine_target_temperature(pg.bottom_rampup_time, self.bottom_start_temperature, pg.bottom_max_temp)

        if allSensorValues[0] > top_target_temp + 0.75:
            self.top_duty_cycle = 0

        if allSensorValues[1] > bottom_target_temp + 0.75:
            self.bottom_duty_cycle = 0

        self.set_temp_indicator_leds(allSensorValues, top_target_temp, bottom_target_temp, led_gpio)

        # set blanket on/off status based on duty cycle + overrides
        self.counter = (self.counter + 1) % self.buffer_length

        pg.top_heat_blanket_on = not pg.top_heat_blanket_off and (((self.top_duty_cycle * self.buffer_length) > self.counter) or pg.top_heat_blanket_on)
        pg.bottom_heat_blanket_on = not pg.bottom_heat_blanket_off and (((self.bottom_duty_cycle * self.buffer_length) > self.counter) or pg.bottom_heat_blanket_on)

        lcd.message("Time:" + str(timedelta(seconds=int(time.time() - self.start_time))) + " P:" + str(allSensorValues[2][1]) +
            "\nTopA:" + '{0:.1f}'.format(allSensorValues[0]) + " TopT:" + '{0:.1f}'.format(top_target_temp) +
            "\nBotA:" + '{0:.1f}'.format(allSensorValues[1]) + " BotT:" + '{0:.1f}'.format(bottom_target_temp) +
            "\nTopDC:" + str(self.top_duty_cycle) + " BotDC:" + str(self.bottom_duty_cycle))

        elapsed_time = time.time() - self.start_time
        if elapsed_time > pg.total_run_duration:
            pg.top_heat_blanket_on = False
            pg.bottom_heat_blanket_on = False
            return AutoStates.Finished

        return AutoStates.Running

    def finish(self, allSensorValues, lcd, led_gpio):
        if pg.start_button:
            return AutoStates.Entering
        lcd.clear()
        lcd.set_color(1.0, 1.0, 0.0)
        lcd.message("Run finished.\nPress green button\nto reset.")
        self.reset_pins(led_gpio)
        if allSensorValues[2][1] > 700:
            pg.exhaust_solenoid_on = not pg.exhaust_solenoid_off
        return AutoStates.Finished

    def error(self, allSensorValues, lcd, led_gpio):
        pg.intake_solenoid_on = False
        pg.exhaust_solenoid_on = True
        pg.top_heat_blanket_on = False
        pg.bottom_heat_blanket_on = False
        led_gpio.output(pg.ERROR_PIN, False)
        lcd.clear()
        lcd.set_color(0.0, 1.0, 1.0)
        lcd.message("operation cancelled.\nTop Temp: " + '{0:.1f}'.format(allSensorValues[0]) +
                        "\nBot Temp: " + '{0:.1f}'.format(allSensorValues[1]) +
                        "\nPressure:" +  '{0:.1f}'.format(allSensorValues[2][3]/10.))
        # turn on error light
        # turn off relays except if over-pressurized, then let off extra pressure
        # await start button for reset
        self.reset_pins(led_gpio)
        if pg.start_button:
            led_gpio.output(pg.ERROR_PIN, True)
            return AutoStates.Entering
        return AutoStates.Error

    def abort(self, allSensorValues, lcd, led_gpio):
        pg.intake_solenoid_on = False
        pg.exhaust_solenoid_on = True
        pg.top_heat_blanket_on = False
        pg.bottom_heat_blanket_on = False
        self.reset_pins(led_gpio)
        # close run data
        # confirm if system is pressurized
            # otherwise await depressurization
        return allSensorValues[2][1] < 100 # real pressure pin is [2][3]

    ## "private" methods...
    def determine_target_temperature(self, rampup_time, start_temperature, max_temperature):
        elapsed_time = int(time.time() - self.start_time)
        print "Elapsed Time: " + str(elapsed_time) + " Ramp-up time: " + str(rampup_time) + " Max temp: " + str(max_temperature)
        # if rampup time is finished, just return max temperature so we hold there
        if elapsed_time > rampup_time:
            return max_temperature

        # in the rampup period, find the equation of the line and plug in elapsed time to find target
        slope = (max_temperature - start_temperature) / rampup_time
        return slope * elapsed_time + start_temperature

    def determine_blanket_desired_duty_cycle(self, rampup_time, last_n_temperatures, start_temperature, max_temperature):
        elapsed_time = int(time.time() - self.start_time)

        previous_time = int(elapsed_time) - len(last_n_temperatures)
        time_array = np.array([range(previous_time, int(elapsed_time)), np.ones(len(last_n_temperatures))])
        fit_slope, fit_intercept = np.linalg.lstsq(time_array.T, last_n_temperatures)[0]

        future_time = int(elapsed_time) + 15

        if elapsed_time > rampup_time:
            yError = max_temperature - (fit_slope * future_time + fit_intercept)
        else:
            slope = (max_temperature - start_temperature) / rampup_time
            yError = (slope * future_time + start_temperature) - (fit_slope * future_time + fit_intercept)
        # hold|increase|decrease

        if yError > 0.25:
            return 0.1
        elif yError < -0.25:
            return -0.1
        else:
            return 0.

    def set_temp_indicator_leds(self, allSensorValues, top_target_temp, bottom_target_temp, led_gpio):
        # must set pin #s
        if not math.isnan(allSensorValues[0]):
            led_gpio.output(pg.TOP_HOT_PIN, not allSensorValues[0] > top_target_temp)
            led_gpio.output(pg.TOP_COLD_PIN, not allSensorValues[0] < top_target_temp)
            led_gpio.output(pg.TOP_GOOD_PIN, not int(allSensorValues[0]) == int(top_target_temp))

        if not math.isnan(allSensorValues[1]):
            led_gpio.output(pg.BOTTOM_HOT_PIN, not allSensorValues[1] > bottom_target_temp)
            led_gpio.output(pg.BOTTOM_COLD_PIN, not allSensorValues[1] < bottom_target_temp)
            led_gpio.output(pg.BOTTOM_GOOD_PIN, not int(allSensorValues[1]) == int(bottom_target_temp))


class AutomaticState:
    def __init__(self):
        self.auto_state = AutoStates.Entering
        self.state_actions = AutomaticStateActions()

    def enter(self, allSensorValues, lcd, led_gpio):
        print "Entering Automatic State"
        self.auto_state = AutoStates.Entering
        self.state_actions = AutomaticStateActions()
        lcd.set_color(1.0, 0.0, 1.0)
        return self

    def exit(self, allSensorValues, lcd, led_gpio):
        print "Exiting Automatic State"
        return self.state_actions.abort(allSensorValues, lcd, led_gpio)

    def in_state(self, allSensorValues, lcd, led_gpio):
        self.auto_state = self.state_actions.perform_action(self.auto_state, allSensorValues, lcd, led_gpio)
        print "In Automatic State"
