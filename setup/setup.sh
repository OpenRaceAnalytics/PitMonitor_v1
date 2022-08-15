#!/bin/bash

#MIT License
#
#Copyright (c) 2022 aXe
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

debug=false

echo "[...---... OpenRaceAnalytics - PitMonitor v1 Install ...---...] ....apt update...."
sudo apt-get update

chmod +x ./common/*.sh

if [ $debug == false ]; then
  echo "[...---... OpenRaceAnalytics - PitMonitor v1 Install ...---...] ....apt upgrade...."
  sudo apt-get full-upgrade -y

  echo "[...---... OpenRaceAnalytics - PitMonitor v1 Install ...---...] .... install tools ...."
  ./common/tools_install.sh

  echo "[...---... OpenRaceAnalytics - PitMonitor v1 Install ...---...] .... install gpsd ...."
  ./common/gpsd_install.sh  

  echo "[...---... OpenRaceAnalytics - PitMonitor v1 Install ...---...] .... configure gpsd ...."
  # Crontab
  line="@reboot sudo stty -F /dev/ttyS0 115200"
  (crontab -u $(whoami) -l; echo "$line" ) | crontab -u $(whoami) -
  sudo stty -F /dev/ttyS0 115200
  # gpsd config
  sudo sed -i '/DEVICES=\"\"/ c\DEVICES=\"/dev/ttyS0\"' /etc/default/gpsd
  # pps config
  if ! grep -q "# GPSD and PPS config" /boot/config.txt; then
    echo '# GPSD and PPS config' | sudo tee -a /boot/config.txt
    # echo 'enable_uart=1' | sudo tee -a /boot/config.txt
    echo 'init_uart_baud=115200' | sudo tee -a /boot/config.txt
    echo 'dtoverlay=pps-gpio,gpiopin=5' | sudo tee -a /boot/config.txt
  fi

  echo "[...---... OpenRaceAnalytics - PitMonitor v1 Install ...---...] .... restart gpsd ...."
  ./common/gpsd_restart.sh

  echo "[...---... OpenRaceAnalytics - PitMonitor v1 Install ...---...] .... install go ...."
  wget https://go.dev/dl/go1.19.linux-armv6l.tar.gz
  sudo tar -C /usr/local -xzf go1.19.linux-armv6l.tar.gz
  rm go1.19.linux-armv6l.tar.gz
  ./common/go_install.sh

  echo "[...---... OpenRaceAnalytics - PitMonitor v1 Install ...---...] .... install mqtt ...."
  ./common/mqtt_install.sh
  #./common/mqtt_benchmark_install.sh

  echo "[...---... OpenRaceAnalytics - PitMonitor v1 Install ...---...] .... install pyLoRa ...."
  ./common/pyLora_install.sh

  echo "[...---... OpenRaceAnalytics - PitMonitor v1 Install ...---...] .... install ssh1106 ...."
  ./common/sh1106_install.sh

  line="@reboot python3 /home/axe/ssh1106/display.py &"
  (crontab -u $(whoami) -l; echo "$line" ) | crontab -u $(whoami) -
  #python3 /home/axe/ssh1106/display.py &

  echo "[...---... OpenRaceAnalytics - PitMonitor v1 Install ...---...] .... install rtc ...."
  ./common/ds3231_install.sh

  echo "[...---... OpenRaceAnalytics - PitMonitor v1 Install ...---...] .... install can ...."
  ./common/can_install.sh

  echo "[...---... OpenRaceAnalytics - PitMonitor v1 Install ...---...] .... install can ...."
  ./common/ads1115_install.sh

  echo "[...---... OpenRaceAnalytics - PitMonitor v1 Install ...---...] .... disable swap ...."
  ./common/disable_swap.sh
fi

if [ $debug == true ]; then
  echo "[...---... OpenRaceAnalytics - PitMonitor v1 Install ...---...] .... dummy ...."

fi

if [ $debug == false ]; then
  echo "[...---... OpenRaceAnalytics - PitMonitor v1 Install ...---...] .... cleanup ...."
  sudo rm -rf tmp
  sudo apt-get update
  sudo apt-get upgrade -y
  sudo apt-get autoremove -y
fi
