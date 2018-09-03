import press_globals as pg
import numpy as np
import time
import Utilities

from enum import Enum

class AutoStates(Enum):
    Entering = 1
    Pressurizing = 2
    Running = 3
    Finished = 4
    Error = 5
    Aborted = 6

### Top Row (Status LEDs)
POWER_PIN = 1
PRESSURIZED_PIN = 0
RUN_IN_PROGRESS_PIN = 4
ERROR_PIN = 5
AUX_1_PIN = 6
AUX_2_PIN = 7

### Second Row (Power indicator LEDs)
TOP_BLANKET_ON_PIN = 12
BOTTOM_BLANKET_ON_PIN = 9
INTAKE_SOLENOID_ON_PIN = 2
EXHAUST_SOLENOID_ON_PIN = 3


### Third Row (Temperature indicator LEDs)
TOP_HOT_PIN = 15
TOP_COLD_PIN = 13
TOP_GOOD_PIN = 14
BOTTOM_HOT_PIN = 8
BOTTOM_COLD_PIN = 11
BOTTOM_GOOD_PIN = 10



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

        pass

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

    def prepare_for_run(self, allSensorValues, lcd, led_gpio):
        lcd.clear()
        lcd.message("Press Green button\nto start run")

        # set run parameters

        if pg.start_button:
            return AutoStates.Pressurizing
        return AutoStates.Entering

    def pressurize(self, allSensorValues, lcd, led_gpio):
        lcd.clear()
        lcd.message("Pressurizing...")

        ## before allowing a transition to running state, set start time

        pg.intake_solenoid_on = not pg.intake_solenoid_off


        self.start_time = time.time()
        self.top_start_temperature = allSensorValues[0]
        self.bottom_start_temperature = allSensorValues[1]

        #verify which sensor value...and calibrate
        # if allSensorValues[3][1] > 700:
        #     return AutoStates.Running
        # return AutoStates.Pressurizing

        return AutoStates.Running

    def do_run(self, allSensorValues, lcd, led_gpio):
        lcd.clear()
        lcd.message("Running...")
        if pg.stop_button:
            pg.intake_solenoid_on = False
            pg.exhaust_solenoid_on = True
            pg.top_heat_blanket_on = False
            pg.bottom_heat_blanket_on = False
            return AutoStates.Aborted

        #unless being overridden, keep the intake solenoid on for the duration of the run
        pg.intake_solenoid_on = not pg.intake_solenoid_off

        #fill buffer of temperatures
        self.top_blanket_temperatures.append(allSensorValues[0])
        self.bottom_blanket_temperatures.append(allSensorValues[1])

        #if the buffer is full, calculate duty cycle
        if len(self.top_blanket_temperatures) >= self.buffer_length:
            self.top_duty_cycle = self.top_duty_cycle +\
                                  self.determine_blanket_desired_duty_cycle(pg.top_rampup_time, self.top_blanket_temperatures, self.top_start_temperature, pg.top_max_temp)
            self.bottom_duty_cycle = self.bottom_duty_cycle +\
                                     self.determine_blanket_desired_duty_cycle(pg.bottom_rampup_time, self.bottom_blanket_temperatures, self.bottom_start_temperature, pg.bottom_max_temp)

            # constrain duty cycles to 0-100%
            self.top_duty_cycle = max(0, min(1, self.top_duty_cycle))
            self.bottom_duty_cycle = max(0, min(1, self.bottom_duty_cycle))

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
        lcd.message("Run finished.\nPress green button to reset.")
        return AutoStates.Finished

    def error(self, allSensorValues, lcd, led_gpio):
        # turn on error light
        # turn off relays except if over-pressurized, then let off extra pressure
        # await start button for reset
        if pg.start_button:
            return AutoStates.Entering
        return AutoStates.Error

    def abort(self, allSensorValues = None, lcd = None, led_gpio = None):
        # turn off relays
        # reset lights
        # close run data
        # confirm if system is pressurized
            # otherwise await depressurization
        return True

    ## "private" methods...
    def determine_target_temperature(self, rampup_time, start_temperature, max_temperature):
        elapsed_time = int(time.time() - self.start_time)

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
        led_gpio.output(TOP_HOT_PIN, not allSensorValues[0] > top_target_temp)
        led_gpio.output(TOP_COLD_PIN, not allSensorValues[0] < top_target_temp)
        led_gpio.output(TOP_GOOD_PIN, not int(allSensorValues[0]) == int(top_target_temp))

        led_gpio.output(BOTTOM_HOT_PIN, not allSensorValues[1] > bottom_target_temp)
        led_gpio.output(BOTTOM_COLD_PIN, not allSensorValues[1] < bottom_target_temp)
        led_gpio.output(BOTTOM_GOOD_PIN, not int(allSensorValues[1]) == int(bottom_target_temp))

class AutomaticState:
    def __init__(self):
        self.auto_state = AutoStates.Entering
        self.state_actions = AutomaticStateActions()

    def enter(self):
        print "Entering Automatic State"
        self.auto_state = AutoStates.Entering
        self.state_actions = AutomaticStateActions()
        return self

    def exit(self):
        print "Exiting Automatic State"
        return self.state_actions.abort()

    def in_state(self, allSensorValues, lcd, led_gpio):
        self.auto_state = self.state_actions.perform_action(self.auto_state, allSensorValues, lcd, led_gpio)
        print "In Automatic State"
            # if self.myTemps.__len__() == self.bufferLength:
            #     timeArray = np.array([myTimes, np.ones(self.bufferLength)])
            #     fitSlope, fitIntercept = np.linalg.lstsq(timeArray.T, myTemps)[0]
            #     targetSlope = 0
            #
            #     if self.counter < self.rampup_time:
            #         targetSlope = get_target_slope(self.initialTemp, self.max_temperature, self.rampup_time)
            #         targetIntercept = self.initialTemp
            #     else:
            #         targetIntercept = self.max_temperature
            #
            #     futureTime = self.counter + 15
            #     yError = (targetSlope * futureTime + targetIntercept) - (fitSlope * futureTime + fitIntercept)
            #
            #
            #     if yError > 0.25:  # increase dutyCycle if we're below target temp
            #         dutyCycle = min(dutyCycle + 0.1, 1.0)
            #     elif yError < -0.25:
            #         dutyCycle = max(dutyCycle - 0.1, 0.0)
            #
            #
            #     print('---------------------------------------------------')
            #     print('Least Squares Values: m={0:0.3F}\tb={1:0.3F}\tyError={2:0.3F}\tNewDutyCycle={3:0.2F}'.format(
            #         fitSlope, fitIntercept, yError, dutyCycle))
            #     print('---------------------------------------------------')
            #     # with open("fit{0}.txt".format("-s1" if args['sensor'] == '1' else "-s2"), "a") as myFile:
            #     #     myFile.write('{0:0.3F}\t{1:0.3F}\t{2:0.3F}\t{3:0.2F}\n'.format(fitSlope, fitIntercept, yError, dutyCycle))
            #     self.storedTimes += myTimes
            #     self.storedTemps += myTemps
            #     myTemps = []
            #     myTimes = []
            #
            # print('Thermocouple Temperature: {0:0.3F}*C / {1:0.3F}*F'.format(self.temp, Utilities.c_to_f(self.temp)))
            # #    print('    Internal Temperature: {0:0.3F}*C / {1:0.3F}*F'.format(internal2, c_to_f(internal2)))
