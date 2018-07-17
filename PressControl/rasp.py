import time
import numpy as np
import ConfigParser
import os.path
import Adafruit_CharLCD as LCD
import Adafruit_GPIO.MCP230xx as MCP
import Adafruit_MAX31855.MAX31855 as MAX31855
import Adafruit_MCP3008
import RPi.GPIO as GPIO

import Utilities
import LedOutputs
import DigitalInputs
from CharLcdOutput import CharLcdOutput

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

class MainControl:
    def __init__(self):
        self.program_mode = 'Startup'
        self.mode_state = 'Startup'
        self.previous_program_mode = 'Startup'
        self.lcd = CharLcdOutput.setup_char_lcd()
        #setting up SPI connected devices (temperature sensors and analog sensors)
        clk = 11
        cs_sensor_1  = 7
        cs_sensor_2 = 7
        cs_analog = 8
        data_out  = 9
        data_in = 10

        # set I2C reset pin high so we can see those devices
        i2c_reset = 21
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(i2c_reset, GPIO.OUT)
        GPIO.output(i2c_reset, True)

        # set spi selector high so that we can engage the A2D chip
        analog_spi_select = 17
        GPIO.setup(analog_spi_select, GPIO.OUT)
        GPIO.setup(27, GPIO.OUT)
        GPIO.setup(22, GPIO.OUT)
        GPIO.output(analog_spi_select, True)

        try:
            sensor = MAX31855.MAX31855(clk, cs_sensor_1, data_out)
            sensor2 = MAX31855.MAX31855(clk, cs_sensor_2, data_out)

            mcp = Adafruit_MCP3008.MCP3008(clk=clk, cs=cs_analog, miso=data_out, mosi=data_in)

            self.temperature_sensors = [sensor, sensor2]
            self.analog_sensor = mcp
        except:
            print 'Could not reach temperature sensors or analog sensor.'

        # set up I2C GPIO for LEDs
        try:
            self.led_gpio = MCP.MCP23017(0x20, busnum=1)
            for i in range(0,16):
                self.led_gpio.setup(i, GPIO.OUT)
                self.led_gpio.output(i, GPIO.HIGH) #True is HIGH is OFF, False is LOW is ON
                #time.sleep(0.2)
            time.sleep(2)
            for i in range(0,16):
                self.led_gpio.output(i, GPIO.LOW) #True is HIGH is OFF, False is LOW is ON
                #time.sleep(0.1)


        except:
            print 'Could not reach LED control chip'

        # set up I2C GPIO for inputs
        try:
            self.digital_gpio = MCP.MCP23017(0x21, busnum=1)
            for i in range(0,4):
                self.digital_gpio.output(i,GPIO.HIGH)
            for i in range(4,16):
                self.digital_gpio.setup(i, GPIO.IN)
                self.digital_gpio.pullup(i, True)


        except:
            print 'Could not reach digital input control chip'

    def check_program_mode(self):

        self.mode_state
        self.program_mode
        pass
        #print 'Checking Program State'

    def set_relays(self):
        pass
        #print "setting relays"
        #TODO set relays based on input or program state

    def main_control_loop(self):
        temp, temp1, analog_input_values, digital_input_values = self.get_all_inputs()
        DigitalInputs.update_input_values(digital_input_values)
        if self.program_mode != self.previous_program_mode:
            pass
            # handle state changes first

        if self.program_mode == 'Manual':
            #self.lcd.clear()
            # GPIO.output(22, True)
            # i = 0
            # sensor = self.temperature_sensors[i]
            # temp = sensor.readTempC()
            # internal = sensor.readInternalC()
            # print('Thermocouple {2} Temperature: {0:0.3F}*C / {1:0.3F}*F'.format(temp, Utilities.c_to_f(temp), i))
            # print('    Internal {2} Temperature: {0:0.3F}*C / {1:0.3F}*F'.format(internal, Utilities.c_to_f(internal), i))
            # self.lcd.message('T{2}:{0:0.2F}*C/{1:0.2F}*F\n'.format(internal, Utilities.c_to_f(internal), i))
            # GPIO.output(22, False)
            # GPIO.output(27, True)
            # i = 1
            # sensor = self.temperature_sensors[i]
            # temp = sensor.readTempC()
            # internal = sensor.readInternalC()
            # print('Thermocouple {2} Temperature: {0:0.3F}*C / {1:0.3F}*F'.format(temp, Utilities.c_to_f(temp), i))
            # print('    Internal {2} Temperature: {0:0.3F}*C / {1:0.3F}*F'.format(internal, Utilities.c_to_f(internal), i))
            # self.lcd.message('T{2}:{0:0.2F}*C/{1:0.2F}*F\n'.format(internal, Utilities.c_to_f(internal), i))
            # GPIO.output(27, False)
            #
            # analog_spi_select = 17
            # GPIO.output(analog_spi_select, True)
            # values = [0] * 16
            # for sensor in range(8):
            #     # The read_ad function will get the value of the specified channel (0-7).
            #     values[sensor] = self.analog_sensor.read_adc(sensor)
            # print('| {0:>4} | {1:>4} | {2:>4} | {3:>4} | {4:>4} | {5:>4} | {6:>4} | {7:>4} |'.format(*values))
            # GPIO.output(analog_spi_select, False)
            # for i in range(16):
            #     values[i] = self.digital_gpio.input(i)
            # print('| {0:>4} | {1:>4} | {2:>4} | {3:>4} | {4:>4} | {5:>4} | {6:>4} | {7:>4} |'.format(*values))
            # print('| {8:>4} | {9:>4} | {10:>4} | {11:>4} | {12:>4} | {13:>4} | {14:>4} | {15:>4} |'.format(*values))

            time.sleep(1.0)
            self.set_relays()

        elif self.program_mode == 'Configure':
            self.lcd.clear()

        elif self.program_mode == 'Automatic':
            self.lcd.clear()

            def get_target_slope(initial_temp, target_temp, rampup):
                return (target_temp - initial_temp) / rampup

            duration = 40*60 #TODO set this
            rampup_time = 20*60 #TODO set this
            max_temperature = 82 #TODO set this

            myTimes = []
            myTemps = []
            storedTimes = []
            storedTemps = []
            counter = 0.

            dutyCycle = 0.5
            bufferLength = 10

            initialTemp = self.temperature_sensors[0].readTempC()

            isOn = False

            while counter < duration: #TODO need to refactor such that this doesn't block main control loop
                temp = self.temperature_sensors[0].readTempC()
                internal = self.temperature_sensors[0].readInternalC()

                if temp != float("NAN"):
                    myTimes.append(counter)
                    myTemps.append(temp)
                else:
                    print "error reading temperature. duty cycle may be wrong"

                if (counter % bufferLength) == 0 and dutyCycle > 0 and isOn == False:
                    # TODO turn On Relay
                    isOn = True

                if (counter % bufferLength) / float(bufferLength) >= dutyCycle and isOn == True:
                    # TODO turn Off Relay
                    isOn = False

                counter += 1.
                #TODO Logging/persist to DB
                #with open("temps{0}.txt".format("-s1" if args['sensor'] == '1' else "-s2"), "a") as myFile:
                #    myFile.write('{0:0.3F}\t{1}\n'.format(temp, "1" if isOn else "0"))
                if myTemps.__len__() == bufferLength:
                    timeArray = np.array([myTimes, np.ones(bufferLength)])
                    fitSlope, fitIntercept = np.linalg.lstsq(timeArray.T, myTemps)[0]
                    targetSlope = 0

                    if counter < rampup_time:
                        targetSlope = get_target_slope(initialTemp, max_temperature, rampup_time)
                        targetIntercept = initialTemp
                    else:
                        targetIntercept = max_temperature

                    futureTime = counter + 15
                    yError = (targetSlope * futureTime + targetIntercept) - (fitSlope * futureTime + fitIntercept)
                    currentYError = (targetSlope * counter + targetIntercept) - (fitSlope * counter + fitIntercept)

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
                    storedTimes += myTimes
                    storedTemps += myTemps
                    myTemps = []
                    myTimes = []

                print('Thermocouple Temperature: {0:0.3F}*C / {1:0.3F}*F'.format(temp, Utilities.c_to_f(temp)))
                #    print('    Internal Temperature: {0:0.3F}*C / {1:0.3F}*F'.format(internal2, c_to_f(internal2)))
                time.sleep(1)
            # relayControl.turnOff()
            print 'finished run, relay off'

        self.check_program_mode()

    def get_all_inputs(self):
        GPIO.output(22, True)
        i = 0
        sensor = self.temperature_sensors[i]
        temp = sensor.readTempC()
        # internal = sensor.readInternalC()
        GPIO.output(22, False)
        GPIO.output(27, True)
        i = 1
        sensor = self.temperature_sensors[i]
        temp1 = sensor.readTempC()
        # internal1 = sensor.readInternalC()
        GPIO.output(27, False)
        analog_spi_select = 17
        GPIO.output(analog_spi_select, True)
        analog_input_values = [0] * 8
        for sensor in range(8):
            # The read_ad function will get the value of the specified channel (0-7).
            analog_input_values[sensor] = self.analog_sensor.read_adc(sensor)
        GPIO.output(analog_spi_select, False)
        digital_input_values = [0] * 16
        for i in range(16):
            digital_input_values[i] = self.digital_gpio.input(i)

        return temp, temp1, analog_input_values, digital_input_values

class SensorState:
    duty_cycle = 0.5
    initial_temp = 0.
    current_temp = 0.
    rampup_time = 20.
    hold_time = 20.
    max_temp = 180.
    def __init__(self):
        self.duty_cycle= 0.5

config_path = './pywork/.press_config'
print os.getcwd()
if os.path.isfile(config_path):
    Config = ConfigParser.ConfigParser()
    Config.read(config_path)
    try:
        conn_string = Config.get('ConnectionStrings','ConnectionString')
    except:
        print 'Error reading configuration file.  Expected Section "ConnectionStrings" and Expected Key: "ConnectionString"'
        exit()
else:
    print 'Configuration file not found, expected at ' + config_path
    exit()

control = MainControl()
while True:
    DigitalInputs.read_inputs()
    #AnalogInputs.read_inputs()
    #TemperatureSensors.read_inputs()
    control.main_control_loop()
    LedOutputs.set_outputs()


# engine = create_engine(conn_string, isolation_level="READ UNCOMMITTED")
# Base = declarative_base(engine)
#
# ########################################################################
# class Configuration(Base):
#     """"""
#     __tablename__ = 'Configuration'
#     __table_args__ = {'autoload': True}
# class FitLog(Base):
#     """"""
#     __tablename__ = 'FitLog'
#     __table_args__ = {'autoload': True}
# class RawLog(Base):
#     """"""
#     __tablename__ = 'RawLog'
#     __table_args__ = {'autoload': True}
# class RunInformation(Base):
#     """"""
#     __tablename__ = 'RunInformation'
#     __table_args__ = {'autoload': True}
# # ----------------------------------------------------------------------
# def loadSession():
#     """"""
#     metadata = Base.metadata
#     Session = sessionmaker(bind=engine)
#     session = Session()
#     return session
#
# if __name__ == "__main__":
#     session = loadSession()
#     res = session.query(Configuration).all()
#     # config = Configuration(TotalDuration=2200,TopRampUpTime=1000,BottomRampUpTime=1000,
#     #                        TopTemperature=80,BottomTemperature=80)
#     # session.add(config)
#     # session.commit()
#     print res[0].Id