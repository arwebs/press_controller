system_power = True
run_in_progress = False
system_pressurized = False
system_fault = False
configuration_mode_active = False
manual_mode_active = False
top_heat_blanket_status = False
bottom_heat_blanket_status = False
intake_solenoid_status = False
exhaust_solenoid_status = False
top_heat_blanket_cold = False
top_heat_blanket_on_target = False
top_heat_blanket_hot = False
bottom_heat_blanket_cold = False
bottom_heat_blanket_on_target = False
bottom_heat_blanket_hot = False

def set_outputs():
    global system_power, run_in_progress,system_pressurized, system_fault, configuration_mode_active
    global  manual_mode_active, top_heat_blanket_status, bottom_heat_blanket_status, intake_solenoid_status
    global exhaust_solenoid_status, top_heat_blanket_cold, top_heat_blanket_on_target, top_heat_blanket_hot
    global bottom_heat_blanket_cold, bottom_heat_blanket_on_target, bottom_heat_blanket_hot

    return [not system_power, not run_in_progress, not system_pressurized, not system_fault, not configuration_mode_active,
            not manual_mode_active, not top_heat_blanket_status, not bottom_heat_blanket_status, not intake_solenoid_status,
            not exhaust_solenoid_status, not top_heat_blanket_cold, not top_heat_blanket_on_target, not top_heat_blanket_hot,
            not bottom_heat_blanket_cold, not bottom_heat_blanket_on_target, not bottom_heat_blanket_hot]