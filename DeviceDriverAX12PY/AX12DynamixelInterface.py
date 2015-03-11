import os
import dynamixel
import sys
import subprocess
import optparse
import yaml
import socket
import json
import time
from utility import ErrorLogger, DeviceController

def main(settings):

	SERVER_IP = 'vsop.online.ntnu.no'
	#SERVER_IP = '78.91.7.89'
	SERVER_PORT = 9001
	SERVER_CONN = (SERVER_IP, SERVER_PORT)

	#Name of the device, must be unique on the server
	DEVICE_NAME = "Ruls"

	#-1 for infinite
	NUMBER_OF_CONNECTION_ATTEMPTS = 10
	#In seconds
	DELAY_BETWEEN_ATTEMPTS = 1

	# Establish a serial connection to the dynamixel network.
	# This usually requires a USB2Dynamixel
	serial = dynamixel.SerialStream(port=settings['port'],
									baudrate=settings['baudRate'],
									timeout=1)
	# Instantiate our network object
	net = dynamixel.DynamixelNetwork(serial)

	# Create a errorlogger
	errorlog = ErrorLogger("Errorlog.txt")
	device_controller = DeviceController(DEVICE_NAME)

	# Populate our network with dynamixel objects
	for servoId in settings['servoIds']:
		newDynamixel = dynamixel.Dynamixel(servoId, net)
		net._dynamixel_map[servoId] = newDynamixel
	
	# Get all the dynamixels in the network
	if not net.get_dynamixels():
		errorlog.write("ERROR: No Dynamixels Found!\n")
		device_controller.printdt("No Dynamixels Found!")
		sys.exit(0)
	else:
		device_controller.printdt("Dynamixels found, network initialized")

	# Establish server connection##############################################################################
	device_controller.establish_connection(errorlog, SERVER_CONN, NUMBER_OF_CONNECTION_ATTEMPTS, DELAY_BETWEEN_ATTEMPTS)

	if (not device_controller.connected):
		errorlog.write("FATAL ERROR: Failed to connect to remote server")
		device_controller.printdt("FATAL ERROR: Failed to connect to server, check network settings and upstream connection then restart")
	else:
		device_controller.printdt("Successfully connected to remote server")
	############################################################################################################

	for actuator in net.get_dynamixels():
		actuator._set_to_wheel_mode()
		actuator.moving_speed = 1024
		actuator.torque_enable = False
		actuator.torque_limit = 900
		actuator.max_torque = 900
		actuator.goal_position = 512
		
	net.synchronize()

	#MAIN LOOP START##############################################################################################
	############################################################################################################
	while True:
		#CHecks if the connection was established, if not allows manual mode locally
		if device_controller.connected:
			#Reads data from socket
			json_data = device_controller.clientsocket.recv(4096)
			if len(json_data) > 0:
				try:
					#Loads the data into a (json)dict
					data = json.loads(json_data)
					
					if data["action"] == "info":
						objects = data["actuators"]
						return_status = {}
						return_status["name"] = device_controller.name
						for dynamo in objects:
							return_status[dynamo["id"]] = net[int(dynamo["id"])]._return_json_status()
						device_controller.printdt("Sending info packets")
						device_controller.clientsocket.send(json.dumps(return_status))
					elif data["action"] == "move":
						objects = data["actuators"]
						for dynamo in objects:
							if str(dynamo["direction"]) in ["ccw", "counterclockwise", "CCW", "Couterclockwise"]:
								new_speed = int(dynamo["speed"])*10
								if new_speed > 1000:
									new_speed = 1000
								elif new_speed < 0:
									new_speed = 0
							elif str(dynamo["direction"]) in ["cw", "clockwise", "CW", "Clockwise"]:					
								new_speed = int(dynamo["speed"])*10 + 1000
								if new_speed > 2000:
									new_speed = 2000
								elif new_speed < 1024:
									new_speed = 1024

							device_controller.printdt(str(dynamo["id"]) + " - " + str(dynamo["speed"]))
							#Set dynamixel register data to send
							net[int(dynamo["id"])].moving_speed = new_speed
							#Send data to dynamixels
							net.synchronize()
						device_controller.clientsocket.send("Success")
					else:
						errorlog.write("ERROR: Wrong protocol format")
						device_controller.printdt("Error, wrong protocol format")
						device_controller.clientsocket.send("Error: Wrong protocol format!")
				#Handles potential valuerrors in the socket data
				except ValueError:
					try:
						errorlog.write("VALUE ERROR: Unable to parse json on string: " + 
							json_data)
						device_controller.printdt("Unable to parse json on string, assuming text message, data: " + json_data)
					except:
						errorlog.write("VALUE ERROR: recieved data was corrupt")
						device_controller.printdt("Recieved data was corrupt!")

					device_controller.clientsocket.send("A valueerror occured!!!")
		#Manual menu
		else:
			data = raw_input("Type command (help for options): ")
			if data in ['r', 'R', 'restart', 'reset']:
				device_controller.printdt("Recieved reset command, restarting now!")
				errorlog.close_log()
				device_controller.restart_program()
			elif data in ['q', 'Q', 'quit', 'QUIT']:
				device_controller.printdt("Recieved quit command, shutting down!")
				errorlog.close_log()
				sys.exit()
			elif data in ['rcw']:
				device_controller.printdt("Recieved run command (clockwise), starting servos!")
				for dynamo in net.get_dynamixels():
					dynamo.moving_speed = 1500
					net.synchronize()
			elif data in ['rccw']:
				device_controller.printdt("Recieved run command (counterclockwise), starting servos!")
				for dynamo in net.get_dynamixels():
					dynamo.moving_speed = 500
					net.synchronize()
			elif data in ['s']:
				device_controller.printdt("Recieved stop command, stopping servos!")
				for dynamo in net.get_dynamixels():
					dynamo.moving_speed = 1024
					net.synchronize()
			elif data in ["help"]:
				print("Commands: r = Restart, q = Shutdown, rcw = Run clockwise, rccw = Run counterclockwise, s = Stop\n")

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