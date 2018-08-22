import press_globals as pg
import numpy as np
import time
import Utilities

class AutomaticStateActions:
    def __init__(self):
        self.temperatureBuffer
        pass

    def prepare_for_run(self):
        pass

    def do_run(self):
        if pg.stop_button:
            # turn off relays
            # log run
            pass



    def finish(self):
        pass

    def error(self):
        pass

    def abort(self):
        # turn off relays
        # reset lights
        # close run data
        return True

class AutomaticState:
    def __init__(self):
        self.duration = 40 * 60  # TODO set this
        self.rampup_time = 20 * 60  # TODO set this
        self.max_temperature = 82  # TODO set this

        self.myTimes = []
        self.myTemps = []
        self.storedTimes = []
        self.storedTemps = []
        self.counter = 0.

        self.dutyCycle = 0.5
        self.bufferLength = 10

        self.initialTemp = 0.

        self.isOn = False
        self.auto_state = "Entering"
        self.state_actions = AutomaticStateActions()

    def enter(self):
        print "Entering Automatic State"
        self.auto_state = "Entering"

        self.duration = 40 * 60  # TODO set this
        self.rampup_time = 20 * 60  # TODO set this
        self.max_temperature = 82  # TODO set this

        self.myTimes = []
        self.myTemps = []
        self.storedTimes = []
        self.storedTemps = []
        self.counter = 0.

        self.dutyCycle = 0.5
        self.bufferLength = 10

        self.initialTemp = 25. #allSensorValues[0]

        self.isOn = False

        return self
    def exit(self):
        print "Exiting Automatic State"
        if self.auto_state == "Running":
            return self.state_actions.abort()
        return True

    def in_state(self, allSensorValues, lcd, led_gpio):
        if self.auto_state == "Entering":
            self.state_actions.prepare_for_run()
        elif self.auto_state == "Running":
            self.state_actions.do_run()
        elif self.auto_state == "Finished":
            self.state_actions.finish()
        elif self.auto_state == "Error":
            self.state_actions.error()



        def get_target_slope(initial_temp, target_temp, rampup):
            return (target_temp - initial_temp) / rampup

        print "In Automatic State"
        lcd.clear()
        lcd.message("In Automatic State")
        lcd.clear()

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