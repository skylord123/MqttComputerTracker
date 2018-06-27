# MqttComputerTracker
Track idle time on a computer over MQTT.

I created this application so I could track whether either of the computers in my home office were in use. I have a motion sensor in the office and this works pretty well but if you hold still for a couple minutes the lights will turn off. This was my way to get around that.

This program just publishes how many seconds have passed since the mouse or keyboard has been used. I use it with Home Assitant & Node-Red.


## How to use
Copy the project to your local machine. Copy the config.ini.default file to config.ini and change the options inside to match your setup. Once everything is setup you can run tracker.py

## Contributing
Feel free to open any Pull Requests. I am open to the idea of this project being able to do more things like checking if the PC is locked.

## To Do
- Update the readme with more documentation.
- Update code to track if the PC is locked or not
- Possibly track PC temps