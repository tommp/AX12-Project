#!/usr/bin/env python2.6
import sys
import os
import time

class ErrorLogger:
	def __init__(self, logfile):
		try:
			self.errorlog = open(logfile, 'a')
			print("Date: " + time.strftime("%d/%m/%Y") + 
				"\nTime: " + time.strftime("%H:%M:%S") + 
				"\nErrorlog initialized\n")
		except:
			print("Date: " + time.strftime("%d/%m/%Y") + 
				"\nTime: " + time.strftime("%H:%M:%S") + 
				"\nFailed to open errorlog!\n")
			self.errorlog = 0

	def write(self, string):
		if self.errorlog:
			self.errorlog.write(string)
		else:
			return 0

	

class DeviceController:
	def __init__(self, name):
		self.name = name

	def restart_program(self):
		python = sys.executable
		os.execl(python, python, * sys.argv)

	def return_name_packet(self):
		name_packet={}
		name_packet["name"] = {self.name}
		return name_packet

