import time
import pps_tools
import threading
import os, csv

class pps_stats:
    pp = __name__ + ".pps_stats "
    def __init__(self): 
        print(pps_stats.pp + "init.")
        with pps_tools.PpsFile("/dev/pps0") as ppsf:
            capabilities = ppsf.get_cap()
            print(pps_tools.data.cap_to_dict(capabilities))

            params = ppsf.get_params()
            params['mode'] = pps_tools.data.PPS_CAPTUREASSERT
            ppsf.set_params(**params)

            edge = ppsf.fetch(timeout=None)
            print(edge)

    def __del__(self): 
        print(pps_stats.pp + "delete.")

class chrony_stats:    
    pp = __name__ + ".chrony_stats "
    def __init__(self,interval=5.0):        
        print(chrony_stats.pp + "init.")

        self.interval = interval

        # internals
        self.version = "1.0.0"
        self.last_update    = None
        self.last_tracking  = None
        self.last_sources   = None

        # stats
        self.root_distance  = None
        self.source         = None
        self.sys_time_off   = None
        self.rms_time_off   = None
        self.stratum        = None

        # threads
        self.thread_chronyc = threading.Thread(target=self.chrony_thfn,args=("chrony_thread",self.interval,),daemon=True)

        self.thread_chronyc.start()
    
    def __del__(self):
        print(chrony_stats.pp + "delete.")

    def chrony_thfn(self,name,interval):
        print(chrony_stats.pp + name + " start.")

        while 1:
            time.sleep(interval)

            stream = os.popen("chronyc -c tracking")
            self.last_tracking = list(csv.reader(stream))
            stream.close()
            stream = os.popen("chronyc -c sources")
            self.last_sources = list(csv.reader(stream))
            stream.close()

            # source
            source_found = False
            for row in self.last_sources:
                if row[1] == '*':
                    self.source = row[2]
                    source_found = True
            if source_found == False:
                self.source = "Not found"

            # root distance
            self.root_distance = float(self.last_tracking[0][10])/2.0 + float(self.last_tracking[0][11])

            # stratum
            self.stratum       = int(self.last_tracking[0][2])

            # sys time offset
            self.sys_time_off  = float(self.last_tracking[0][4])

            # rms offset
            self.rms_time_off  = float(self.last_tracking[0][6])
        
        print(chrony_stats.pp + name + " end.")
