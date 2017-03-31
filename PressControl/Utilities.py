def c_to_f(c):
    return c * 9.0 / 5.0 + 32.0

class FakeLCD:
    def __init__(self):
        pass
    def clear(self):
        print 'LCD Cleared'
    def message(self,text):
        print 'LCD Text: ' + text

class FakeIO:
    def __init__(self):
        relays = 0
        leds = 0
    def get_pot_values(self):
        pass

    def get_temperature_sensor_values(self):
        pass

    def set_relay_outputs(self, relay_outputs):
        pass

    def set_led_outputs(self, led_outputs):
        pass
