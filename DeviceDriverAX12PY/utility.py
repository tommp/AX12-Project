#!/usr/bin/env python2.6
import os
import dynamixel
import sys
import subprocess
import optparse
import yaml
import socket
import json
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
			self.errorlog.write("Date: " + time.strftime("%d/%m/%Y") + 
			"\nTime: " + time.strftime("%H:%M:%S") + 
			"\n" + string + "\n" + "\n")
		else:
			return 0
	def close_log(self):
		if self.errorlog:
			self.errorlog.close()

	

class DeviceController:
	def __init__(self, settings, errorlog):
		self.name = settings['name']
		self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.connected = True
		self.right_actuator_cluster = []
		self.left_actuator_cluster = []
		self.speed_scale = 6


		#CW for forward
		for i in range((settings['servoIds'].size())/2):
			self.right_actuator_cluster.append(settings['servoIds'][i])

		#CCW for forward
		for i in range((settings['servoIds'].size())/2, settings['servoIds'].size()):
			self.left_actuator_cluster.append(settings['servoIds'][i])

		# Establish a serial connection to the dynamixel network.
		# This usually requires a USB2Dynamixel
		self.serial = dynamixel.SerialStream(port=settings['port'],
										baudrate=settings['baudRate'],
										timeout=1)
		# Instantiate our network object
		self.net = dynamixel.DynamixelNetwork(self.serial)

		# Populate our network with dynamixel objects
		for servoId in settings['servoIds']:
			newDynamixel = dynamixel.Dynamixel(servoId, self.net)
			self.net._dynamixel_map[servoId] = newDynamixel
		
		# Get all the dynamixels in the network
		if not self.net.get_dynamixels():
			errorlog.write("ERROR: No Dynamixels Found!\n")
			printdt("No Dynamixels Found!")
			sys.exit(0)
		else:
			printdt("Dynamixels found, network initialized")

		for actuator in self.net.get_dynamixels():
			actuator._set_to_wheel_mode()
			actuator.moving_speed = 1024
			actuator.torque_enable = False
			actuator.torque_limit = 900
			actuator.max_torque = 900
			actuator.goal_position = 512
			
		self.net.synchronize()

	def reset_speed(self):
		for actuator_id in self.left_actuator_cluster:
			self.net[actuator_id].moving_speed = 1024

		for actuator_id in self.right_actuator_cluster:
			self.net[actuator_id].moving_speed = 1024

	def add_move_forward(self, speed):
		if speed > 100:
			setspeed = 100
		elif speed < 0:
			setspeed = 0
		else:
			setspeed = speed

		for actuator_id in self.left_actuator_cluster:
			self.net[actuator_id].moving_speed -= (1000 - self.speed_scale*speed)

		for actuator_id in self.right_actuator_cluster:
			self.net[actuator_id].moving_speed += self.speed_scale*speed


	def add_move_backward(self, speed):
		if speed > 100:
			setspeed = 100
		elif speed < 0:
			setspeed = 0
		else:
			setspeed = speed

		for actuator_id in self.left_actuator_cluster:
			self.net[actuator_id].moving_speed += self.speed_scale*speed

		for actuator_id in self.right_actuator_cluster:
			self.net[actuator_id].moving_speed -= (1000 - self.speed_scale*speed) 

	#THIS IS LOL; FIX IT
	def add_turn_left(self, turn):
		if speed > 100:
			setspeed = 100
		elif speed < 0:
			setspeed = 0
		else:
			setspeed = speed

		for actuator_id in self.left_actuator_cluster:
			self.net[actuator_id].moving_speed += (10 - self.speed_scale)*speed

		for actuator_id in self.right_actuator_cluster:
			self.net[actuator_id].moving_speed += (10 - self.speed_scale)*speed

	#THIS IS LOL; FIX IT
	def add_turn_right(self, turn):
		if speed > 100:
			setspeed = 100
		elif speed < 0:
			setspeed = 0
		else:
			setspeed = speed

		for actuator_id in self.left_actuator_cluster:
			self.net[actuator_id].moving_speed -= (10 - self.speed_scale)*speed

		for actuator_id in self.right_actuator_cluster:
			self.net[actuator_id].moving_speed -= (10 - self.speed_scale)*speed

	def move(speed, turn):
		self.net.synchronize()

	def restart_program(self):
		python = sys.executable
		os.execl(python, python, * sys.argv)

	def return_name_packet(self):
		name_packet={}
		name_packet["name"] = self.name
		return name_packet

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

def printdt(string):
		print ("Date: " + time.strftime("%d/%m/%Y") + 
			"\nTime: " + time.strftime("%H:%M:%S") + 
			"\n" + string + "\n")