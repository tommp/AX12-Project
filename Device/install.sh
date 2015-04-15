#!/bin/bash

#Install crontab if it is not present
sudo apt-get --assume-yes install gnome-schedule
sudo apt-get --assume-yes install network-manager-gnome
sudo apt-get --assume-yes install wpasupplicant

sudo /etc/init.d/dbus restart

#The following lines makes a cronjob that automatically starts the python device driver scipt on reboot
#Write out current crontab
crontab -l > tmpcron
#echo new cron into cron file
echo "@reboot sh /home/pi/EIT/Device/startup.py >/home/pi/logs/cronlog 2>&1" >> tmpcron
#Install new cron file
sudo crontab -e mycron
#Delete temp
rm mycron

#Enable cronjobs on startup
update-rc.d cron defaults

chmod 755 startup.sh

cd /

mkdir logs