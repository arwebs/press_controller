import press_globals as pg
import numpy as np
import time
import Utilities

def determine_target_temperature(elapsed_time, rampup_time, start_temperature, max_temperature):
    # if rampup time is finished, just return max temperature so we hold there
    if elapsed_time > rampup_time:
        return max_temperature

    # in the rampup period, find the equation of the line and plug in elapsed time to find target
    slope = (max_temperature - start_temperature) / rampup_time
    return slope * elapsed_time + start_temperature

def determine_blanket_desired_duty_cycle(current_temperature, target_temperature, last_n_temperatures):
    return 0.5

class AutomaticStateActions:
    def __init__(self):
        self.top_blanket_temperatures = []
        self.bottom_blanket_temperatures = []
        self.top_duty_cycle = 0.5
        self.bottom_duty_cycle = 0.5
        self.bufferLength = 10
        self.start_time = time.time()
        self.top_start_temperature = 0.
        self.bottom_start_temperature = 0.
        self.counter = 0
        pass

    def prepare_for_run(self, allSensorValues):
        # set run parameters
        # await start button press
        return ""

    def await_start(self):
        #display run parameters
        #wait for start button to be pressed
        return ""

    def pressurize(self):
        # pressurize system
        # once pressurized, proceed to run
        ## before allowing a transition to running state, set start time
        self.start_time = time.time()
        self.top_start_temperature = allSensorValues[0]
        self.bottom_start_temperature = allSensorValues[1]
        # if stop button pressed, open relief valve until pressure < 20psi
        return ""

    def do_run(self, allSensorValues):
        if pg.stop_button:
            # turn off relays
            # log run
            return ""
        elapsed_time = time.time() - self.start_time

        #fill buffer of temperatures
        self.top_blanket_temperatures.append(allSensorValues[0])
        self.bottom_blanket_temperatures.append(allSensorValues[1])

        top_target_temp = determine_target_temperature(elapsed_time, pg.top_rampup_time, self.top_start_temperature, pg.top_max_temp)
        bottom_target_temp = determine_target_temperature(elapsed_time, pg.bottom_rampup_time, self.bottom_start_temperature, pg.bottom_max_temp)

        #if the buffer is full, calculate duty cycle
        if len(self.top_blanket_temperatures) >= self.bufferLength:
            self.top_duty_cycle = determine_blanket_desired_duty_cycle(
                allSensorValues[0], top_target_temp, self.top_blanket_temperatures)
            self.bottom_duty_cycle = determine_blanket_desired_duty_cycle(allSensorValues[1],
                bottom_target_temp, self.bottom_blanket_temperatures)
            self.top_blanket_temperatures = []
            self.bottom_blanket_temperatures = []

        # if we're too hot, take immediate action
        if allSensorValues[0] > top_target_temp + 0.5:
            self.top_duty_cycle = 0

        if allSensorValues[1] > bottom_target_temp + 0.5:
            self.bottom_duty_cycle = 0

        # set blanket on/off status based on
        self.counter = (self.counter + 1) % 10
        pg.top_heat_blanket_on = (self.top_duty_cycle * 10) > self.counter
        pg.bottom_heat_blanket_on = (self.bottom_duty_cycle * 10) > self.counter

        if elapsed_time > pg.total_run_duration:
            return "Finished"
        return "Running"

    def finish(self):
        if pg.start_button:
            return ""
        return "Finished"

    def error(self):
        # turn on error light
        # turn off relays except if over-pressurized, then let off extra pressure
        # await start button for reset
        pass

    def abort(self):
        # turn off relays
        # reset lights
        # close run data
        # confirm if system is pressurized
            # otherwise await depressurization
        return True

class AutomaticState:
    def __init__(self):
        self.auto_state = "Entering"
        self.state_actions = AutomaticStateActions()

    def enter(self):
        print "Entering Automatic State"
        self.auto_state = "Entering"
        return self

    def exit(self):
        print "Exiting Automatic State"
        return self.state_actions.abort()

    def in_state(self, allSensorValues, lcd, led_gpio):
        if self.auto_state == "Entering":
            self.auto_state = self.state_actions.prepare_for_run()
        elif self.auto_state == "Pressurizing":
            self.auto_state = self.state_actions.pressurize()
        elif self.auto_state == "Running":
            self.auto_state = self.state_actions.do_run()
        elif self.auto_state == "Finished":
            self.auto_state = self.state_actions.finish()
        elif self.auto_state == "Error":
            self.auto_state = self.state_actions.error()



        def get_target_slope(initial_temp, target_temp, rampup):
            return (target_temp - initial_temp) / rampup

        print "In Automatic State"
        lcd.clear()
        lcd.message("In Automatic State")


        while self.counter < self.duration:  # TODO need to refactor such that this doesn't block main control loop
            self.temp = allSensorValues[0]

            if self.temp != float("NAN") and self.temp != 0.0:
                self.myTimes.append(self.counter)
                self.myTemps.append(self.temp)
            else:
                print "error reading temperature. duty cycle may be wrong"

            if (self.counter % self.bufferLength) == 0 and self.dutyCycle > 0 and self.isOn == False:
                # TODO turn On Relay
                self.isOn = True

            if (self.counter % self.bufferLength) / float(self.bufferLength) >= self.dutyCycle and self.isOn == True:
                # TODO turn Off Relay
                self.isOn = False

                self.counter += 1.
            # TODO Logging/persist to DB
            if self.myTemps.__len__() == self.bufferLength:
                timeArray = np.array([myTimes, np.ones(self.bufferLength)])
                fitSlope, fitIntercept = np.linalg.lstsq(timeArray.T, myTemps)[0]
                targetSlope = 0

                if self.counter < self.rampup_time:
                    targetSlope = get_target_slope(self.initialTemp, self.max_temperature, self.rampup_time)
                    targetIntercept = self.initialTemp
                else:
                    targetIntercept = self.max_temperature

                futureTime = self.counter + 15
                yError = (targetSlope * futureTime + targetIntercept) - (fitSlope * futureTime + fitIntercept)
                currentYError = (targetSlope * self.counter + targetIntercept) - (fitSlope * self.counter + fitIntercept)

                if yError > 0.25:  # increase dutyCycle if we're below target temp
                    dutyCycle = min(dutyCycle + 0.1, 1.0)
                elif yError < -0.25:
                    dutyCycle = max(dutyCycle - 0.1, 0.0)

                if currentYError < -1.0:  # if we are currently too hot, take immediate action
                    dutyCycle = 0.0

                print('---------------------------------------------------')
                print('Least Squares Values: m={0:0.3F}\tb={1:0.3F}\tyError={2:0.3F}\tNewDutyCycle={3:0.2F}'.format(
                    fitSlope, fitIntercept, yError, dutyCycle))
                print('---------------------------------------------------')
                # with open("fit{0}.txt".format("-s1" if args['sensor'] == '1' else "-s2"), "a") as myFile:
                #     myFile.write('{0:0.3F}\t{1:0.3F}\t{2:0.3F}\t{3:0.2F}\n'.format(fitSlope, fitIntercept, yError, dutyCycle))
                self.storedTimes += myTimes
                self.storedTemps += myTemps
                myTemps = []
                myTimes = []

            print('Thermocouple Temperature: {0:0.3F}*C / {1:0.3F}*F'.format(self.temp, Utilities.c_to_f(self.temp)))
            #    print('    Internal Temperature: {0:0.3F}*C / {1:0.3F}*F'.format(internal2, c_to_f(internal2)))
            time.sleep(1)

        pg.top_heat_blanket_on = False
        pg.bottom_heat_blanket_on = False
        pg.intake_solenoid_on = False
        pg.exhaust_solenoid_on = False
