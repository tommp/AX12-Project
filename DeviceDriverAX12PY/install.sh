#!/bin/sh

#Install crontab if it is not present
sudo apt-get install gnome-schedule

#The following lines makes a cronjob that automatically starts the python device driver scipt on reboot
#Write out current crontab
crontab -l > tmpcron
#echo new cron into cron file
echo "@reboot sh /home/pi/EIT/DeviceDriverAX12PY/startup.py" >> tmpcron
#Install new cron file
sudo crontab -e mycron
#Delete temp
rm mycron

#Starts the driver
sh startup.sh