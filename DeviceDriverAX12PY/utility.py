#!/usr/bin/env python2.6
import sys
import os
import time
import json
import socket

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
			self.errorlog.write("Date: " + time.strftime("%d/%m/%Y") + 
			"\nTime: " + time.strftime("%H:%M:%S") + 
			"\n" + string + "\n" + "\n")
		else:
			return 0
	def close_log(self):
		if self.errorlog:
			self.errorlog.close()

	

class DeviceController:
	def __init__(self, name):
		self.name = name
		self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.connected = True

	def restart_program(self):
		python = sys.executable
		os.execl(python, python, * sys.argv)

	def return_name_packet(self):
		name_packet={}
		name_packet["name"] = self.name
		return name_packet

	def printdt(self, string):
		print ("Date: " + time.strftime("%d/%m/%Y") + 
			"\nTime: " + time.strftime("%H:%M:%S") + 
			"\n" + string + "\n")

	def establish_connection(self,errorlog, server_conn, num_conn_attempts, conn_attempt_delay):
		if num_conn_attempts <= 0:
			while (not self.connected):
				try:
					self.clientsocket.connect(server_conn)
					self.clientsocket.send(json.dumps(self.return_name_packet()))
					self.connected = True
				except:
					errorlog.write("ERROR: Failed to connect to remote server, retrying")
					self.printdt("ERROR: Failed to connect to remote server, retrying")
				time.sleep(conn_attempt_delay)
		else:
			for i in range(num_conn_attempts):
				try:
					self.clientsocket.connect(server_conn)
					self.clientsocket.send(json.dumps(self.return_name_packet()))
					self.connected = True
					break;
				except:
					errorlog.write("ERROR: Failed to connect to remote server, retrying")
					self.printdt("ERROR: Failed to connect to remote server, retrying")
				time.sleep(conn_attempt_delay)

