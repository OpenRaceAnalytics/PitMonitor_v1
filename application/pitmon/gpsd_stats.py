from gpsdclient import GPSDClient
import time
import threading

pp = __name__ + ".gpsd_stats "

modes = ['unknown','no fix','2D','3D']
stati = ['Unknown','Normal','DGPS','RTK fixed','RTK floating','DR','GNSSDR','Time (surveyed)','Simulated','P(Y)']

class gpsd_stats:

    def __init__(self,hostname='localhost'):
        print(pp + "init.")
        self.hostname = hostname
        self.client = GPSDClient(host=self.hostname)

        # internal
        self.last_tpv       = None
        self.last_sky       = None
        # stats
        self.version        = "1.0.0"
        self.sky_update     = 0.0
        self.nSats          = 0
        self.uSats          = 0
        self.tpv_update     = 0.0
        self.lat            = 0.0
        self.lon            = 0.0
        self.alt            = 0.0
        self.speed          = 0.0
        self.mode           = 0
        self.status         = 0
        self.msgs_received  = 0

        # threads
        self.thread_gpsd = threading.Thread(target=self.gpsd_thfn,args=("gpsd_thread",),daemon=True)

        self.thread_gpsd.start()
        
    def __del__(self):
        print(pp + "delete.")

    def getMode(self,num=None):
        if num == None:
            return modes[self.mode]
        elif num >= 0 and num < len(modes):
            return modes[num]
        else:   
            return "Error mode out of range"
            
    def getStatus(self,num=None):
        if num == None:
            return stati[self.status]
        elif num >= 0 and num < len(stati):
            return stati[num]
        else:   
            return "Error status out of range"

    def getSats(self):
        return str(self.uSats) + '/' + str(self.nSats)
        

    def gpsd_thfn(self,name):
        print(pp + name + " start.")

        for result in self.client.dict_stream():
            self.msgs_received += 1
            if result["class"] == "SKY":
                self.sky_update = time.time()
                self.last_sky = result
                self.nSats = int(result.get("nSat"))
                self.uSats = int(result.get("uSat"))
            elif result["class"] == "TPV":
                self.tpv_update = time.time()
                self.last_tpv = result
                self.lat    = float(result.get("lat"))
                self.lon    = float(result.get("lon"))                
                self.alt    = float(result.get("alt"))
                self.speed  = float(result.get("speed"))
                self.mode   = int(result.get("mode"))
                self.status = int(result.get("status"))
            elif result["class"] == "VERSION":
                pass
            elif result["class"] == "DEVICES":
                pass
            elif result["class"] == "WATCH":
                pass
            else:
                print(result)

        print(pp + name + " end.")
