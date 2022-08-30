from pitmon import mqtt_stats, gpsd_stats, time_stats
import time

mqtt_stat   = mqtt_stats.mqtt_stats()
gpsd_stat   = gpsd_stats.gpsd_stats()
chrony_stat = time_stats.chrony_stats()
pps_stat    = time_stats.pps_stats()

time.sleep(30)
print(mqtt_stat.msgs_received)
print(mqtt_stat.host_uptime)
# print(mqtt_stat.host_server)
# print(mqtt_stat.host_version)
print(mqtt_stat.msg_max_delta)
print(mqtt_stat.alive_max_delay)
print(gpsd_stat.getMode())
print(gpsd_stat.getStatus())
print(gpsd_stat.getSats())
print(gpsd_stat.msgs_received)
time.sleep(5)