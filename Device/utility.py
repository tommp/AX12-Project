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

class Car_configuration:
	def __init__(self, left_actuator_cluster, right_actuator_cluster, net):
		self.right_actuator_cluster = right_actuator_cluster
		self.left_actuator_cluster = left_actuator_cluster
		self.speed_scale = 8
		self.net = net

	def reset_speed(self):
		for actuator_id in self.left_actuator_cluster:
			self.net[actuator_id].moving_speed = 0

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
			self.net[actuator_id].moving_speed += (self.speed_scale*setspeed)
			if self.net[actuator_id].moving_speed > 2048:
				self.net[actuator_id].moving_speed = 2048

		for actuator_id in self.right_actuator_cluster:
			self.net[actuator_id].moving_speed += (self.speed_scale*setspeed)
			if self.net[actuator_id].moving_speed > 2048:
				self.net[actuator_id].moving_speed = 2048


	def add_move_backward(self, speed):
		if speed > 100:
			setspeed = 100
		elif speed < 0:
			setspeed = 0
		else:
			setspeed = speed

		for actuator_id in self.left_actuator_cluster:
			self.net[actuator_id].moving_speed += (1024 + self.speed_scale*setspeed)
			if self.net[actuator_id].moving_speed > 2048:
				self.net[actuator_id].moving_speed = 2048

		for actuator_id in self.right_actuator_cluster:
			self.net[actuator_id].moving_speed -= (1000 - self.speed_scale*setspeed) 
			if self.net[actuator_id].moving_speed < 0:
				self.net[actuator_id].moving_speed = 0

	def add_turn_left(self, turn):
		if turn > 100:
			setturn = 100
		elif turn < 0:
			setturn = 0
		else:
			setturn = turn

		#TODO::TAKE CARE OF SPECIAL CASES TO WORK PROPERLY
		for actuator_id in self.left_actuator_cluster:
			self.net[actuator_id].moving_speed -= (10 - self.speed_scale)*setturn
			if self.net[actuator_id].moving_speed < 0:
				self.net[actuator_id].moving_speed = 0

		for actuator_id in self.right_actuator_cluster:
			self.net[actuator_id].moving_speed += (10 - self.speed_scale)*setturn
			if self.net[actuator_id].moving_speed > 2048:
				self.net[actuator_id].moving_speed = 2048

	def add_turn_right(self, turn):
		if turn > 100:
			setturn = 100
		elif turn < 0:
			setturn = 0
		else:
			setturn = turn

		for actuator_id in self.left_actuator_cluster:
			self.net[actuator_id].moving_speed += (10 - self.speed_scale)*setturn
			if self.net[actuator_id].moving_speed > 2048:
				self.net[actuator_id].moving_speed = 2048

		for actuator_id in self.right_actuator_cluster:
			self.net[actuator_id].moving_speed -= (10 - self.speed_scale)*setturn
			if self.net[actuator_id].moving_speed < 1024:
				self.net[actuator_id].moving_speed = 1024
		

#TODO::RENAME TO LOG
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
		try:
			self.name = settings['name']
		except:
			self.name = "RULS_DEFAULT"
		self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.connected = False
		self.configurations = {}
		self.configuration_ids = []

		# Establish a serial connection to the dynamixel network.
		# This usually requires a USB2Dynamixel
		try:
			self.serial = dynamixel.SerialStream(port=settings['port'],
											baudrate=settings['baudRate'],
											timeout=1)
		except:
			errorlog.write("ERROR: No Dynamixels Found!\n")
			printdt("No Dynamixels Found!")
			device_controller.restart_program()

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
			device_controller.restart_program()
		else:
			printdt("Dynamixels found, network initialized")

		for actuator in self.net.get_dynamixels():
			actuator._set_to_wheel_mode()
			actuator.moving_speed = 1024
			actuator.torque_enable = False
			actuator.torque_limit = 1023
			actuator.max_torque = 1023
			actuator.goal_position = 512
			
		self.net.synchronize()

	def check_if_ids_in_network(self, servo_ids):
		invalid_servos = []
		net_ids = []

		for actuator in self.net.get_dynamixels():
			net_ids.append(actuator.id)

		for servo in servo_ids:
			if servo not in net_ids:
				invalid_servos.append(servo)
				printdt("ERROR: Requested id not in dynamixel network: " + str(servo))
				errorlog.write("ERROR: Requested id not in dynamixel network: " + str(servo))

		return invalid_servos

	def set_angle_limits(self, servos):
		servo_ids = []

		for servo in servos:
			servo_ids.append(servo["id"])

		invalid_servos = self.check_if_ids_in_network(servo_ids)

		if not invalid_servos:
			for servo in servos:
				self.net[servo["id"]].ccw_angle_limit = servo["counterclockwise"]
				self.net[servo["id"]].cw_angle_limit = servo["clockwise"]
				printdt("Set ccw limit to: " + str(servo["counterclockwise"]) + 
									", set cw limit to: " + str(servo["clockwise"]) + ", for servo: " + 
									str(servo["id"]))
			device_controller.send_reply_message("success",  "Angle limits set!")
			printdt("Angle limits set!")
		else:
			status_string = "Requested id(s) not in dynamixel network: "
			for invalid_servo in invalid_servos:
				status_string += str(invalid_servo) + ", "
			printdt(status_string)
			device_controller.send_reply_message("error",  status_string)


	def send_ids(self):
		return_status = {}
		return_status["name"] = self.name
		return_status["ids"] = []
		for actuator in self.net.get_dynamixels():
			return_status["ids"].append(actuator.id)
		self.clientsocket.send(json.dumps(return_status))

	def create_car_configuration(self, errorlog, conf_id, servo_ids):
		right_actuator_cluster = []
		left_actuator_cluster = []

		self.configuration_ids.append(conf_id)

		printdt("Creating car configuration with id: " + str(conf_id) + "...")

		invalid_servos = self.check_if_ids_in_network(servo_ids)

		if invalid_servos:
			status_string = "Requested id(s) not in dynamixel network: "
			for invalid_servo in invalid_servos:
				status_string += str(invalid_servo) + ", "
			printdt(status_string)
			device_controller.send_reply_message("Error",  status_string)
			return -1;
		else:
			printdt("Servos initialized")

		#CW for forward
		for i in range(len(servo_ids)/2):
			right_actuator_cluster.append(servo_ids[i])

		#CCW for forward
		for i in range(len(servo_ids)/2, len(servo_ids)):
			left_actuator_cluster.append(servo_ids[i])

		printdt("Success: Created car configuration with id: " + str(conf_id))

		self.configurations[conf_id] = Car_configuration(left_actuator_cluster, right_actuator_cluster, self.net)

	def move_configuration(self, speed, turn, conf_id):
		self.configurations[conf_id].reset_speed()
		if(speed > 0):
			self.configurations[conf_id].add_move_forward(speed)
		elif(speed < 0):
			self.configurations[conf_id].add_move_backward(abs(speed))

		if(turn > 0):
			self.configurations[conf_id].add_turn_right(turn)
		elif (turn < 0):
			self.configurations[conf_id].add_turn_left(abs(turn))

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
				self.clientsocket.settimeout(5)
				try:
					printdt("Attempting to connect to remote...")
					self.clientsocket.connect(server_conn)
					self.clientsocket.send(json.dumps(self.return_name_packet()))
					self.connected = True
				except:
					errorlog.write("ERROR: Failed to connect to remote server, retrying")
					printdt("ERROR: Failed to connect to remote server, retrying")
				time.sleep(conn_attempt_delay)
		else:
			for i in range(num_conn_attempts):
				self.clientsocket.settimeout(5)
				try:
					printdt("Attempting to connect to remote...")
					self.clientsocket.connect(server_conn)
					self.clientsocket.send(json.dumps(self.return_name_packet()))
					self.connected = True
					printdt("Connected!")
					break;
				except:
					errorlog.write("ERROR: Failed to connect to remote server, retrying")
					printdt("ERROR: Failed to connect to remote server, retrying")
				time.sleep(conn_attempt_delay)
		self.clientsocket.settimeout(None)

	def send_reply_message(self, status, message):
		status_packet={}
		status_packet["status"] = status
		status_packet["message"] = message
		self.clientsocket.send(json.dumps(status_packet))

def printdt(string):
		print ("Date: " + time.strftime("%d/%m/%Y") + 
			"\nTime: " + time.strftime("%H:%M:%S") + 
			"\n" + string + "\n")