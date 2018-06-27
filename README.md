# MqttComputerTracker
Track idle time on a computer over MQTT.

NOTE: This was built for Windows but may work for Linux just fine. Feel free to test this and report back.

I created this application so I could track whether either of the computers in my home office were in use. I have a motion sensor in the office and this works pretty well but if you hold still for a couple minutes the lights will turn off. This was my way to get around that.

This program just publishes how many seconds have passed since the mouse or keyboard has been used. I use it with Home Assitant & Node-Red.


## How to use
Copy the project to your local machine. Copy the config.ini.default file to config.ini and change the options inside to match your setup. Once everything is setup you can run tracker.py

## Configuration

### Example
Check out the example [config.ini.default](config.ini.default) to see how to format your own config.ini file.

###Options Examplained:

`Host` - Host of the MQTT server

`port` - Port of the MQTT server

`id` - ID to assign the client when connecting

`status_channel` - Not in use currently but will publish `away` or `active` in the future.

`last_active_channel` - Channel to publish how many seconds have passed since the mouse or keyboard has been in use.

## Contributing
Feel free to open any Pull Requests or any Issues.

## Compiling to exe

You can compile this into an executablea so it doesn't require Python to be installed. 

I used PyInstaller with this command (you  can user other alternatives as well)
```
pyinstaller ./MqttComputerTracker.py --onefile --noconsol
```
`--onefile` generates just the exe

`--noconsol` runs the program without console

## To Do
- Update the readme with more documentation (list out the dependencies required to install)
- Update code to track if the PC is locked or not
- Possibly track PC temps