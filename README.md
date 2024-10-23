# logmonitor - log file monitor
Python script, that monitors a given log file for a RegExp and if found sends a Telegram message. It is not aimed to be fast and reliable, it is just a simple script. 

## Client:
It is the simple hack to get info about my garage door open - as my garage is too far from WiFi, NRF24 signal from my home. I installed a simple magnetic sensor like [Botland](https://botland.store/magnetic-sensors/3104-magnetic-sensor-to-open-door-window-reed-contact-cmd14-screws-5904422366247.html), plug it in Meshtastic powered ESP32 device in the garage and set up the detection via [Meshtastic detection](https://meshtastic.org/docs/configuration/module/detection-sensor/). With the detection settings you can use a keyword for the alarm (like: OpenGarageSOMETHING)



## Server: 
Now it gets trickier. The Meshtastic (Helltec) device in my home was set up to log via syslog. Syslog server runs on my home server, I needed to scan the Meshtastic log (Router.log) for a keyword (OpenGarageSOMETHING) and when found, use it for a Telegram message. The simple python code [logmonitor.py](https://github.com/cubapp/logmonitor/blob/main/logmonitor.py) does it. In order to run it on the server (Debian 12.x) you need to start the script as a service via systemctl - hence the [logmonitor.service](https://github.com/cubapp/logmonitor/blob/main/logmonitor.service)

Do not forget to add and run the service:
```
sudo systemctl daemon-reload
sudo systemctl enable logmonitor
sudo systemctl start logmonitor
```

and check the log files:
```
journalctl -u logmonitor.service
#or
less /opt/logmonitor/alarm_log.txt

```


### Rsyslog settings:
To log data from different IPs or hostnames into the corresponding directories, you can set up the rsyslog this way:

```
$template remote-incoming-logs,"/var/log/%HOSTNAME%/%PROGRAMNAME%.log"
*.* ?remote-incoming-logs
& stop
```

It is not recommended settings, but somehow works for me. 

