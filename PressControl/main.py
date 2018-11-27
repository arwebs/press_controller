
import atexit
import time

import Adafruit_CharLCD as LCD
import Adafruit_GPIO.MCP230xx as MCP
import Adafruit_MAX31855.MAX31855 as MAX31855
import Adafruit_MCP3008
import RPi.GPIO as GPIO

import press_globals as pg

from AutomaticState import AutomaticState
from ConfigState import ConfigState
from ManualState import ManualState

import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.gen
from tornado.options import define, options

import multiprocessing
import json
# initialize global variables
pg.init()

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
        sensor_setup = MAX31855.MAX31855(clk=clk, cs=cs_sensor_1, do=data_out)
        sensor2_setup = MAX31855.MAX31855(clk=clk, cs=cs_sensor_2, do=data_out)
        #analog sensors (POTS & pressure sensor)
        analog_sensors = Adafruit_MCP3008.MCP3008(clk=clk, cs=cs_analog, miso=data_out, mosi=data_in)

        #lcd screen
        gpio = MCP.MCP23017(0x22, busnum=1)

        # must set enable bit to low value
        gpio.setup(9, GPIO.OUT)
        gpio.output(9, GPIO.LOW)

        lcd = LCD.Adafruit_RGBCharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows, lcd_red, lcd_green, lcd_blue,enable_pwm=False, gpio=gpio)
        lcd.message("Hello!")
        lcd.set_color(0, 0, 0)  # 0 [zero] is for On

        # LEDs
        led_gpio = MCP.MCP23017(0x20, busnum=1)
        for i in range(0, 16):
            led_gpio.setup(i, GPIO.OUT)
            led_gpio.output(i, GPIO.HIGH)  # True is HIGH is OFF, False is LOW is ON

        led_gpio.output(pg.POWER_PIN, GPIO.LOW)

        #digital input pins
        digital_gpio = MCP.MCP23017(0x21, busnum=1)
        for i in range(0, 4):
            digital_gpio.setup(i, GPIO.OUT)
            digital_gpio.output(i, GPIO.HIGH)
        for i in range(4, 16):
            digital_gpio.setup(i, GPIO.IN)
            digital_gpio.pullup(i, True)

        return [sensor_setup, sensor2_setup, analog_sensors, digital_gpio, lcd, led_gpio]
    except Exception as e:
        print(e)
        print 'Could not reach temperature sensors or analog sensor.'

# 4	    STOP
# 5	    START
# 6 	Mode switch left
# 7	    Mode switch right
# 8	    Blanket 2 switch left
# 9	    Blanket 2 switch right
# 10	Solenoid 1 switch left
# 11	Solenoid 1 switch right
# 12	Solenoid 2 switch RIGHT
# 13	Solenoid 2 switch LEFT
# 14	Blanket 1 switch left
# 15	Blanket 1 switch right

def update_input_values(digital_input_values):
    pg.start_button = not digital_input_values[5]
    pg.stop_button = not digital_input_values[4]
    pg.manual_mode = not digital_input_values[7]
    pg.auto_mode = digital_input_values[6] and digital_input_values[7]
    pg.config_mode = not digital_input_values[6]
    pg.bottom_heat_blanket_auto = digital_input_values[14] and digital_input_values[15]
    pg.bottom_heat_blanket_off = not digital_input_values[14]
    pg.bottom_heat_blanket_on = not digital_input_values[15]
    pg.top_heat_blanket_auto = digital_input_values[8] and digital_input_values[9]
    pg.top_heat_blanket_off = not digital_input_values[8]
    pg.top_heat_blanket_on = not digital_input_values[9]
    pg.intake_solenoid_auto = digital_input_values[10] and digital_input_values[11]
    pg.intake_solenoid_off = not digital_input_values[10]
    pg.intake_solenoid_on = not digital_input_values[11]
    pg.exhaust_solenoid_auto = digital_input_values[12] and digital_input_values[13]
    pg.exhaust_solenoid_off = not digital_input_values[13]
    pg.exhaust_solenoid_on = not digital_input_values[12]

def get_sensor_values(sensor, sensor2, analogSensors, digitalSensors):
    print "Checking Sensors."
    GPIO.output(22, True)
    temp = sensor.readTempC()
    print sensor.readState()
    GPIO.output(22, False)
    GPIO.output(27, True)
    temp1 = sensor2.readTempC()
    GPIO.output(27, False)
    analog_spi_select = 17
    GPIO.output(analog_spi_select, True)
    analog_input_values = [0] * 8
    for sensor in range(8):
        # The read_adc function will get the value of the specified channel (0-7).
        analog_input_values[sensor] = analogSensors.read_adc(sensor)
    GPIO.output(analog_spi_select, False)
    digital_input_values = [0] * 16
    for i in range(16):
        digital_input_values[i] = digitalSensors.input(i)

    return temp, temp1, analog_input_values, digital_input_values

def is_there_a_sensor_problem(allSensorValues):
    #if either temperature sensor is too hot
    #come back and check pressure value (#3 here)
    return allSensorValues[0] > 85 or allSensorValues[1] > 85 or allSensorValues[2][1] > 900

def set_power_leds(allSensorValues):
    led_gpio.output(9, not pg.top_heat_blanket_on)
    led_gpio.output(12,not  pg.bottom_heat_blanket_on)
    led_gpio.output(2, not pg.intake_solenoid_on)
    led_gpio.output(3, not pg.exhaust_solenoid_on)
    led_gpio.output(pg.POWER_PIN, False)
    led_gpio.output(pg.PRESSURIZED_PIN, not allSensorValues[2][1] > 100)
    led_gpio.output(pg.AUX_1_PIN, not(allSensorValues[0] > 30 or allSensorValues[1] > 30))

def set_relays():
    digital_input_values.output(0, pg.top_heat_blanket_on)
    digital_input_values.output(1, pg.bottom_heat_blanket_on)
    digital_input_values.output(2, pg.intake_solenoid_on)
    digital_input_values.output(3, pg.exhaust_solenoid_on)

@atexit.register
def gracefulShutdown():
    print "Graceful Shutdown initialized"
    for i in range(0, 16):
        led_gpio.output(i, GPIO.HIGH)  # True is HIGH is OFF, False is LOW is ON
    led_gpio.output(5, GPIO.LOW)
    lcd.clear()
    lcd.set_color(1,1,1)
    #currentStateObject.exit(allSensorValues, lcd, led_gpio) # need to find these
    #turn off relays
    for i in range(0,4):
        digital_input_values.output(i, GPIO.LOW)

sensorProblem = False
inputProblem = False

(sensor, sensor2, analog_input_values, digital_input_values, lcd, led_gpio)= setup_pins()
keepGoing = True
led_gpio.output(5, GPIO.HIGH)

define("port", default=8080, help="run on the given port", type=int)

clients = []
class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print 'new connection'
        clients.append(self)
        self.write_message("connected")

    def on_message(self, message):
        print 'tornado received from client: %s' % message
        self.write_message('got it!')
        q = self.application.settings.get('queue')
        q.put(message)

    def on_close(self):
        print 'connection closed'
        clients.remove(self)

# instantiate our state classes once so they can persist data without going static/global
manual_state = ManualState()
automatic_state = AutomaticState()
config_state = ConfigState()

class SerialProcess(multiprocessing.Process):

    def __init__(self, taskQ, resultQ):
        multiprocessing.Process.__init__(self)
        self.taskQ = taskQ
        self.resultQ = resultQ
        self.keepGoing = True
        self.currentStateObject = ManualState()
        self.requestedStateObject = ManualState()

    def close(self):
        pass

    def run(self):
        start_time = time.time()
        while self.keepGoing:
            try:
                if not self.taskQ.empty():
                    task = self.taskQ.get()
                    print "incoming message: " + task
                time.sleep(1.0)
                print(chr(27) + "[2J") # clears console
                allSensorValues = get_sensor_values(sensor, sensor2, analog_input_values, digital_input_values)
                print allSensorValues[0]
                print allSensorValues[1]
                print allSensorValues[2]
                print allSensorValues[3]
                if is_there_a_sensor_problem(allSensorValues):
                    # TODO...
                    pass

                update_input_values(allSensorValues[3])

                if pg.manual_mode:
                    self.requestedStateObject = manual_state
                if pg.auto_mode:
                    self.requestedStateObject = automatic_state
                if pg.config_mode:
                    self.requestedStateObject = config_state

                if self.currentStateObject != self.requestedStateObject:
                    if self.currentStateObject.exit(allSensorValues, lcd, led_gpio):
                        self.requestedStateObject.enter(allSensorValues, lcd, led_gpio)
                        self.currentStateObject = self.requestedStateObject
                else:
                    self.currentStateObject.in_state(allSensorValues, lcd, led_gpio)

                set_power_leds(allSensorValues)
                set_relays()
                self.resultQ.put({ "time": time.time() - start_time,
                                            "top_temp":allSensorValues[0],
                                            "bottom_temp":allSensorValues[1],
                                            "pressure":allSensorValues[2][3]/10.})

            except Exception as e:
                print(e)
                self.keepGoing = False
                lcd.message("Fatal Error.")
                led_gpio.output(pg.ERROR_PIN, GPIO.LOW)






################################ MAIN ################################

def main():
    taskQ = multiprocessing.Queue()
    resultQ = multiprocessing.Queue()

    sp = SerialProcess(taskQ, resultQ)
    sp.daemon = True
    sp.start()

    # wait a second before sending first task
    time.sleep(1)
    taskQ.put("first task")

    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers=[
            (r"/", IndexHandler),
            (r"/ws", WebSocketHandler)
        ], queue=taskQ
    )
    httpServer = tornado.httpserver.HTTPServer(app)
    httpServer.listen(options.port)
    print "Listening on port:", options.port

    def checkResults():
        if not resultQ.empty():
            result = resultQ.get()
            for c in clients:
                c.write_message(result)

    mainLoop = tornado.ioloop.IOLoop.instance()
    scheduler = tornado.ioloop.PeriodicCallback(checkResults, 10, io_loop=mainLoop)
    scheduler.start()
    mainLoop.start()


if __name__ == "__main__":
    main()
