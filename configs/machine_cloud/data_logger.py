import glib
import time
import gobject

import hal
import logging
import splunklib.client as client
import linuxcnc



class HandlerClass:

    def on_button_press(self,widget,data=None):
        self.nhits += 1
        self.builder.get_object('hits').set_label("Hits: %d" % (self.nhits))

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
        self.nhits = 0
	self.emc = linuxcnc
	self.status = self.emc.stat()

	service = client.connect(host='localhost',port=8089,username='admin',password='changeme')
	content = service.info
	builder.get_object('guid').set_label("%s: %s" % ('guid', content['guid']))
	builder.get_object('mode').set_label("%s: %s" % ('mode', content['mode']))
	builder.get_object('licenseState').set_label("%s: %s" % ('licenseState', content['licenseState']))
	service.logout()

	machinebook = logging.getLogger('Linuxcnc')
	machinebook.propagate = False
	machinebook.setLevel(logging.DEBUG)
	fh = logging.FileHandler('machinebook.log')
	formatter = logging.Formatter('%(asctime)s|%(name)s|%(levelname)s|%(message)s')
	fh.setFormatter(formatter)
	machinebook.addHandler(fh)
	self.machinebook = machinebook

	gobject.timeout_add(1000, self.periodic)
	gobject.timeout_add(6000, self.periodicslow)
	

    def periodic(self):
	self.status.poll()
	self.halcomp['logger_beat'] = not self.halcomp['logger_beat']
	message = ""
	message = message +"%5.2f"%(self.status.actual_position[0]) + "|"
	message = message +"%5.2f"%(self.status.actual_position[1]) + "|"
	message = message +"%5.2f"%(self.status.actual_position[2]) + "|"
	message = message +"%5.2f"%(self.status.axis[0]['velocity']) + "|"
	message = message +"%5.2f"%(self.status.axis[1]['velocity']) + "|"
	message = message +"%5.2f"%(self.status.axis[2]['velocity']) + "|"
	message = message +"%5.2f"%(self.status.ain[0]) + "|"
	message = message +"%5.2f"%(self.status.ain[1]) + "|"
	message = message +"%5.2f"%(self.status.ain[2]) + "|"
	self.machinebook.debug(message)
	message = ""
	message = message +"%5.2f"%(self.halcomp['logger_11']) + "|"
	message = message +"%5.2f"%(self.halcomp['logger_12']) + "|"
	message = message +"%5.2f"%(self.halcomp['logger_13']) + "|"
	message = message +"%5.2f"%(self.halcomp['logger_21']) + "|"
	message = message +"%5.2f"%(self.halcomp['logger_22']) + "|"
	message = message +"%5.2f"%(self.halcomp['logger_23']) + "|"
	message = message +"%5.2f"%(self.halcomp['logger_31']) + "|"
	message = message +"%5.2f"%(self.halcomp['logger_32']) + "|"
	message = message +"%5.2f"%(self.halcomp['logger_33']) + "|"
	self.machinebook.warn(message)
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
	self.machinebook.info(self.status.file+"|NC-Line: {0}".format(self.status.motion_line)+"|task_mode {0}".format(self.status.task_mode)+"|task_state {0}".format(self.status.task_state)+"|spindle_enabled {0}".format(self.status.spindle_enabled)+"|spindle_speed {0}".format(self.status.spindle_speed))
    	return True		


def get_handlers(halcomp,builder,useropts):
    '''
    this function is called by gladevcp at import time (when this module is passed with '-u <modname>.py')

    return a list of object instances whose methods should be connected as callback handlers
    any method whose name does not begin with an underscore ('_') is a  callback candidate

    the 'get_handlers' name is reserved - gladevcp expects it, so do not change
    '''
    return [HandlerClass(halcomp,builder,useropts)]
