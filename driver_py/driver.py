import os
import dynamixel
import sys
import subprocess
import optparse
import yaml

import socket
import json
import time


def main(settings):

	SERVER_IP = '78.91.5.36'
	SERVER_PORT = 9001
	SERVVER_CONN = (SERVER_IP, SERVER_PORT)

	# Establish a serial connection to the dynamixel network.
	# This usually requires a USB2Dynamixel
	serial = dynamixel.SerialStream(port=settings['port'],
									baudrate=settings['baudRate'],
									timeout=1)
	# Instantiate our network object
	net = dynamixel.DynamixelNetwork(serial)

	# Populate our network with dynamixel objects
	for servoId in settings['servoIds']:
		newDynamixel = dynamixel.Dynamixel(servoId, net)
		net._dynamixel_map[servoId] = newDynamixel
	
	if not net.get_dynamixels():
		print 'No Dynamixels Found!'
		sys.exit(0)
	else:
		print "...Done"

	try:
		clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		clientsocket.connect(SERVVER_CONN)
		clientsocket.send("Connection established!")
	except:
		print("Failed to connect to remote server")

	for actuator in net.get_dynamixels():
		actuator._set_to_wheel_mode()
		actuator.moving_speed = 1024
		actuator.torque_enable = False
		actuator.torque_limit = 900
		actuator.max_torque = 900
		actuator.goal_position = 512
		
	net.synchronize()

	#Main loop
	while True:
		json_data = clientsocket.recv(4096)
		if len(json_data) > 0:
			try:
				data = json.loads(json_data)

				if data["action"] == "info":
					objects = data["objects"]
					return_status = {}
					for dynamo in objects:
						return_status[dynamo["id"]] = net[int(dynamo["id"])]._return_json_status()
					clientsocket.send(json.dumps(return_status))
				elif data["action"] == "move":
					objects = data["objects"]
					for dynamo in objects:
						print str(dynamo["id"]) + " - " + str(dynamo["speed"])
						net[int(dynamo["id"])].moving_speed = int(dynamo["speed"])
						net.synchronize()
					clientsocket.send("Success")
				else:
					clientsocket.send("Error: Wrong protocol format!")

			except ValueError:
				print "Unable to parse json on string: " + json_data
				clientsocket.send("A valueerror occured!!!")


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