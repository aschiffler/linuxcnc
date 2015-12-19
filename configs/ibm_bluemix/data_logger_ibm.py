import glib
import time
import gobject
import hal
import linuxcnc
import time
import client as mqtt
import json
import uuid
import logging

class HandlerClass:

    def __init__(self, halcomp,builder,useropts):
        self.halcomp = halcomp
	self.halcomp.newpin("logger_beat", hal.HAL_BIT, hal.HAL_OUT)
	self.halcomp.newpin("logger_11", hal.HAL_FLOAT, hal.HAL_IN)
	self.halcomp.newpin("logger_12", hal.HAL_FLOAT, hal.HAL_IN)
	self.halcomp.newpin("logger_13", hal.HAL_FLOAT, hal.HAL_IN)
	self.halcomp.newpin("logger_21", hal.HAL_FLOAT, hal.HAL_IN)
	self.halcomp.newpin("logger_22", hal.HAL_FLOAT, hal.HAL_IN)
	self.halcomp.newpin("logger_23", hal.HAL_FLOAT, hal.HAL_IN)
	self.halcomp.newpin("logger_31", hal.HAL_FLOAT, hal.HAL_IN)
	self.halcomp.newpin("logger_32", hal.HAL_FLOAT, hal.HAL_IN)
	self.halcomp.newpin("logger_33", hal.HAL_FLOAT, hal.HAL_IN)
	self.halcomp['logger_beat'] = False
        self.builder = builder
	self.emc = linuxcnc
	self.status = self.emc.stat()
	# MQTT
	self.mqttc = mqtt.Client("d:" + "hjr4ov" + ":" + "linuxcnc" + ":" + "master_mc51")
	self.mqttc.username_pw_set("use-token-auth", password="wjbNvKD4tffNF&!WbQ")
	self.mqttc.on_connect = self.on_connect
	self.mqttc.on_log = self.on_log
	self.mqttc.connect(host="hjr4ov" + ".messaging.internetofthings.ibmcloud.com", port=1883, keepalive=60)
	self.mqttc.loop_start() 

	
    def on_connect(self,mqttc, obj, flags, rc):
	gobject.timeout_add(1000, self.periodic)
	gobject.timeout_add(5000, self.periodicslow)
	self.builder.get_object('guid').set_label("rc: "+str(rc))
	self.builder.get_object('connect').set_label("Disconnect")

    def on_disconnect(self,mqttc, obj, flags, rc):
	self.mqttc.loop_stop() 
	self.builder.get_object('guid').set_label("rc: "+str(rc))
	self.builder.get_object('connect').set_label("Connect")

    def on_connect_pressed(self, widget,data=None):
	return True

    def on_log(self,mqttc, obj, level, string):
	self.builder.get_object('log').set_label(string)


    def periodic(self):
	self.status.poll()
	self.halcomp['logger_beat'] = not self.halcomp['logger_beat']
	
	msg = json.JSONEncoder().encode({"d":{
		"Pos_x[mm]":self.status.actual_position[0],
		"Pos_y[mm]":self.status.actual_position[1],
		"Pos_z[mm]":self.status.actual_position[2],
		"Strom_x[%]":self.halcomp['logger_11'],
		"Strom_y[%]":self.halcomp['logger_22'],
		"Strom_z[%]":self.halcomp['logger_33'],
		"Geschw_x[mm/s]":self.status.axis[0]['velocity'],
		"Geschw_y[mm/s]":self.status.axis[1]['velocity'],
		"Geschw_z[mm/s]":self.status.axis[2]['velocity'],
		"Spindle_speed[1/min]":self.status.spindle_speed}})
	self.mqttc.publish("iot-2/evt/status/fmt/json", payload=msg, qos=0, retain=False)

	self.builder.get_object('oalogger11').set_label("%5.2f"%(self.halcomp['logger_11']))
	self.builder.get_object('oalogger12').set_label("%5.2f"%(self.halcomp['logger_12']))
	self.builder.get_object('oalogger13').set_label("%5.2f"%(self.halcomp['logger_13']))
	self.builder.get_object('oalogger21').set_label("%5.2f"%(self.halcomp['logger_21']))
	self.builder.get_object('oalogger22').set_label("%5.2f"%(self.halcomp['logger_22']))
	self.builder.get_object('oalogger23').set_label("%5.2f"%(self.halcomp['logger_23']))
	self.builder.get_object('oalogger31').set_label("%5.2f"%(self.halcomp['logger_31']))
	self.builder.get_object('oalogger32').set_label("%5.2f"%(self.halcomp['logger_32']))
	self.builder.get_object('oalogger33').set_label("%5.2f"%(self.halcomp['logger_33']))
	return True

    def periodicslow(self):
	self.status.poll()
    	return True		


def get_handlers(halcomp,builder,useropts):
    '''
    this function is called by gladevcp at import time (when this module is passed with '-u <modname>.py')

    return a list of object instances whose methods should be connected as callback handlers
    any method whose name does not begin with an underscore ('_') is a  callback candidate

    the 'get_handlers' name is reserved - gladevcp expects it, so do not change
    '''
    return [HandlerClass(halcomp,builder,useropts)]
