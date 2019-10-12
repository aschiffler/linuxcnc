import glib
import time
import gobject

import hal
import linuxcnc

import pandas as pd
import numpy as np
from sklearn.externals import joblib
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import ExtraTreesClassifier

class HandlerClass:
	def __init__(self, halcomp,builder,useropts):
		self.halcomp = halcomp
		self.halcomp.newpin("logger_beat", hal.HAL_BIT, hal.HAL_OUT)
		self.halcomp.newpin("ai_label", hal.HAL_FLOAT, hal.HAL_OUT)
		self.halcomp.newpin("logger_11", hal.HAL_FLOAT, hal.HAL_IN)
		self.halcomp.newpin("logger_12", hal.HAL_FLOAT, hal.HAL_IN)
		self.halcomp.newpin("logger_13", hal.HAL_FLOAT, hal.HAL_IN)
		self.halcomp.newpin("logger_21", hal.HAL_FLOAT, hal.HAL_IN)
		self.halcomp.newpin("logger_22", hal.HAL_FLOAT, hal.HAL_IN)
		self.halcomp.newpin("logger_23", hal.HAL_FLOAT, hal.HAL_IN)
		self.halcomp.newpin("logger_31", hal.HAL_FLOAT, hal.HAL_IN)
		self.halcomp.newpin("logger_32", hal.HAL_FLOAT, hal.HAL_IN)
		self.halcomp.newpin("logger_33", hal.HAL_FLOAT, hal.HAL_IN)
		self.halcomp.newpin("logger_41", hal.HAL_FLOAT, hal.HAL_IN)
		self.halcomp.newpin("logger_42", hal.HAL_FLOAT, hal.HAL_IN)
		self.halcomp.newpin("logger_43", hal.HAL_FLOAT, hal.HAL_IN)
		self.halcomp.newpin("logger_51", hal.HAL_FLOAT, hal.HAL_IN)
		self.halcomp.newpin("logger_52", hal.HAL_FLOAT, hal.HAL_IN)
		self.halcomp.newpin("logger_53", hal.HAL_FLOAT, hal.HAL_IN)
		self.halcomp.newpin("logger_61", hal.HAL_FLOAT, hal.HAL_IN)
		self.halcomp.newpin("logger_62", hal.HAL_FLOAT, hal.HAL_IN)
		self.halcomp.newpin("logger_63", hal.HAL_FLOAT, hal.HAL_IN)
		self.halcomp.newpin("logger_71", hal.HAL_FLOAT, hal.HAL_IN)
		self.halcomp.newpin("logger_72", hal.HAL_FLOAT, hal.HAL_IN)
		self.halcomp.newpin("logger_73", hal.HAL_FLOAT, hal.HAL_IN)
		self.halcomp.newpin("logger_81", hal.HAL_FLOAT, hal.HAL_IN)
		self.halcomp.newpin("logger_82", hal.HAL_FLOAT, hal.HAL_IN)
		self.halcomp.newpin("logger_83", hal.HAL_FLOAT, hal.HAL_IN)
		self.halcomp.newpin("start_stop", hal.HAL_BIT, hal.HAL_IN)
		self.halcomp.newpin("predict", hal.HAL_BIT, hal.HAL_IN)
		self.halcomp['logger_beat'] = False
	        self.builder = builder
	 	self.emc = linuxcnc
		self.status = self.emc.stat()
		self.statemachine = 1
		self.train_class = 1
		self.df = pd.DataFrame(index=range(600),columns=[
			'pos1','pos2','pos3',
			'c1_f1','c1_f2','c1_f3',
			'c2_f1','c2_f2','c2_f3',
			'c3_f1','c3_f2','c3_f3',
			'c4_f1','c4_f2','c4_f3',
			'c5_f1','c5_f2','c5_f3',
			'c6_f1','c6_f2','c6_f3',
			'c7_f1','c7_f2','c7_f3',
			'c8_f1','c8_f2','c8_f3'])
		self.y = pd.DataFrame(index=range(600),columns=['target'])
		self.data_cycle_start = 0
		self.data_cycle_stop = -1
	
		gobject.timeout_add(1000, self.periodic)

	def on_btn_new_clicked(self, obj, data=None):
		self.statemachine = 1
		print "new model"
		self.model = MLPClassifier(verbose='true',solver='adam',activation='logistic',
			alpha=1e-5,hidden_layer_sizes=(50,),random_state=1)
		print self.model
		return True

	def on_btn_new_rf_clicked(self, obj, data=None):
		self.statemachine = 1
		print "new model"
		self.model = ExtraTreesClassifier(n_estimators=500,random_state=0,criterion="entropy",bootstrap=False)
		print self.model
		return True

	def on_btn_load_clicked(self, obj, data=None):
		self.statemachine = 1
		filename = self.builder.get_object('filename_1').get_text()
		print "load model "  + filename
		self.model = joblib.load(filename)
		print self.model
		return True

	def on_btn_save_clicked(self, obj, data=None):
		self.statemachine = 1
		filename = self.builder.get_object('filename_2').get_text()
		print "save model "  + filename
		self.model = joblib.dump(self.model,filename)
		print self.model
		return True

	def on_btn_train_all_clicked(self, obj, data=None):
		self.statemachine = 4
		print "Training started"
		self.model.fit(
			self.df.loc[:self.data_cycle_stop],
			np.ravel(self.y.loc[:self.data_cycle_stop].astype('int')))
		self.statemachine = 1
		print "Training finished"
		return True

	def on_btn_train1_clicked(self, obj, data=None):
		self.statemachine = 1
		self.train_class = 1
		self.y.loc[self.data_cycle_start:self.data_cycle_stop] = self.train_class
		print self.y.loc[:self.data_cycle_stop]
		print "data labeled to " + "{:.2f}".format(self.train_class)
		return True

	def on_btn_train2_clicked(self, obj, data=None):
		self.statemachine = 1
		self.train_class = 2
		self.y.loc[self.data_cycle_start:self.data_cycle_stop] = self.train_class
		print self.y.loc[:self.data_cycle_stop]
		print "data labeled to " + "{:.2f}".format(self.train_class)
		return True

	def on_btn_train3_clicked(self, obj, data=None):
		self.statemachine = 1
		self.train_class = 3
		self.y.loc[self.data_cycle_start:self.data_cycle_stop] = self.train_class
		print self.y.loc[:self.data_cycle_stop]
		print "data labeled to " + "{:.2f}".format(self.train_class)
		return True

	def on_btn_train4_clicked(self, obj, data=None):
		self.statemachine = 1
		self.train_class = 4
		self.y.loc[self.data_cycle_start:self.data_cycle_stop] = self.train_class
		print self.y.loc[:self.data_cycle_stop]
		print "data labeled to " + "{:.2f}".format(self.train_class)
		return True


	def on_btn_predict_clicked(self, obj, data=None):
		self.statemachine = 3
		print "predict"
		return True

	def on_btn_start_collect_clicked(self, obj, data=None):
		self.statemachine = 2
		self.data_cycle_start = self.data_cycle_stop + 1 
		print "start_collect"
		return True

	def on_btn_stop_collect_clicked(self, obj, data=None):
		self.statemachine = 1
		print "stop_collect"
		print "start " + "{:.2f}".format(self.data_cycle_start)
		print "stop " + "{:.2f}".format(self.data_cycle_stop)
		print self.df.loc[:self.data_cycle_stop]
		return True

	def on_btn_reset_collect_clicked(self, obj, data=None):
		self.statemachine = 1
		self.data_cycle_start = 0
		self.data_cycle_stop = -1		
		print "reset_collect"
		return True
	
	def periodic(self):
		self.status.poll()
		self.halcomp['logger_beat'] = not self.halcomp['logger_beat']
		if self.statemachine == 1:
			self.halcomp['ai_label'] = 0
			if self.halcomp['start_stop']:
				self.on_btn_start_collect_clicked(self, 0)
			if self.halcomp['predict']:
				self.statemachine = 3
		if self.statemachine == 2: 
			if not self.halcomp['start_stop']:
				self.on_btn_stop_collect_clicked(self, 0)
			self.data_cycle_stop = self.data_cycle_stop + 1 
			self.df.loc[self.data_cycle_stop] = [
			self.status.actual_position[0],self.status.actual_position[1],self.status.actual_position[2],
			self.halcomp['logger_11'],self.halcomp['logger_12'],self.halcomp['logger_13'],
			self.halcomp['logger_21'],self.halcomp['logger_22'],self.halcomp['logger_23'],
			self.halcomp['logger_31'],self.halcomp['logger_32'],self.halcomp['logger_33'],
			self.halcomp['logger_41'],self.halcomp['logger_42'],self.halcomp['logger_43'],
			self.halcomp['logger_51'],self.halcomp['logger_52'],self.halcomp['logger_53'],
			self.halcomp['logger_61'],self.halcomp['logger_62'],self.halcomp['logger_63'],
			self.halcomp['logger_71'],self.halcomp['logger_72'],self.halcomp['logger_73'],
			self.halcomp['logger_81'],self.halcomp['logger_82'],self.halcomp['logger_83']]

		if self.statemachine == 3:
			if not self.halcomp['predict']:
				self.statemachine = 1
			data = [ [
			self.status.actual_position[0],self.status.actual_position[1],self.status.actual_position[2],
			self.halcomp['logger_11'],self.halcomp['logger_12'],self.halcomp['logger_13'],
			self.halcomp['logger_21'],self.halcomp['logger_22'],self.halcomp['logger_23'],
			self.halcomp['logger_31'],self.halcomp['logger_32'],self.halcomp['logger_33'],
			self.halcomp['logger_41'],self.halcomp['logger_42'],self.halcomp['logger_43'],
			self.halcomp['logger_51'],self.halcomp['logger_52'],self.halcomp['logger_53'],
			self.halcomp['logger_61'],self.halcomp['logger_62'],self.halcomp['logger_63'],
			self.halcomp['logger_71'],self.halcomp['logger_72'],self.halcomp['logger_73'],
			self.halcomp['logger_81'],self.halcomp['logger_82'],self.halcomp['logger_83']]]
			prediction = self.model.predict_proba(data)
			self.halcomp['ai_label'] = self.model.predict(data)[0]
			for i in range(1,prediction.shape[1]+1):
				self.builder.get_object('class'+'{:,d}'.format(i)).set_text("{:.2f}".format(prediction[0][i-1]))
				self.builder.get_object('class'+'{:,d}'.format(i)).set_fraction(prediction[0][i-1])
			
		if self. statemachine == 4:	
			print "training"

		return True		

def get_handlers(halcomp,builder,useropts):
   return [HandlerClass(halcomp,builder,useropts)]
