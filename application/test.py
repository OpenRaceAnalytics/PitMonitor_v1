from pitmon import mqtt_stats, gpsd_stats, time_stats
import time

time.sleep(1)

mqtt_stat   = mqtt_stats.mqtt_stats()
gpsd_stat   = gpsd_stats.gpsd_stats()
chrony_stat = time_stats.chrony_stats()
pps_stat    = time_stats.pps_stats()

f = open("/home/ora/logfile.log","a")
f.write("Log started at %s\n" % str(time.time()))

def callback_pps(timestamp):
    print("Callback hit with delay : %3.2f us" % (1e6*(time.time()-timestamp)))
    now=time.time()
    f.write("PPS    Log Entry %0.6f: Timestamp: %0.6f Delay: %0.6f\n" % (now,timestamp,now-timestamp))
    f.write("Chrony SRC: %s Stratum: %u Root Dist: %0.9f Offset: %0.9f RMS: %0.9f\n" % (chrony_stat.source,chrony_stat.stratum,chrony_stat.root_distance,chrony_stat.sys_time_off,chrony_stat.rms_time_off))
    f.write("MQTT   RxM: %u Uptime: %u AliveMaxDelay %0.6f\n" % (mqtt_stat.msgs_received,mqtt_stat.host_uptime,mqtt_stat.alive_max_delay))
    f.write("GPSD   RxM: %u Sats: %s Mode: %s Status: %s\n" % (gpsd_stat.msgs_received,gpsd_stat.getSats(),gpsd_stat.getMode(),gpsd_stat.getStatus()))
    f.flush()

pps_stat.addPpsCallback(callback_pps)

time.sleep(60)

f.close()