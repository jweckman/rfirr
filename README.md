# rfirr - Radio signal based irrigation system used with two Raspberry Pi computers

## Description

rfirr is an irrigation application which is installed on two Raspberry Pi computers. One of them is the main computer activating the second one that is controlling the actual irrigation system. Having a setup like this allows for the use of a battery such as a moped or car battery to power the second Pi and other needed peripherals. This in turn makes it possible to have the irrigation system in a place without grid power, with the inside Pi controlling it from inside a building within ~20 meters (depends on location and radio equipment signal strength) 

## Recommended setup

Minimum requirements:
* Two raspberry pi computers with raspbian installed
* Wifi network for shared logging through samba or SSH
* 12v solenoid valve
* Canister or bucket or similar to hold water 
* 12v radio frequency relay 
* 12v regular relay
* Battery. 12V car battery recommended. For shorter use moped battery can be enough, or when coupled with solar panel
* Radio frequency sender module 
* Plastic tubes for leading water to plants
* 12v to 5v converter. Usb car charger is simple to install and works well (outside rpi needs 5v to run)
* Various plumbing and electronics related tools for cutting, soldering, taping etc.
* See-through box to put electronics and camera in. Small plastic toolbox with compartments worked well for me

Recommended additional items:
* 12v water pump, car windshield wiper pump works very well and is cheap
* Moisture sensor
* Analogue to Digital converter (ADC) for accurate moisture sensor readings 
* 2A fuse to protect outside rpi
* Camera for outside rpi for monitoring plant status

## Raspberry Pi OS level recommended tweaks
### Disable blinking LED for power saving:
Put the following commands in /etc/rc.local

echo none | sudo tee /sys/class/leds/led0/trigger
echo 1 | sudo tee /sys/class/leds/led0/brightness

### Disable WiFi power saving
WiFi power saving can cause bad connections. Disable with following line in /etc/rc.local:
/sbin/iwconfig wlan0 power off

### Disable HDMI port
HDMI port needs additional power. Disable with following line in /etc/rc.local:
/usr/bin/tvservice -o

## Usage

1. Select desired mode of operation in the config to be either dual-pi-rf or single-pi-rpc mode.
2. Copy and modify sample systemd unit file "irrigation.service" to /etc/systemd/system on the pi
3. Run: systemctl enable --now irrigation.service
4. In case using RPC, check CURL examples in rpc_examples.sh for manual operation

Running the above steps in rpc mode will also automatically run the configurabe scheduler on a separate thread. This gives the flexibility of having the scheduler and the ability to complement it with manual irrigation when needed.
