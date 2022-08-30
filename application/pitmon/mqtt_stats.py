from xml.etree.ElementTree import TreeBuilder
import paho.mqtt.client as mqtt
import time
import threading
import random

class mqtt_stats:
    def __init__(self, host='localhost', port=1883,client_id_prefix='mqtt_stats',keepalive=5):
        self.host               = host
        self.port               = port
        self.keepalive          = keepalive
        self.client_id          = client_id_prefix + '#' + str(random.randint(0,0xFFFF))
        self.client             = mqtt.Client(client_id=self.client_id)
        
        # internals      
        self.version        = "1.0.0"
        self.isConnected    = False
        self.isTimedOut     = False  
        self.isAlive        = False
        self.msg_last_rx    = 0.0
        self.msg_max_delta  = 0.0
        self.msgs_received  = 0
        self.host_uptime    = 0
        self.host_server    = ""
        self.host_version   = ""
        self.alive_msg      = ""
        self.alive_msg_rx   = ""
        self.alive_time     = 0.0
        self.alive_max_delay= 0.0
        self.alive_topic    = "client/connection/" + str(client_id_prefix) + "/heartbeat"

        # threads
        self.timeout_thread     = threading.Thread(target=self.timeout_detect_thfn,args=("timeout_thread",15.0,),daemon=True)
        self.heartbeat_thread   = threading.Thread(target=self.heartbeat_thfn,args=("heartbeat_thread",self.alive_topic,2.0,2.0,),daemon=True)

        # debug
        print(__name__ + ".client id:" + self.client_id)

        # callbacks
        self.client.on_message      = self.on_message
        self.client.on_connect      = self.on_connect
        self.client.on_disconnect   = self.on_disconnect

        # connect and loop start
        self.client.connect(host=self.host,port=self.port,keepalive=self.keepalive)
        self.client.loop_start()

        # start internal threads
        self.timeout_thread.start()
        self.heartbeat_thread.start()

        self.client.subscribe("$SYS/broker/#")
        self.client.subscribe(self.alive_topic)
    
    def __del__(self):
        self.client.disconnect()
        self.client.loop_stop()

    def timeout_detect_thfn(self,name,timeout):
        # init
        self.isTimedOut = True
        while self.msg_last_rx == 0:
            time.sleep(0.1)

        # do monitoring
        while 1:
            now = time.time()
            if now - self.msg_last_rx > timeout:
                print(__name__ + ".client timeout detected, max: " + str(timeout) + " current: " + str(now-self.msg_last_rx))
                self.isTimedOut = True
            else:
                self.isTimedOut = False
            time.sleep(timeout/10)

    def heartbeat_thfn(self,name,topic,interval,timeout):
        # init
        iteration = 0
        self.isAlive = False

        #do monitoring
        while 1:
            time.sleep(interval)
            self.alive_msg = self.client_id + ' heartbeat #' + str(iteration)
            self.alive_time = 0.0
            self.alive_msg_rx = ""
            iteration += 1
            alive = False
            self.client.publish(topic,self.alive_msg)            
            tsStart = time.time()
            while time.time() - tsStart < timeout:
                if self.alive_time != 0:
                    if self.alive_msg == self.alive_msg_rx:
                        alive = True
                        if self.alive_time - tsStart > self.alive_max_delay:
                            self.alive_max_delay = self.alive_time - tsStart
                    else:
                        print(__name__ + ".client alive msg missmatch")
                    break
                time.sleep(0.1)
            if alive == False:
                print(__name__ + ".client heartbeat timed out")
            self.isAlive = alive
    

    def on_connect(self,client, userdata, flags, rc):
        if rc == 0 and client.is_connected() == True:
            self.isConnected = self.client.is_connected()
            print(__name__ + ".client is connected")
        else:
            self.isConnected = False
            print(__name__ + ".client connection failed. result: " + str(rc))

    def on_disconnect(self, client, userdata, rc):
        self.isConnected = False
        print(__name__ + ".client disconnected unexpectetly. result: " + str(rc))

    def on_message(self, client, userdata, message):
        self.msgs_received += 1

        now = time.time()
        # update max delta time
        if self.msg_last_rx != 0.0:
            if now - self.msg_last_rx > self.msg_max_delta:
                self.msg_max_delta = now- self.msg_last_rx

        # update last received time
        self.msg_last_rx = now
        
        data = str(message.payload.decode("utf-8"))
        if message.topic == self.alive_topic:
            self.alive_time     = now
            self.alive_msg_rx   = data
        if message.topic == "$SYS/broker/uptime":
            split = data.split(' ',1)
            self.host_uptime = int(split[0])
        if message.topic == "$SYS/broker/version":
            split = data.split(' ',2)
            self.host_server  = split[0]
            self.host_version = split[2]
