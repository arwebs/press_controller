# press_controller
Control logic for ski press.  Includes a poor-man's PID along with ability to configure and monitor a run.  Pressing is dangerous!  This software is designed to work with pressure vessels which should they fail could kill you and cause a lot of damage.  Use at your own risk and only with a full understanding of what could go wrong.
## Devices
* Raspberry Pi
* Custom PCB
  * Contains GPIO Expansion chips & A2D converter
* Solid State Relays
* Solenoid valves
## Physical Inputs
* Temperature Sensors -- top and bottom heat blanket
  * Optically isolated from the rest of the board
  * Use SPI protocol
* Pressure Sensor -- monitor air bladder pressure
  * Input from A2D converter
* Pots
  * Used for manually setting configuration
  * Input from A2D converter
* Selector Switches
  * Used for manually setting configuration, starting/stopping runs, overriding relay positions
## Physical Outputs
* 4x20 Character LCD -- display status 
* 16 LEDs -- also display status
* Solid State Relays -- control heat blankets and solenoids for air bladders
