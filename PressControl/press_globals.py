def init():
    global start_button, stop_button, auto_mode, manual_mode, config_mode, top_heat_blanket_off, top_heat_blanket_auto, top_heat_blanket_on
    global bottom_heat_blanket_off, bottom_heat_blanket_auto, bottom_heat_blanket_on, intake_solenoid_off, intake_solenoid_auto, intake_solenoid_on
    global exhaust_solenoid_off, exhaust_solenoid_auto, exhaust_solenoid_on
    global total_run_duration, top_rampup_time, bottom_rampup_time, top_max_temp, bottom_max_temp, target_pressure
    global POWER_PIN, PRESSURIZED_PIN,RUN_IN_PROGRESS_PIN,ERROR_PIN,AUX_1_PIN,AUX_2_PIN,TOP_BLANKET_ON_PIN,BOTTOM_BLANKET_ON_PIN,INTAKE_SOLENOID_ON_PIN,EXHAUST_SOLENOID_ON_PIN,TOP_HOT_PIN,TOP_COLD_PIN,TOP_GOOD_PIN,BOTTOM_HOT_PIN,BOTTOM_COLD_PIN,BOTTOM_GOOD_PIN


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
    total_run_duration = 40. * 60.
    top_rampup_time = 20 * 60.
    bottom_rampup_time = 20. * 60.
    top_max_temp = 80.
    bottom_max_temp = 80.
    target_pressure = 80

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