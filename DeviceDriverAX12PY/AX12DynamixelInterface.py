import os
import dynamixel
import sys
import subprocess
import optparse
import yaml
import socket
import json
import time
from utility import ErrorLogger, DeviceController, printdt
from random import randint


def main(settings):

	#SERVER_IP = 'vsop.online.ntnu.no'
	SERVER_IP = '78.91.5.62'
	SERVER_PORT = 9001
	SERVER_CONN = (SERVER_IP, SERVER_PORT)

	#-1 for infinite
	NUMBER_OF_CONNECTION_ATTEMPTS = -1
	#In seconds
	DELAY_BETWEEN_ATTEMPTS = 1

	# Create a errorlogger
	errorlog = ErrorLogger("errorlog.txt")

	# Create a device controller
	device_controller = DeviceController(settings, errorlog)

	# Establish server connection
	device_controller.establish_connection(errorlog, SERVER_CONN, NUMBER_OF_CONNECTION_ATTEMPTS, DELAY_BETWEEN_ATTEMPTS)

	if (not device_controller.connected):
		errorlog.write("FATAL ERROR: Failed to connect to remote server")
		printdt("FATAL ERROR: Failed to connect to server, check network settings and upstream connection then restart")
	else:
		printdt("Successfully connected to remote server")


	#MAIN LOOP START##############################################################################################
	############################################################################################################
	while True:
		#Checks if the connection was established, if not allows manual mode locally
		if device_controller.connected:
			#Reads data from socket
			try:
				json_data = device_controller.clientsocket.recv(4096)
			except:
				errorlog.write("ERROR: Server socket connection failed")
				printdt("Error, server socket connection failed")
				device_controller.restart_program()
			if len(json_data) > 0:
				try:
					#Loads the data into a (json)dict
					data = json.loads(json_data)
					
					if data["action"] == "info":
						objects = data["actuators"]
						return_status = {}
						return_status["name"] = device_controller.name
						for dynamo in objects:
							return_status[dynamo["id"]] = device_controller.net[int(dynamo["id"])]._return_json_status()
						printdt("Sending info packets..")
						device_controller.clientsocket.send(json.dumps(return_status))
						printdt("Info packets sent!")
					elif data["action"] == "moveCar":
						status_string = "Speed set to: " + str(data["speed"]) + ", Direction set to: " + str(data["direction"])
						device_controller.move_configuration(int(data["speed"]), int(data["direction"]), int(data["id"]))
						device_controller.send_reply_message("Success", status_string)
						printdt(status_string)
					elif data["action"] == "createCar":
						#TODO:::::SMARTER WAY FOR THIS, INCREMENT AND ADD
						car_id = randint(0,1000)
						while(car_id in device_controller.configuration_ids):
							car_id = randint(0,5000)
						device_controller.create_car_configuration(car_id, data["actuators"].sort())
						device_controller.send_reply_message("Success", car_id)
						printdt("Created car object with id: " + str(car_id))
					elif data["action"] == "shutdown":
						printdt("Recieved quit command, shutting down!")
						errorlog.close_log()
						sys.exit()
					else:
						errorlog.write("ERROR: Wrong protocol format")
						printdt("Error, wrong protocol format")
						device_controller.send_reply_message("ERROR","Wrong protocol format!")
				#Handles potential valuerrors in the socket data
				except ValueError:
					try:
						device_controller.send_reply_message("VALUE ERROR","Unable to parse json on string: " + 
							json_data)
						errorlog.write("VALUE ERROR: Unable to parse json on string: " + 
							json_data)
						printdt("Unable to parse json on string, assuming text message, data: " + json_data)
					except:
						device_controller.send_reply_message("VALUE ERROR", "Recieved data was corrupt")
						errorlog.write("VALUE ERROR: Recieved data was corrupt")
						printdt("Recieved data was corrupt!")
		#Manual menu
		else:
			while(True):
				data = raw_input("Type command (help for options): ")
				if data in ['r', 'R', 'restart', 'reset']:
					printdt("Recieved reset command, restarting now!")
					errorlog.close_log()
					device_controller.restart_program()
				elif data in ['q', 'Q', 'quit', 'QUIT']:
					printdt("Recieved quit command, shutting down!")
					errorlog.close_log()
					sys.exit()
				elif data in ['rcw']:
					printdt("Recieved run command (clockwise), starting servos!")
					for dynamo in device_controller.net.get_dynamixels():
						dynamo.moving_speed = 1500
						device_controller.net.synchronize()
				elif data in ['rccw']:
					printdt("Recieved run command (counterclockwise), starting servos!")
					for dynamo in device_controller.net.get_dynamixels():
						dynamo.moving_speed = 500
						device_controller.net.synchronize()
				elif data in ['s']:
					printdt("Recieved stop command, stopping servos!")
					for dynamo in device_controller.net.get_dynamixels():
						dynamo.moving_speed = 1024
						device_controller.net.synchronize()
				elif data in ["help"]:
					print("Commands: r = Restart, q = Shutdown, rcw = Run clockwise, rccw = Run counterclockwise, s = Stop\n")
				else:
					continue
	#MAIN LOOP END##############################################################################################
	############################################################################################################


def validateInput(userInput, rangeMin, rangeMax):
	'''
	Returns valid user input or None
	'''
	try:
		inTest = int(userInput)
		if inTest < rangeMin or inTest > rangeMax:
			print "ERROR: Value out of range [" + str(rangeMin) + '-' + str(rangeMax) + "]"
			return None
	except ValueError:
		print("ERROR: Please enter an integer")
		return None
	
	return inTest

if __name__ == '__main__':
	
	parser = optparse.OptionParser()
	parser.add_option("-c", "--clean",
					  action="store_true", dest="clean", default=False,
					  help="Ignore the settings.yaml file if it exists and \
					  prompt for new settings.")
	
	(options, args) = parser.parse_args()
	
	# Look for a settings.yaml file
	settingsFile = 'settings.yaml'
	if not options.clean and os.path.exists(settingsFile):
		with open(settingsFile, 'r') as fh:
			settings = yaml.load(fh)
	# If we were asked to bypass, or don't have settings
	else:
		settings = {}
		if os.name == "posix":
			portPrompt = "Which port corresponds to your USB2Dynamixel? \n"
			# Get a list of ports that mention USB
			try:
				possiblePorts = subprocess.check_output('ls /dev/ | grep -i usb',
														shell=True).split()
				possiblePorts = ['/dev/' + port for port in possiblePorts]
			except subprocess.CalledProcessError:
				sys.exit("USB2Dynamixel not found. Please connect one.")
				
			counter = 1
			portCount = len(possiblePorts)
			for port in possiblePorts:
				portPrompt += "\t" + str(counter) + " - " + port + "\n"
				counter += 1
			portPrompt += "Enter Choice: "
			portChoice = None
			while not portChoice:                
				portTest = raw_input(portPrompt)
				portTest = validateInput(portTest, 1, portCount)
				if portTest:
					portChoice = possiblePorts[portTest - 1]

		else:
			portPrompt = "Please enter the port name to which the USB2Dynamixel is connected: "
			portChoice = raw_input(portPrompt)
	
		settings['port'] = portChoice

		# Device name
		deviceName = ""
		while not deviceName:
			dnTest = raw_input("Enter device name, must be unique on the server: ")
			if dnTest.isalpha():
				deviceName = dnTest
			else:
				print("ERROR: Name must be only letters, no numbers or special characters")

		settings['name'] = deviceName

		# Baud rate
		baudRate = None
		while not baudRate:
			brTest = raw_input("Enter baud rate [Default: 1000000 bps]:")
			if not brTest:
				baudRate = 1000000
			else:
				baudRate = validateInput(brTest, 9600, 1000000)
					
		settings['baudRate'] = baudRate
		
		# Servo ID
		highestServoId = None
		while not highestServoId:
			hsiTest = raw_input("Please enter the highest ID of the connected servos: ")
			highestServoId = validateInput(hsiTest, 1, 255)
		
		settings['highestServoId'] = highestServoId


		highestServoId = settings['highestServoId']

		# Establish a serial connection to the dynamixel network.
		# This usually requires a USB2Dynamixel
		serial = dynamixel.SerialStream(port=settings['port'],
										baudrate=settings['baudRate'],
										timeout=1)
		# Instantiate our network object
		net = dynamixel.DynamixelNetwork(serial)
		
		# Ping the range of servos that are attached
		print "Scanning for Dynamixels..."
		net.scan(1, highestServoId)

		settings['servoIds'] = []
		print "Found the following Dynamixels IDs: "
		for dyn in net.get_dynamixels():
			print dyn.id
			settings['servoIds'].append(dyn.id)

		# Make sure we actually found servos
		if not settings['servoIds']:
		  print 'No Dynamixels Found!'
		  sys.exit(0)

		# Save the output settings to a yaml file
		with open(settingsFile, 'w') as fh:
			yaml.dump(settings, fh)
			print("Your settings have been saved to 'settings.yaml'. \nTo " +
				   "change them in the future either edit that file or run " +
				   "this example with -c.")
	
	main(settings)