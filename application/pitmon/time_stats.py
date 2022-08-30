import time
import threading
import os, csv
from .pps import pps_tools

class pps_stats:
    pp = __name__ + ".pps_stats "
    callback = None
    def __init__(self): 
        print(pps_stats.pp + "init.")

        # threads
        self.thread_pps = threading.Thread(target=self.pps_thfn,args=("pps_thread",),daemon=True)

        self.thread_pps.start()


    def __del__(self): 
        print(pps_stats.pp + "delete.")

    def addPpsCallback(self,cb):
        self.callback = cb

    def pps_thfn(self,name):        
        print(pps_stats.pp + name + " start.")

        with pps_tools.PpsFile("/dev/pps0") as ppsf:
            # capabilities = ppsf.get_cap()
            # print(pps_tools.data.cap_to_dict(capabilities))

            params = ppsf.get_params()
            params['mode'] = pps_tools.data.PPS_CAPTUREASSERT
            ppsf.set_params(**params)
            while 1:
                edge = ppsf.fetch(timeout=None)
                # print(edge)
                if self.callback != None:
                    self.callback(float(edge.get('assert_time')))

        print(pps_stats.pp + name + " end.")


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
        self.root_distance  = 0.0
        self.source         = "not set"
        self.sys_time_off   = 0.0
        self.rms_time_off   = 0.0
        self.stratum        = 9

        # threads
        self.thread_chronyc = threading.Thread(target=self.chrony_thfn,args=("chrony_thread",self.interval,),daemon=True)

        self.thread_chronyc.start()
    
    def __del__(self):
        print(chrony_stats.pp + "delete.")

    def chrony_thfn(self,name,interval):
        print(chrony_stats.pp + name + " start.")

        while 1:

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
            
            time.sleep(interval)
        
        print(chrony_stats.pp + name + " end.")
