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
## Getting Started
To run on a fresh install of Raspbian:
```sudo apt-get update
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install git build-essential python-dev python-pip python-smbus git
sudo pip install RPi.GPIO

    cd ~
    git clone https://github.com/adafruit/Adafruit_Python_CharLCD.git
    git clone https://github.com/adafruit/Adafruit_Python_MAX31855.git
    git clone https://github.com/adafruit/Adafruit_Python_MCP3008.git
    cd Adafruit_Python_CharLCD
    sudo python setup.py install
    cd ../Adafruit_Python_MAX31855
    sudo python setup.py install
    cd ../Adafruit_Python_MCP3008
    sudo python setup.py install
```
