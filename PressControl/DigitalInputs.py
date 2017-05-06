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
    global start_button, stop_button,auto_mode, manual_mode, config_mode, top_heat_blanket_off, top_heat_blanket_auto, top_heat_blanket_on
    global bottom_heat_blanket_off, bottom_heat_blanket_auto, bottom_heat_blanket_on, intake_solenoid_off, intake_solenoid_auto, intake_solenoid_on
    global exhaust_solenoid_off, exhaust_solenoid_auto, exhaust_solenoid_on

    start_button = not digital_input_values[4]
    stop_button = not digital_input_values[5]
    manual_mode = not digital_input_values[7]
    auto_mode = digital_input_values[6] and digital_input_values[7]
    config_mode = not digital_input_values[6]
    bottom_heat_blanket_auto = digital_input_values[14] and digital_input_values[15]
    bottom_heat_blanket_off = not digital_input_values[14]
    bottom_heat_blanket_on = not digital_input_values[15]
    top_heat_blanket_auto = digital_input_values[8] and digital_input_values[9]
    top_heat_blanket_off = not digital_input_values[8]
    top_heat_blanket_on = not digital_input_values[9]
    intake_solenoid_auto = digital_input_values[10] and digital_input_values[11]
    intake_solenoid_off = not digital_input_values[10]
    intake_solenoid_on = not digital_input_values[11]
    exhaust_solenoid_auto = digital_input_values[12] and digital_input_values[13]
    exhaust_solenoid_off = not digital_input_values[13]
    exhaust_solenoid_on = not digital_input_values[12]
