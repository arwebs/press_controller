
import Adafruit_MAX31855.MAX31855 as MAX31855
import Adafruit_MCP3008
import RPi.GPIO as GPIO

def setup_pins():
    print "Setup Pins."
    # setting up SPI connected devices (temperature sensors and analog sensors)
    clk = 11
    cs_sensor_1 = 7
    cs_sensor_2 = 7
    cs_analog = 8
    data_out = 9
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

        return [sensor, sensor2, mcp]
    except:
        print 'Could not reach temperature sensors or analog sensor.'

def setup_sensors():
    print "Setup sensors."

def get_sensor_values(sensor, sensor2, analogSensors, digitalSensors):
    print "Checking Sensors."
    GPIO.output(22, True)
    i = 0
    #sensor = self.temperature_sensors[i]
    temp = sensor.readTempC()
    # internal = sensor.readInternalC()
    GPIO.output(22, False)
    GPIO.output(27, True)
    i = 1
    #sensor = self.temperature_sensors[i]
    temp1 = sensor2.readTempC()
    # internal1 = sensor.readInternalC()
    GPIO.output(27, False)
    analog_spi_select = 17
    GPIO.output(analog_spi_select, True)
    analog_input_values = [0] * 8
    for sensor in range(8):
        # The read_ad function will get the value of the specified channel (0-7).
        analog_input_values[sensor] = analogSensors.read_adc(sensor)
    GPIO.output(analog_spi_select, False)
    digital_input_values = [0] * 16
    for i in range(16):
        digital_input_values[i] = digitalSensors.input(i)

    return temp, temp1, analog_input_values, digital_input_values

    return []

def is_there_a_sensor_problem(allSensorValues):
    return False

def is_there_an_input_problem(allInputValues):
    return False

def get_input_values():
    print "Reading Inputs."
    return []

def handle_sensor_problem():
    print "handling sensor problem"

def handle_input_problem():
    print "handling input problem"

def set_power_leds():
    print "setting power LEDs"

def attempt_to_leave_current_state():
    print "attempting to leave current state"
    return True

def is_new_state_requested(currentState, allInputValues):
    print "figuring out if newstate was requested"
    return True

def enter_new_state():
    print "entering new state"

def perform_state_specific_operations():
    print "performing state specific operations..."

sensorProblem = False
inputProblem = False
newStateRequested = True
currentState = "Startup"


setup_pins()
setup_sensors()

while True:
    allSensorValues = get_sensor_values()

    if is_there_a_sensor_problem(allSensorValues):
        handle_sensor_problem()

    allInputValues = get_input_values()
    if is_there_an_input_problem(allInputValues):
        handle_input_problem()

    set_power_leds()


    newStateRequested = is_new_state_requested(currentState, allInputValues)
    if newStateRequested:
        successfullyLeftState = attempt_to_leave_current_state()
        if successfullyLeftState:
            currentState = "TODO: newState"
            enter_new_state()
    perform_state_specific_operations()