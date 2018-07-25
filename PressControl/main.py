
import Adafruit_MAX31855.MAX31855 as MAX31855
import Adafruit_MCP3008
import Adafruit_CharLCD as LCD
import Adafruit_GPIO.MCP230xx as MCP
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

    #lcd i2c pins
    lcd_rs = 8
    lcd_en = 10
    lcd_d4 = 4
    lcd_d5 = 5
    lcd_d6 = 6
    lcd_d7 = 7
    lcd_red = 13
    lcd_green = 14
    lcd_blue = 15

    lcd_columns = 20
    lcd_rows = 4

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
        #temperature sensors
        sensor = MAX31855.MAX31855(clk, cs_sensor_1, data_out)
        sensor2 = MAX31855.MAX31855(clk, cs_sensor_2, data_out)
        #analog sensors (POTS & pressure sensor)
        analog_sensors = Adafruit_MCP3008.MCP3008(clk=clk, cs=cs_analog, miso=data_out, mosi=data_in)

        #lcd screen
        gpio = MCP.MCP23017(0x22, busnum=1)

        # must set enable bit to low value
        gpio.setup(9, GPIO.OUT)
        gpio.output(9, GPIO.LOW)

        lcd = LCD.Adafruit_RGBCharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows, lcd_red, lcd_green, lcd_blue,gpio=gpio)
        lcd.message("Hello!")

        digital_gpio = MCP.MCP23017(0x21, busnum=1)
        for i in range(0, 4):
            digital_gpio.output(i, GPIO.HIGH)
        for i in range(4, 16):
            digital_gpio.setup(i, GPIO.IN)
            digital_gpio.pullup(i, True)

        return [sensor, sensor2, analog_sensors, digital_gpio, lcd]
    except Exception as e:
        print(e)
        print 'Could not reach temperature sensors or analog sensor.'

def get_sensor_values(sensor, sensor2, analogSensors, digitalSensors):
    print "Checking Sensors."
    GPIO.output(22, True)
    #sensor = self.temperature_sensors[i]
    temp = sensor.readTempC()
    # internal = sensor.readInternalC()
    GPIO.output(22, False)
    GPIO.output(27, True)
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


(sensor, sensor2, analog_input_values, digital_input_values, lcd)= setup_pins()

while True:
    allSensorValues = get_sensor_values(sensor, sensor2, analog_input_values, digital_input_values)
    print allSensorValues[0]
    print allSensorValues[1]
    print allSensorValues[2]
    print allSensorValues[3]
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