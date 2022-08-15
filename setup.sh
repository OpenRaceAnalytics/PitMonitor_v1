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
export INSTALL_LOG="/var/log/pitmon_install.log" 

if ! grep -q "# install log create." $INSTALL_LOG; then
    echo '# install log create.' | sudo tee -a $INSTALL_LOG
fi

echo "[...---... OpenRaceAnalytics - PitMonitor v1 Install ...---...] ....apt update...."
sudo apt-get update

chmod +x ./setup_common/scripts/*.sh

if [ $debug == false ]; then
  echo "[...---... OpenRaceAnalytics - PitMonitor v1 Install ...---...] ....apt upgrade...."
  sudo apt-get full-upgrade -y

  echo "[...---... OpenRaceAnalytics - PitMonitor v1 Install ...---...] .... install tools ...."
  ./setup_common/scripts/tools_install_gui.sh

  echo "[...---... OpenRaceAnalytics - PitMonitor v1 Install ...---...] .... install gpsd ...."
  ./setup_common/scripts/gpsd_install.sh  

  echo "[...---... OpenRaceAnalytics - PitMonitor v1 Install ...---...] .... configure gpsd ...."
  if ! grep -q "# configure gpsd done." $INSTALL_LOG; then
    # Chrony Timeserver 
    sudo cp -rf setup_common/files/chrony/chrony_server.conf /etc/chrony/chrony.conf
    sudo ln -s /lib/systemd/system/gpsd.service /etc/systemd/system/multi-user.target.wants/
    # Crontab
    line="@reboot sudo stty -F /dev/ttyS0 115200"
    (crontab -u $(whoami) -l; echo "$line" ) | crontab -u $(whoami) -
    sudo stty -F /dev/ttyS0 115200
    # gpsd config
    sudo sed -i '/DEVICES=\"\"/ c\DEVICES=\"/dev/ttyS0\"' /etc/default/gpsd
    # pps config
    if ! grep -q "# GPSD and PPS config" /boot/config.txt; then
      echo '# GPSD and PPS config' | sudo tee -a /boot/config.txt
      echo 'init_uart_baud=115200' | sudo tee -a /boot/config.txt
      echo 'dtoverlay=pps-gpio,gpiopin=4' | sudo tee -a /boot/config.txt
    fi

    echo "[...---... OpenRaceAnalytics - PitMonitor v1 Install ...---...] .... restart gpsd ...."
    ./setup_common/scripts/gpsd_restart.sh

    echo '# configure gpsd done.' | sudo tee -a $INSTALL_LOG
  fi

  
  echo "[...---... OpenRaceAnalytics - PitMonitor v1 Install ...---...] .... install rtc ...."
  ./setup_common/scripts/ds3231_install.sh

  echo "[...---... OpenRaceAnalytics - PitMonitor v1 Install ...---...] .... install mqtt ...."
  ./setup_common/scripts/mqtt_install.sh
  #./setup_common/scripts/mqtt_benchmark_install.sh

  echo "[...---... OpenRaceAnalytics - PitMonitor v1 Install ...---...] .... disable swap ...."
  ./setup_common/scripts/disable_swap.sh
fi

if [ $debug == true ]; then
  echo "[...---... OpenRaceAnalytics - PitMonitor v1 Install ...---...] .... dummy ...."

fi

if [ $debug == false ]; then
  echo "[...---... OpenRaceAnalytics - PitMonitor v1 Install ...---...] .... cleanup ...."
  if ! grep -q "# cleanup done." $INSTALL_LOG; then
    sudo rm -rf tmp
    sudo apt-get update
    sudo apt-get upgrade -y
    sudo apt-get autoremove -y
    sudo reboot
    echo '# cleanup done.' | sudo tee -a $INSTALL_LOG
  fi
fi
