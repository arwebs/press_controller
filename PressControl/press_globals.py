def init():
    global start_button, stop_button, auto_mode, manual_mode, config_mode, top_heat_blanket_off, top_heat_blanket_auto, top_heat_blanket_on
    global bottom_heat_blanket_off, bottom_heat_blanket_auto, bottom_heat_blanket_on, intake_solenoid_off, intake_solenoid_auto, intake_solenoid_on
    global exhaust_solenoid_off, exhaust_solenoid_auto, exhaust_solenoid_on

    start_button = False
    stop_button = False
    auto_mode = True
    manual_mode = False
    config_mode = False
    top_heat_blanket_off = False
    top_heat_blanket_auto = True
    top_heat_blanket_on = False
    bottom_heat_blanket_off = False
    bottom_heat_blanket_auto = True
    bottom_heat_blanket_on = False
    intake_solenoid_off = False
    intake_solenoid_auto = True
    intake_solenoid_on = False
    exhaust_solenoid_off = False
    exhaust_solenoid_auto = True
    exhaust_solenoid_on = False