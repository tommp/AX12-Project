import os
import dynamixel
import sys
import subprocess
import optparse
import yaml

import socket
import threading


def main(settings):

	SERVER_IP = '78.91.7.139'
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
		clientsocket.bind(SERVVER_CONN)
		clientsocket.send("Dynamixel controller connected!")

		try:
			remote_controller = threading.Thread(None, remote_handler)
			remote_controller.daemon = True
			remote_controller.start()
		except:
			print("Failed to initialize remote_controller")
	except:
		print("Failed to connect to remote server")

	for actuator in net.get_dynamixels():
		actuator.cw_angle_limit = 0
		actuator.ccw_angle_limit = 0
		actuator.moving_speed = 1024
		actuator.torque_enable = True
		actuator.torque_limit = 800 
		actuator.max_torque = 800

	net.synchronize()

	command_lock = threading.Semaphore()

	#Main loop
	while True:
		command = raw_input("Type command: ")

		command_lock.acquire()
		process_command(command)
		command_lock.release()

def remote_handler():
	while True:
		command = clientsocket.recv(64)

		command_lock.acquire()
		process_command_remote(command)
		command_lock.release()

def process_command(command):
	if command in ['r', 'R', 'run', 'RUN']:
		for actuator in net.get_dynamixels():
			actuator.moving_speed = 500
	elif command in ['s', 'S', 'stop', 'STOP']:
		for actuator in net.get_dynamixels():
			actuator.moving_speed = 1024
	elif command in ['q', 'Q', 'quit', 'QUIT']:
		for actuator in net.get_dynamixels():
			print("Recieved local quit command, shutting down local and remote connection!")
			try:
				clientsocket.send("Recieved local quit command, shutting down local and remote connection!")
				clientsocket.close()
			except:
				print("Could not close remote connections")
			actuator.moving_speed = 1024
			net.synchronize()
			exit(0)
	net.synchronize()

def process_command_remote(command):
	if command in ['r', 'R', 'run', 'RUN']:
		for actuator in net.get_dynamixels():
			actuator.moving_speed = 500
	elif command in ['s', 'S', 'stop', 'STOP']:
		for actuator in net.get_dynamixels():
			actuator.moving_speed = 1024
	elif command in ['q', 'Q', 'quit', 'QUIT']:
		for actuator in net.get_dynamixels():
			clientsocket.send("Recieved quit command, shutting down remote connection!")
			clientsocket.close()
			exit(0)
	net.synchronize()


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