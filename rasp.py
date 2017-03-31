import math
import numpy as np
import argparse as ap
import time

import Adafruit_CharLCD as LCD
import Adafruit_GPIO.MCP230xx as MCP
import Adafruit_MAX31855.MAX31855 as MAX31855
import Adafruit_MCP3008

class Utilities:
    @staticmethod
    def c_to_f(c):
        return c * 9.0 / 5.0 + 32.0

    class fake_lcd():
        def clear(self):
            print 'LCD Cleared'
        def message(self,text):
            print 'LCD Text: ' + text

class MainControl:
    # program_mode = None
    # lcd = None
    # temperature_sensors = None
    # analog_sensor = None

    def __init__(self):
        self.program_mode = 'Manual'
        self.lcd = Utilities.fake_lcd() #todo remove this and enable setup_lcd()
        # self.setup_lcd()
        self.setup_spi_interfaces()

    def setup_lcd(self):
        lcd_rs        = 0
        lcd_en        = 1
        lcd_d4        = 2
        lcd_d5        = 3
        lcd_d6        = 4
        lcd_d7        = 5
        lcd_red       = 6
        lcd_green     = 7
        lcd_blue      = 8

        lcd_columns = 20
        lcd_rows    = 4

        gpio = MCP.MCP23017(0x22,busnum=1)
        self.lcd = LCD.Adafruit_RGBCharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7,
                                      lcd_columns, lcd_rows, lcd_red, lcd_green, lcd_blue,
                                      gpio=gpio)
    def setup_spi_interfaces(self):
        clk = 18
        cs_sensor_1  = 16
        cs_sensor_2 = 12
        cs_analog = 25
        data_out  = 23
        data_in = 24
        sensor = MAX31855.MAX31855(clk, cs_sensor_1, data_out)
        sensor2 = MAX31855.MAX31855(clk, cs_sensor_2, data_out)
        mcp = Adafruit_MCP3008.MCP3008(clk=clk, cs=cs_analog, miso=data_out, mosi=data_in)

        self.temperature_sensors = [sensor, sensor2]
        self.analog_sensor = mcp


    def check_program_mode(self):
        #TODO get mode selection from input
        print 'Checking Program State'

    def set_relays(self):
        print "setting relays"
        #TODO set relays based on input or program state

    def main_control_loop(self):
        while self.program_mode == 'Manual':
            self.lcd.clear()
            for i, sensor in enumerate(self.temperature_sensors):
                temp = sensor.readTempC()
                internal = sensor.readInternalC()
                print('Thermocouple {2} Temperature: {0:0.3F}*C / {1:0.3F}*F'.format(temp, Utilities.c_to_f(temp), i))
                print('    Internal {2} Temperature: {0:0.3F}*C / {1:0.3F}*F'.format(internal, Utilities.c_to_f(internal), i))
                self.lcd.message('T{2}:{0:0.2F}*C/{1:0.2F}*F\n'.format(internal, Utilities.c_to_f(internal), i))

            values = [0] * 8
            for sensor in range(8):
                # The read_ad function will get the value of the specified channel (0-7).
                values[sensor] = self.analog_sensor.read_adc(sensor)
            print('| {0:>4} | {1:>4} | {2:>4} | {3:>4} | {4:>4} | {5:>4} | {6:>4} | {7:>4} |'.format(*values))
            self.lcd.message('Pot: {0}'.format(values[0]))
            time.sleep(2.0)
            self.set_relays()
            self.check_program_mode()

        while self.program_mode == 'Configure':
            self.lcd.clear()

            self.check_program_mode()

        while self.program_mode == 'Automatic':
            self.lcd.clear()

            self.check_program_mode()

control = MainControl()
while True:
    control.main_control_loop()

#
# def get_target_slope(initial_temp, target_temp, rampup):
#     return (target_temp - initial_temp) / rampup
#
# class SensorState:
#     duty_cycle = 0.5
#     initial_temp = 0.
#     current_temp = 0.
#     rampup_time = 20.
#     hold_time = 20.
#     max_temp = 180.
#     def __init__(self):
#         self.duty_cycle= 0.5
#
#
#
# parser = ap.ArgumentParser(description='Temperature controller')
# parser.add_argument('-s', '--sensor', help='Sensor', required=False)
# parser.add_argument('-t', '--temperature', help='Maximum Temperature, degrees C', required=False)
# parser.add_argument('-d', '--duration', help='Duration of run in seconds', required=False)
# parser.add_argument('-r', '--rampup', help='Time to ramp up to temperature in seconds', required=False)
# args = vars(parser.parse_args())
# print args
#
# CLK = 25
# DO = 18
#
# sensors = [MAX31855.MAX31855(CLK, 24, DO), MAX31855.MAX31855(CLK, 28, DO) ]
#
# myTimes = []
# myTemps = []
# storedTimes = []
# storedTemps = []
# counter = 0.
#
# dutyCycle = 0.5
# bufferLength = 10
#
# initialTemp = sensors[0].readTempC()
#
# isOn = False
#
# while counter < int(args['duration']):
#     temp = sensor.readTempC()
#     internal = sensor.readInternalC()
#
#     if temp != float("NAN"):
#         myTimes.append(counter)
#         myTemps.append(temp)
#     else:
#         print "error reading temperature. duty cycle may be wrong"
#
#     if (counter % bufferLength) == 0 and dutyCycle > 0 and isOn == False:
#         # TODO turn On Relay
#         isOn = True
#
#     if (counter % bufferLength) / float(bufferLength) >= dutyCycle and isOn == True:
#         # TODO turn Off Relay
#         isOn = False
#
#     counter += 1.
#     with open("temps{0}.txt".format("-s1" if args['sensor'] == '1' else "-s2"), "a") as myFile:
#         myFile.write('{0:0.3F}\t{1}\n'.format(temp, "1" if isOn else "0"))
#     if myTemps.__len__() == bufferLength:
#         timeArray = np.array([myTimes, np.ones(bufferLength)])
#         fitSlope, fitIntercept = np.linalg.lstsq(timeArray.T, myTemps)[0]
#         targetSlope = 0
#         targetIntercept = 0
#
#         if counter < float(args['rampup']):
#             targetSlope = get_target_slope(initialTemp, float(args['temperature']), int(args['rampup']))
#             targetIntercept = initialTemp
#         else:
#             targetIntercept = float(args['temperature'])
#
#         futureTime = counter + 15
#         yError = (targetSlope * futureTime + targetIntercept) - (fitSlope * futureTime + fitIntercept)
#         currentYError = (targetSlope * counter + targetIntercept) - (fitSlope * counter + fitIntercept)
#
#         if yError > 0.25:  # increase dutyCycle if we're below target temp
#             dutyCycle = min(dutyCycle + 0.1, 1.0)
#         elif yError < -0.25:
#             dutyCycle = max(dutyCycle - 0.1, 0.0)
#
#         if currentYError < -1.0:  # if we are currently too hot, take immediate action
#             dutyCycle = 0.0
#
#         print('---------------------------------------------------')
#         print('Sensor {4}: Least Squares Values: m={0:0.3F}\tb={1:0.3F}\tyError={2:0.3F}\tNewDutyCycle={3:0.2F}'.format(
#             fitSlope, fitIntercept, yError, dutyCycle, args['sensor']))
#         print('---------------------------------------------------')
#         with open("fit{0}.txt".format("-s1" if args['sensor'] == '1' else "-s2"), "a") as myFile:
#             myFile.write('{0:0.3F}\t{1:0.3F}\t{2:0.3F}\t{3:0.2F}\n'.format(fitSlope, fitIntercept, yError, dutyCycle))
#         x = np.arange((counter - bufferLength), counter, 1)
#
#         storedTimes += myTimes
#         storedTemps += myTemps
#         myTemps = []
#         myTimes = []
#
#     print('Sensor {2}: Thermocouple Temperature: {0:0.3F}*C / {1:0.3F}*F'.format(temp, c_to_f(temp), args['sensor']))
#     #    print('    Internal Temperature: {0:0.3F}*C / {1:0.3F}*F'.format(internal2, c_to_f(internal2)))
#     time.sleep(1)
#
# relayControl.turnOff()
# print 'finished run, relay off'
