# OpenRaceAnalytics - PitMonitor v1
Pi 4 based Pit Monitor and Control Base

# HW
- Raspberry Pi 4 B
- 7" official Touchscrenn + Case (DSI -> DSI; GPIO 2 SDA -> TS SDA; GPIO 3 SCL -> TS SCL)
- GPS with PPS (GPIO 14 TX -> GPS RX; GPIO 15 RX -> GPS TX; GPIO 4 -> PPS; 5V; GND)
- RTC DS3231 (GPIO 2 SDA -> RTC SDA; GPIO 3 SCL -> RTC SCL)
- PoE Shield (optional)

# ORA Class C Network config
IP-V4: 222.111.222.0
Subnet: 255.255.255.0
CIDR: 222.111.222.0/24

# SW
- Based on Raspberry PI OS 64
- Setup with Raspberry PI Imager
    - Hostname: ora-pitmon.local
    - User: ora
- IPV4: 222.111.222.10/24

# Install
- git clone https://github.com/OpenRaceAnalytics/PitMonitor_v1.git --recurse-submodule
- chmod +x setup.sh
